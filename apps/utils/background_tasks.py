"""
Background task management for running phylogeo computations asynchronously.

This module runs the heavy phylogeo pipeline using Redis Queue (RQ), while
tracking progress and ETA in each job's metadata.
"""

import io
import json
import os
import re
import sys
import tempfile
import time
import warnings
from pathlib import Path

import pandas as pd
from redis import Redis
from redis.exceptions import RedisError
from rq import Queue, get_current_job
from rq.exceptions import NoSuchJobError
from rq.job import Job

import db.controllers.results as results_ctrl
import utils.mail as mail
import utils.utils as utils
from aphylogeo.genetic_trees import GeneticTrees
from aphylogeo.params import Params
from enums import convert_settings_to_codes

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Suppress repetitive warnings that flood the worker terminal.
# BiopythonDeprecationWarning inherits from BiopythonWarning(Warning), NOT
# DeprecationWarning, so we must filter by module only (no category restriction).
warnings.filterwarnings("ignore", module=r"Bio\.Application")

# ── Paths ─────────────────────────────────────────────────────────────────────
# apps/utils/background_tasks.py → project root is three levels up.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SETTINGS_FILE = _PROJECT_ROOT / "genetic_settings_file.json"
TEMP_DIR = _PROJECT_ROOT / "temp"

# ── Redis / RQ primitives ─────────────────────────────────────────────────────
_redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
redis_conn = Redis.from_url(_redis_url)
task_queue = Queue(connection=redis_conn)

# Persistent calibration key (seconds per operation)
CALIBRATED_TIME_KEY = "iphylogeo:background:calibrated_time_per_operation"

# RQ retention settings
RQ_RESULT_TTL_SECONDS = 3600
RQ_FAILURE_TTL_SECONDS = 86400

# Calibration constants based on observed performance
REFERENCE_TIME_PER_OPERATION = 0.40
BASE_OVERHEAD_TIME = 12
TIME_PER_CLIMATIC_COLUMN = 1.0
ALIGNMENT_TIME_PER_SEQ = 0.20

# All phases (alignment + tree sub-steps) emit "Started/Finished: X / N" logs.
TOTAL_STEPS_GENETIC = 4
TOTAL_STEPS_ALIGNED = 3
OUTPUT_OVERHEAD = 5

# Phase-based progress floors.
PHASE_PROGRESS_FLOOR = {
    "pending": 2,
    "climatic_trees": 18,
    "alignement": 42,
    "alignment": 42,
    "genetic_trees": 78,
    "output": 92,
}


def _time_based_progress(elapsed: float, estimated: float) -> float:
    """Return linear time-based progress capped at 95%."""
    if estimated <= 0:
        return 0.0
    return min(95.0, elapsed / estimated * 100.0)


def _count_pairwise_operations(genetic_file=None, aligned_genetic_file: str = None) -> tuple[int, int]:
    """Return (num_sequences, num_operations) for genetic/aligned inputs."""
    num_sequences = 0
    if genetic_file:
        num_sequences = count_sequences(genetic_file)
    elif aligned_genetic_file:
        try:
            aligned_data = json.loads(aligned_genetic_file)
            if isinstance(aligned_data, dict) and "msa" in aligned_data:
                msa_windows = aligned_data.get("msa", {})
                first_window = next(iter(msa_windows.values()), "")
                num_sequences = first_window.count(">")
            else:
                num_sequences = (
                    len(aligned_data)
                    if isinstance(aligned_data, (list, dict))
                    else 4
                )
        except Exception:
            num_sequences = 4

    num_operations = 0
    if num_sequences > 0:
        num_operations = (num_sequences * (num_sequences - 1)) // 2
        if num_operations < 1:
            num_operations = num_sequences

    return num_sequences, num_operations


def _get_calibrated_time_per_operation() -> float | None:
    """Get persisted seconds/op calibration from Redis."""
    try:
        raw_value = redis_conn.get(CALIBRATED_TIME_KEY)
        if raw_value is None:
            return None
        return float(raw_value)
    except Exception:
        return None


def _set_calibrated_time_per_operation(value: float):
    """Persist seconds/op calibration in Redis."""
    try:
        redis_conn.set(CALIBRATED_TIME_KEY, f"{value:.6f}")
    except Exception:
        pass


def _fetch_job(result_id: str) -> Job | None:
    """Fetch an RQ job by id; return None if not available."""
    if not result_id:
        return None
    try:
        return Job.fetch(str(result_id), connection=redis_conn)
    except (NoSuchJobError, RedisError):
        return None
    except Exception:
        return None


def _resolve_job_for_result(result_id: str) -> Job | None:
    """Return current worker job when possible; otherwise fetch by id."""
    current = get_current_job()
    if current is not None and str(current.id) == str(result_id):
        return current
    return _fetch_job(result_id)


def get_available_memory_gb() -> float:
    """Get the available system memory in GB."""
    if PSUTIL_AVAILABLE:
        try:
            mem = psutil.virtual_memory()
            return mem.available / (1024**3)
        except Exception:
            pass
    return 8.0


def get_total_memory_gb() -> float:
    """Get the total system memory in GB."""
    if PSUTIL_AVAILABLE:
        try:
            mem = psutil.virtual_memory()
            return mem.total / (1024**3)
        except Exception:
            pass
    return 16.0


def count_sequences(genetic_file) -> int:
    """Count the number of sequences in a genetic file."""
    if not genetic_file:
        return 0

    if isinstance(genetic_file, dict):
        num_sequences = len(genetic_file)
        print(f"[count_sequences] Dict with {num_sequences} sequences (keys)")

        if num_sequences > 0:
            first_key = list(genetic_file.keys())[0]
            first_value = genetic_file[first_key]
            print(
                f"[count_sequences] Example: '{first_key}' -> {len(str(first_value))} chars"
            )

        return num_sequences

    if isinstance(genetic_file, str):
        count = genetic_file.count(">")
        print(f"[count_sequences] String with {count} '>' characters")
        return count if count > 0 else 1

    print(f"[count_sequences] Unknown type: {type(genetic_file)}, returning 1")
    return 1


def count_climatic_columns(climatic_file: str) -> int:
    """Count the number of columns in climatic data."""
    if not climatic_file:
        return 0

    try:
        df = pd.read_json(io.StringIO(climatic_file))
        return max(0, len(df.columns) - 1)
    except Exception:
        return 2


def estimate_processing_time(
    climatic_file: str,
    genetic_file=None,
    aligned_genetic_file: str = None,
    genetic_tree_file: str = None,
) -> float:
    """Estimate total processing time (seconds)."""
    estimated_time = BASE_OVERHEAD_TIME

    available_ram = get_available_memory_gb()
    total_ram = get_total_memory_gb()

    num_climatic_cols = count_climatic_columns(climatic_file)
    num_sequences, num_operations = _count_pairwise_operations(
        genetic_file, aligned_genetic_file
    )

    calibrated = _get_calibrated_time_per_operation()
    time_per_operation = (
        calibrated if calibrated is not None else REFERENCE_TIME_PER_OPERATION
    )

    if genetic_file or aligned_genetic_file:
        sequence_time = num_operations * time_per_operation
        alignment_time = (num_sequences * ALIGNMENT_TIME_PER_SEQ) if genetic_file else 0

        estimated_time += sequence_time + alignment_time

        print(f"[Time Estimation] Pairwise: {num_sequences} seq -> {num_operations} ops")
        print(
            f"[Time Estimation] Breakdown: ops={num_operations} x {time_per_operation:.3f}s "
            f"= {sequence_time:.1f}s + alignment={alignment_time:.1f}s"
        )

    elif genetic_tree_file:
        estimated_time += 10

    climatic_time = num_climatic_cols * TIME_PER_CLIMATIC_COLUMN
    estimated_time += climatic_time

    print(f"[Time Estimation] Available RAM: {available_ram:.2f} GB / {total_ram:.2f} GB")
    print(
        f"[Time Estimation] Sequences: {num_sequences}, Climatic columns: {num_climatic_cols}"
    )
    print(
        f"[Time Estimation] Total estimated time: {estimated_time:.1f} seconds "
        f"({estimated_time / 60:.1f} minutes)"
    )

    return max(5, estimated_time)


def get_task_status(result_id: str) -> dict:
    """
    Get current status using RQ job metadata and DB fallback.

    Returns:
        dict with 'status', 'progress', 'estimated_time', 'elapsed_time', optional 'error'
    """
    job = _fetch_job(result_id)

    db_status = None
    try:
        db_result = results_ctrl.get_result(result_id)
        if db_result:
            db_status = str(db_result.get("status", "")).lower()
    except Exception:
        db_status = None

    if job is not None:
        meta = dict(job.meta or {})

        try:
            rq_status = job.get_status(refresh=True)
        except Exception:
            rq_status = job.get_status()

        status = str(meta.get("status", "pending")).lower()
        if rq_status == "finished":
            status = "complete"
        elif rq_status in {"failed", "stopped", "canceled"}:
            status = "error"

        # DB remains source of truth for terminal states.
        if db_status in {"complete", "error"}:
            status = db_status

        phase_status = db_status or status
        phase_floor = PHASE_PROGRESS_FLOOR.get(phase_status, 0)

        progress = float(meta.get("progress", 0) or 0)
        estimated_time = float(meta.get("estimated_time", 0) or 0)
        elapsed_time = float(meta.get("elapsed_time", 0) or 0)

        if "start_time" in meta and estimated_time > 0:
            elapsed_time = max(0.0, time.time() - float(meta["start_time"]))
            if status not in {"complete", "error"}:
                # Pure linear time-based progress — no phase jumps, no easing.
                # Phase floors are only a fallback when we have no timing data.
                progress = max(progress, _time_based_progress(elapsed_time, estimated_time))
        else:
            progress = max(progress, phase_floor)

        if status == "complete":
            progress = 100
        elif status == "error":
            progress = 0
        else:
            progress = min(95, progress)

        payload = {
            "status": status,
            "progress": progress,
            "estimated_time": estimated_time,
            "elapsed_time": elapsed_time,
        }

        if status == "error":
            error_msg = meta.get("error")
            if not error_msg and getattr(job, "exc_info", None):
                lines = str(job.exc_info).splitlines()
                error_msg = lines[-1] if lines else str(job.exc_info)
            if error_msg:
                payload["error"] = error_msg

        return payload

    # Fallback when job does not exist in RQ (or expired).
    try:
        result = results_ctrl.get_result(result_id)
        if result:
            status = str(result.get("status", "unknown"))
            if status.lower() == "complete":
                return {"status": status, "progress": 100}
            if status.lower() == "error":
                return {"status": status, "progress": 0}
            return {
                "status": status,
                "progress": PHASE_PROGRESS_FLOOR.get(status.lower(), 0),
            }
    except Exception:
        pass

    return {"status": "not_found", "progress": 0}


def update_task_status(
    result_id: str,
    status: str,
    error: str = None,
    estimated_time: float = None,
    pipeline_mode: str = None,
    num_operations: int = None,
):
    """Update status/progress metadata for the corresponding RQ job."""
    job = _resolve_job_for_result(result_id)
    if job is None:
        return

    meta = dict(job.meta or {})

    status_lower = str(status).lower()
    meta["status"] = status_lower
    meta["sub_progress"] = None

    if error:
        meta["error"] = error

    if pipeline_mode is not None:
        meta["pipeline_mode"] = pipeline_mode

    if num_operations is not None:
        meta["num_operations"] = int(num_operations)

    if estimated_time is not None:
        meta["estimated_time"] = float(estimated_time)
        meta["start_time"] = time.time()

    if status_lower == "complete":
        meta["progress"] = 100

        start_time = meta.get("start_time")
        operations = int(meta.get("num_operations") or 0)
        if start_time and operations > 0:
            observed_elapsed = max(0.1, time.time() - float(start_time))
            observed_time_per_op = observed_elapsed / operations
            if 0.01 <= observed_time_per_op <= 10:
                calibrated = _get_calibrated_time_per_operation()
                if calibrated is None:
                    new_calibrated = observed_time_per_op
                else:
                    new_calibrated = (calibrated * 0.60) + (observed_time_per_op * 0.40)
                _set_calibrated_time_per_operation(new_calibrated)
                print(
                    "[Time Estimation] Calibrated time/op updated to "
                    f"{new_calibrated:.3f}s (observed {observed_time_per_op:.3f}s)"
                )

    elif status_lower == "error":
        meta["progress"] = 0

    else:
        floor = PHASE_PROGRESS_FLOOR.get(status_lower, 0)
        current_progress = float(meta.get("progress", 0) or 0)
        meta["progress"] = max(current_progress, floor)

    if "start_time" in meta:
        meta["elapsed_time"] = max(0.0, time.time() - float(meta["start_time"]))

    job.meta = meta
    try:
        job.save_meta()
    except Exception:
        pass


def _recalculate_estimate(job: Job, done: int, total: int):
    """
    Correct estimated_time using multiProcessor progress lines and store in job.meta.
    """
    if total <= 0:
        return

    now = time.time()
    meta = dict(job.meta or {})

    if "start_time" not in meta:
        meta["start_time"] = now

    pipeline_start = float(meta["start_time"])

    # Initialize step trackers on first progress event.
    if "mp_step_start" not in meta:
        meta["mp_step_start"] = now
        meta["mp_step_total"] = total
        meta["mp_completed"] = []
        meta["mp_step_count"] = 0
        meta["mp_prev_total"] = total

    # Detect step boundary when operation total changes.
    if total != meta["mp_prev_total"]:
        meta["mp_step_start"] = now
        meta["mp_step_total"] = total
        meta["mp_step_count"] = int(meta.get("mp_step_count", 0)) + 1
        meta["mp_prev_total"] = total
        print(f"[Progress] Step {meta['mp_step_count'] + 1} started (N={total})")

    step_elapsed = now - float(meta["mp_step_start"])
    rate = 0.0

    if done > 0 and step_elapsed > 0.5:
        rate = done / step_elapsed
        remaining_current = max(0, total - done) / rate
    else:
        remaining_current = max(
            0,
            float(meta.get("estimated_time", 60.0)) - (now - pipeline_start),
        )

    completed_durations = list(meta.get("mp_completed", []))
    steps_done = int(meta.get("mp_step_count", 0))
    mode = meta.get("pipeline_mode", "genetic")
    total_steps = TOTAL_STEPS_GENETIC if mode == "genetic" else TOTAL_STEPS_ALIGNED
    steps_remaining_after_current = max(0, total_steps - steps_done - 1)

    if completed_durations:
        avg_step_time = sum(completed_durations) / len(completed_durations)
    elif step_elapsed > 0.5 and done > 0:
        avg_step_time = total * step_elapsed / done
    else:
        avg_step_time = float(meta.get("estimated_time", 60.0)) / total_steps

    remaining_future = steps_remaining_after_current * avg_step_time

    total_elapsed = now - pipeline_start
    remaining = remaining_current + remaining_future + OUTPUT_OVERHEAD
    meta["estimated_time"] = total_elapsed + remaining
    meta["elapsed_time"] = total_elapsed
    meta["sub_progress"] = max(0, min(100, round(done / total * 100)))

    print(
        f"[Progress] Step {steps_done + 1}/{total_steps}  {done}/{total}  "
        f"rate={rate:.3f} ops/s  remaining_current={remaining_current:.1f}s  "
        f"avg_step={avg_step_time:.1f}s  future_steps={steps_remaining_after_current}  "
        f"remaining≈{remaining:.1f}s"
    )

    job.meta = meta
    try:
        job.save_meta()
    except Exception:
        pass


def record_step_elapsed(result_id: str, elapsed_seconds: float):
    """
    Record an actual step duration from a "Time elapsed: T seconds" line.
    """
    job = _resolve_job_for_result(result_id)
    if job is None:
        return

    meta = dict(job.meta or {})
    completed = list(meta.get("mp_completed", []))
    completed.append(float(elapsed_seconds))
    meta["mp_completed"] = completed

    print(
        f"[Progress] Step completed in {elapsed_seconds:.1f}s "
        f"({len(completed)} steps done)"
    )

    job.meta = meta
    try:
        job.save_meta()
    except Exception:
        pass


def update_task_sub_progress(result_id: str, done: int, total: int):
    """Update within-step sub-progress and adaptively correct estimated_time."""
    if total <= 0:
        return

    job = _resolve_job_for_result(result_id)
    if job is None:
        return

    _recalculate_estimate(job, done, total)


class ProgressCapture(io.TextIOBase):
    """
    Intercepts aphylogeo multiProcessor stdout lines:
      - "Finished/Started: X / N" -> progress update + estimate correction
      - "Time elapsed: T seconds" -> actual sub-step duration

    Noisy aphylogeo stats lines (memory, %, counters) are parsed for metadata
    but not forwarded to the terminal to keep worker output readable.
    """

    _PROGRESS_PATTERN = re.compile(r"(?:Started|Finished):\s+(\d+)\s*/\s*(\d+)")
    _ELAPSED_PATTERN = re.compile(r"Time elapsed:\s+([\d.]+)\s+seconds")
    # Lines to capture silently — they repeat hundreds of times per run.
    _NOISY_PATTERN = re.compile(
        r"(?:Started:|Finished:|Available memory:|Active processes:|"
        r"Min memory per:|Time for one:|Time elapsed:|Completed with|"
        r"Creating bootstrap|---|\d+\s*%)"
    )

    def __init__(self, result_id: str, inner):
        self.result_id = result_id
        self.inner = inner

    def write(self, s: str) -> int:
        m = self._PROGRESS_PATTERN.search(s)
        if m:
            done, total = int(m.group(1)), int(m.group(2))
            update_task_sub_progress(self.result_id, done, total)

        e = self._ELAPSED_PATTERN.search(s)
        if e:
            record_step_elapsed(self.result_id, float(e.group(1)))

        # Only forward lines that aren't repetitive aphylogeo stats noise.
        if not self._NOISY_PATTERN.search(s):
            return self.inner.write(s)
        return len(s)

    def flush(self):
        self.inner.flush()


def run_pipeline_async(
    result_id: str,
    climatic_file: str,
    genetic_file: dict = None,
    aligned_genetic_file: str = None,
    genetic_tree_file: str = None,
    params_climatic: dict = None,
    email: str = None,
):
    """
    Enqueue the phylogeo pipeline in RQ.
    """
    print(f"[Pipeline] Starting run_pipeline_async for result_id: {result_id}")

    print("[Pipeline] Estimating processing time...")
    _, num_operations = _count_pairwise_operations(genetic_file, aligned_genetic_file)
    estimated_time = estimate_processing_time(
        climatic_file, genetic_file, aligned_genetic_file, genetic_tree_file
    )
    print(f"[Pipeline] Estimated time: {estimated_time:.1f}s")

    if genetic_file is not None:
        pipeline_mode = "genetic"
    elif aligned_genetic_file is not None:
        pipeline_mode = "aligned"
    else:
        pipeline_mode = "tree"

    job = task_queue.enqueue(
        run_pipeline_task,
        result_id,
        climatic_file,
        genetic_file,
        aligned_genetic_file,
        genetic_tree_file,
        params_climatic,
        email,
        job_id=str(result_id),
        job_timeout=7200,          # 2 h hard cap; avoids zombie jobs
        result_ttl=RQ_RESULT_TTL_SECONDS,
        failure_ttl=RQ_FAILURE_TTL_SECONDS,
    )

    # Seed metadata immediately so UI can poll before worker starts.
    job.meta = dict(job.meta or {})
    job.meta.update(
        {
            "status": "pending",
            "progress": PHASE_PROGRESS_FLOOR["pending"],
            "estimated_time": estimated_time,
            "start_time": time.time(),
            "pipeline_mode": pipeline_mode,
            "num_operations": int(num_operations),
            "sub_progress": None,
        }
    )
    job.save_meta()

    print(f"[Pipeline] Task enqueued successfully for result_id: {result_id}")
    return result_id


def _write_genetic_temp_fasta(path: str, genetic_file):
    """Write genetic input to a FASTA temp file used by downstream params."""
    with open(path, "w", encoding="utf-8") as handle:
        if isinstance(genetic_file, dict):
            for seq_name, sequence in genetic_file.items():
                handle.write(f">{seq_name}\n{sequence}\n")
        elif isinstance(genetic_file, str):
            handle.write(genetic_file)


def run_pipeline_task(
    result_id: str,
    climatic_file: str,
    genetic_file: dict = None,
    aligned_genetic_file: str = None,
    genetic_tree_file: str = None,
    params_climatic: dict = None,
    email: str = None,
):
    """
    RQ worker function that executes the phylogeo pipeline.
    """
    print(f"[Pipeline Task] Starting run_pipeline_task for result_id: {result_id}")

    temp_fasta_path = None
    try:
        # Re-read latest settings from JSON and apply to Params
        print(f"[Pipeline Task] Loading settings from {SETTINGS_FILE}...")
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as settings_file:
                latest_settings = json.load(settings_file)
            latest_codes = convert_settings_to_codes(latest_settings)
            Params.update_from_dict(
                {k: v for k, v in latest_codes.items() if k in Params.PARAMETER_KEYS}
            )
            print("[Pipeline Task] Settings loaded successfully")
        except Exception as e:
            print(f"[Warning] Could not reload settings: {e}")

        # Prepare climatic trees
        print("[Pipeline Task] Creating climatic trees...")
        selected_columns = params_climatic.get("names") if params_climatic else None
        climatic_trees = utils.create_climatic_trees(
            result_id, climatic_file, selected_columns
        )
        update_task_status(result_id, "climatic_trees")
        print("[Pipeline Task] Climatic trees created successfully")

        genetic_trees = None

        if genetic_file is not None:
            # Run full genetic pipeline (alignment + trees + output)
            temp_dir = str(TEMP_DIR)
            os.makedirs(temp_dir, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".fasta",
                dir=temp_dir,
                delete=False,
                encoding="utf-8",
            ) as temp_fasta:
                temp_fasta_path = temp_fasta.name

            _write_genetic_temp_fasta(temp_fasta_path, genetic_file)

            reference_gene_file = {
                "reference_gene_dir": os.path.dirname(temp_fasta_path),
                "reference_gene_file": os.path.basename(temp_fasta_path),
            }
            Params.update_from_dict(reference_gene_file)

            update_task_status(result_id, "alignment")
            original_stdout = sys.stdout
            sys.stdout = ProgressCapture(result_id, original_stdout)
            try:
                utils.run_genetic_pipeline(
                    result_id, climatic_file, genetic_file, climatic_trees
                )
            finally:
                sys.stdout = original_stdout

        elif aligned_genetic_file is not None:
            # Process pre-aligned genetic data
            from aphylogeo.alignement import Alignment

            loaded_seq_alignment = Alignment.from_json_string(aligned_genetic_file)
            msa_set = loaded_seq_alignment.msa

            results_ctrl.update_result({"_id": result_id, "msaSet": msa_set})

            update_task_status(result_id, "genetic_trees")
            original_stdout = sys.stdout
            sys.stdout = ProgressCapture(result_id, original_stdout)
            try:
                genetic_trees = utils.create_genetic_trees(result_id, msa_set)
            finally:
                sys.stdout = original_stdout

            update_task_status(result_id, "output")
            utils.create_output(
                result_id,
                climatic_trees,
                genetic_trees,
                pd.read_json(io.StringIO(climatic_file)),
            )

        elif genetic_tree_file is not None:
            # Process pre-computed genetic trees
            loaded_genetic_trees = GeneticTrees.load_trees_from_json(genetic_tree_file)
            genetic_trees = loaded_genetic_trees.trees

            results_ctrl.update_result(
                {
                    "_id": result_id,
                    "genetic_trees": genetic_trees,
                }
            )

            update_task_status(result_id, "genetic_trees")
            update_task_status(result_id, "output")
            utils.create_output(
                result_id,
                climatic_trees,
                genetic_trees,
                pd.read_json(io.StringIO(climatic_file)),
            )

        update_task_status(result_id, "complete")

        if email:
            try:
                results_url = f"/result/{result_id}"
                mail.send_results_ready_email(email, results_url)
            except Exception as e:
                print(f"[Warning] Could not send email: {e}")

        return result_id

    except Exception as e:
        print(f"[Error in background pipeline]: {e}")
        update_task_status(result_id, "error", error=str(e))
        results_ctrl.update_result({"_id": result_id, "status": "error"})
        raise

    finally:
        if temp_fasta_path:
            try:
                os.unlink(temp_fasta_path)
            except OSError:
                pass
