"""
Background task management for running phylogeo computations asynchronously.

This module provides functionality to run the heavy phylogeo pipeline in the background,
allowing users to navigate freely while the computation is in progress.
"""

import io
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import db.controllers.results as results_ctrl
import utils.utils as utils
import utils.mail as mail
from aphylogeo.alignement import Alignment
from aphylogeo.genetic_trees import GeneticTrees
from aphylogeo.params import Params
from enums import convert_settings_to_codes

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Thread pool for background tasks (max 4 concurrent tasks)
_executor = ThreadPoolExecutor(max_workers=4)

# Store for tracking tasks (in production, use Redis or similar)
_task_store = {}
_task_lock = threading.Lock()

# Calibration constants based on observed performance
# Reference: observed from terminal output
# - 35 sequences -> 595 operations (pairwise comparisons: n*(n-1)/2 = 35*34/2 = 595)
# - 107 ops completed in 256 seconds -> approximately 2.4s per op with some parallelism
# - Observed "Time for one" in aphylogeo: 5.5 seconds (single process calibration)
# - Effective parallelism appears low due to process spawn overhead and memory constraints
#
# Real-world observation:
# - 595 ops at 18% in 256s -> total ~1420s expected (about 24 minutes)
# - This suggests ~2.5 effective parallel processes on average
REFERENCE_TIME_PER_OPERATION = 2.4   # Effective seconds per operation (observed: 107 ops / 256s)
BASE_OVERHEAD_TIME = 20              # Base overhead time in seconds (startup, file I/O, etc.)
TIME_PER_CLIMATIC_COLUMN = 1.5       # Seconds per climatic column for tree building
ALIGNMENT_TIME_PER_SEQ = 1.0         # Additional time for alignment per sequence

# Parallelism estimation
# Based on observation: 595 ops, 256s for 107 ops -> ~2.4s per op effective
# Calibration shows 5.5s per single op, so effective parallelism = 5.5/2.4 = 2.3
# We use conservative estimate of 2-3 effective parallel processes
RAM_PER_PROCESS_GB = 0.15            # Conservative: ~0.15 GB per process
MAX_EFFECTIVE_PARALLELISM = 3        # Observed effective parallelism (conservative)


def get_available_memory_gb() -> float:
    """
    Get the available system memory in GB.

    Returns:
        Available memory in GB, or a default value if psutil is not available.
    """
    if PSUTIL_AVAILABLE:
        try:
            mem = psutil.virtual_memory()
            return mem.available / (1024 ** 3)  # Convert bytes to GB
        except Exception:
            pass
    # Default to 8 GB if we can't detect
    return 8.0


def get_total_memory_gb() -> float:
    """
    Get the total system memory in GB.

    Returns:
        Total memory in GB, or a default value if psutil is not available.
    """
    if PSUTIL_AVAILABLE:
        try:
            mem = psutil.virtual_memory()
            return mem.total / (1024 ** 3)  # Convert bytes to GB
        except Exception:
            pass
    # Default to 16 GB if we can't detect
    return 16.0


def count_sequences(genetic_file) -> int:
    """
    Count the number of sequences in a genetic file.

    The genetic_file is a dict where:
    - Keys are sequence names (e.g., 'ICE1-Bod001')
    - Values are DNA/RNA strings

    The number of sequences = number of keys in the dict.
    The actual processing time depends on n² comparisons where n = number of sequences.

    Args:
        genetic_file: Dict with genetic data (FASTA sequences) or string

    Returns:
        Number of sequences
    """
    if not genetic_file:
        return 0

    # genetic_file is a dict where keys are sequence names
    if isinstance(genetic_file, dict):
        num_sequences = len(genetic_file)
        print(f"[count_sequences] Dict with {num_sequences} sequences (keys)")

        if num_sequences > 0:
            first_key = list(genetic_file.keys())[0]
            first_value = genetic_file[first_key]
            print(f"[count_sequences] Example: '{first_key}' -> {len(str(first_value))} chars")

        return num_sequences

    # If it's a string (FASTA format), count '>' characters
    if isinstance(genetic_file, str):
        count = genetic_file.count('>')
        print(f"[count_sequences] String with {count} '>' characters")
        return count if count > 0 else 1

    print(f"[count_sequences] Unknown type: {type(genetic_file)}, returning 1")
    return 1


def count_climatic_columns(climatic_file: str) -> int:
    """
    Count the number of columns in climatic data.

    Args:
        climatic_file: JSON string with climatic data

    Returns:
        Number of columns (excluding ID column)
    """
    if not climatic_file:
        return 0

    try:
        df = pd.read_json(io.StringIO(climatic_file))
        return max(0, len(df.columns) - 1)  # Exclude ID column
    except Exception:
        return 2  # Default estimate


def estimate_processing_time(
    climatic_file: str,
    genetic_file=None,
    aligned_genetic_file: str = None,
    genetic_tree_file: str = None
) -> float:
    """
    Estimate the total processing time based on number of sequences.

    Based on observed aphylogeo performance:
    - Operations = n*(n-1)/2 where n = number of sequences (pairwise comparisons)
    - Example: 35 sequences -> 35*34/2 = 595 operations
    - Effective time per operation: ~2.4 seconds (accounts for average parallelism)
    - Observed: 107 ops in 256s = ~2.4s per operation

    Args:
        climatic_file: JSON string with climatic data
        genetic_file: Dict with genetic data
        aligned_genetic_file: JSON string with aligned genetic data
        genetic_tree_file: JSON string with genetic tree data

    Returns:
        Estimated time in seconds
    """
    estimated_time = BASE_OVERHEAD_TIME

    # Get available RAM for logging
    available_ram = get_available_memory_gb()
    total_ram = get_total_memory_gb()

    # Count data elements
    num_climatic_cols = count_climatic_columns(climatic_file)
    num_sequences = 0

    if genetic_file:
        num_sequences = count_sequences(genetic_file)
    elif aligned_genetic_file:
        try:
            aligned_data = json.loads(aligned_genetic_file)
            if isinstance(aligned_data, dict) and "msa" in aligned_data:
                # Alignment JSON format: count ">" in first window's FASTA string
                msa_windows = aligned_data.get("msa", {})
                first_window = next(iter(msa_windows.values()), "")
                num_sequences = first_window.count(">")
            else:
                num_sequences = len(aligned_data) if isinstance(aligned_data, (list, dict)) else 4
        except Exception:
            num_sequences = 4

    # === Main time calculation ===
    # Number of operations = pairwise comparisons = n*(n-1)/2
    if genetic_file or aligned_genetic_file:
        # Pairwise comparisons formula
        num_operations = (num_sequences * (num_sequences - 1)) // 2
        if num_operations < 1:
            num_operations = num_sequences  # Fallback for single sequence

        # Use effective time per operation (already accounts for average parallelism)
        # Based on observation: 107 ops / 256s = 2.4s per op effective
        sequence_time = num_operations * REFERENCE_TIME_PER_OPERATION

        # Add alignment time only for non-aligned data (pre-aligned skips this step)
        alignment_time = (num_sequences * ALIGNMENT_TIME_PER_SEQ) if genetic_file else 0

        estimated_time += sequence_time + alignment_time

        print(f"[Time Estimation] Pairwise: {num_sequences} seq -> {num_operations} ops")
        print(f"[Time Estimation] Breakdown: ops={num_operations} x {REFERENCE_TIME_PER_OPERATION}s = {sequence_time:.1f}s + alignment={alignment_time:.1f}s")

    elif genetic_tree_file:
        # Trees already provided, minimal processing
        estimated_time += 10

    # Add small overhead for climatic processing
    climatic_time = num_climatic_cols * TIME_PER_CLIMATIC_COLUMN
    estimated_time += climatic_time

    # Log estimation details for debugging
    print(f"[Time Estimation] Available RAM: {available_ram:.2f} GB / {total_ram:.2f} GB")
    print(f"[Time Estimation] Sequences: {num_sequences}, Climatic columns: {num_climatic_cols}")
    print(f"[Time Estimation] Total estimated time: {estimated_time:.1f} seconds ({estimated_time / 60:.1f} minutes)")

    # No maximum cap - let it estimate the real time
    return max(5, estimated_time)


def get_task_status(result_id: str) -> dict:
    """
    Get the current status of a background task.

    Args:
        result_id: The ID of the result being processed

    Returns:
        dict with 'status', 'progress', 'estimated_time', 'elapsed_time', and optional 'error' keys
    """
    with _task_lock:
        if result_id in _task_store:
            task_info = _task_store[result_id].copy()
            # Calculate progress based on elapsed time vs estimated time
            if "start_time" in task_info and "estimated_time" in task_info:
                elapsed = time.time() - task_info["start_time"]
                estimated = task_info["estimated_time"]
                # Progress based on time, capped at 95% until complete
                progress = min(95, (elapsed / estimated) * 100)
                task_info["progress"] = progress
                task_info["elapsed_time"] = elapsed
            return task_info

    # If not in memory store, check the database
    try:
        result = results_ctrl.get_result(result_id)
        if result:
            status = result.get("status", "unknown")
            if status.lower() == "complete":
                return {"status": status, "progress": 100}
            return {"status": status, "progress": 0}
    except Exception:
        pass

    return {"status": "not_found", "progress": 0}


def update_task_status(result_id: str, status: str, error: str = None, estimated_time: float = None):
    """Update the status of a background task."""
    with _task_lock:
        if result_id not in _task_store:
            _task_store[result_id] = {}

        _task_store[result_id]["status"] = status
        # Reset sub-progress when moving to a new step
        _task_store[result_id]["sub_progress"] = None

        if error:
            _task_store[result_id]["error"] = error

        if estimated_time is not None:
            _task_store[result_id]["estimated_time"] = estimated_time
            _task_store[result_id]["start_time"] = time.time()

        if status.lower() == "complete":
            _task_store[result_id]["progress"] = 100
        elif status.lower() == "error":
            _task_store[result_id]["progress"] = 0


def update_task_sub_progress(result_id: str, done: int, total: int):
    """Update within-step sub-progress (0–100) from aphylogeo multiProcessor output."""
    if total <= 0:
        return
    with _task_lock:
        if result_id in _task_store:
            _task_store[result_id]["sub_progress"] = round(done / total * 100)


class ProgressCapture(io.TextIOBase):
    """
    A stdout wrapper that intercepts aphylogeo multiProcessor progress lines
    such as "Started:           1 / 4     25 %" and records the sub-progress
    into the _task_store for the given result_id.
    """

    # Pattern: "Started:   <done> / <total>"
    _PATTERN = re.compile(r"Started:\s+(\d+)\s*/\s*(\d+)")

    def __init__(self, result_id: str, inner):
        self.result_id = result_id
        self.inner = inner

    def write(self, s: str) -> int:
        m = self._PATTERN.search(s)
        if m:
            done, total = int(m.group(1)), int(m.group(2))
            update_task_sub_progress(self.result_id, done, total)
        return self.inner.write(s)

    def flush(self):
        self.inner.flush()


def cleanup_task(result_id: str):
    """Remove a task from the in-memory store."""
    with _task_lock:
        if result_id in _task_store:
            del _task_store[result_id]


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
    Submit the phylogeo pipeline to run in the background.

    Args:
        result_id: The ID of the result being processed
        climatic_file: JSON string with climatic data
        genetic_file: Dict with genetic data (FASTA sequences)
        aligned_genetic_file: JSON string with pre-aligned genetic data
        genetic_tree_file: JSON string with pre-computed genetic trees
        params_climatic: Dict with climatic parameters
        email: Optional email to notify when complete

    Returns:
        The result_id
    """
    print(f"[Pipeline] Starting run_pipeline_async for result_id: {result_id}")

    # Estimate processing time based on file sizes
    print("[Pipeline] Estimating processing time...")
    estimated_time = estimate_processing_time(
        climatic_file, genetic_file, aligned_genetic_file, genetic_tree_file
    )
    print(f"[Pipeline] Estimated time: {estimated_time:.1f}s")

    update_task_status(result_id, "pending", estimated_time=estimated_time)

    print("[Pipeline] Submitting task to executor...")
    _executor.submit(
        _run_pipeline_task,
        result_id,
        climatic_file,
        genetic_file,
        aligned_genetic_file,
        genetic_tree_file,
        params_climatic,
        email,
    )
    print(f"[Pipeline] Task submitted successfully for result_id: {result_id}")

    return result_id


def _run_pipeline_task(
    result_id: str,
    climatic_file: str,
    genetic_file: dict = None,
    aligned_genetic_file: str = None,
    genetic_tree_file: str = None,
    params_climatic: dict = None,
    email: str = None,
):
    """
    The actual pipeline execution that runs in a background thread.
    """
    print(f"[Pipeline Task] Starting _run_pipeline_task for result_id: {result_id}")
    try:
        # Re-read latest settings from JSON and apply to Params
        print("[Pipeline Task] Loading settings from genetic_settings_file.json...")
        try:
            with open("genetic_settings_file.json", "r") as _sf:
                _latest_settings = json.load(_sf)
            _latest_codes = convert_settings_to_codes(_latest_settings)
            Params.update_from_dict(
                {k: v for k, v in _latest_codes.items() if k in Params.PARAMETER_KEYS}
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
        print("[Pipeline Task] Climatic trees created successfully")

        genetic_trees = None

        # Process genetic data based on input type
        if genetic_file is not None:
            # Run full genetic pipeline (alignment + trees + output)
            reference_gene_file = {
                "reference_gene_dir": os.getcwd() + "\\temp",
                "reference_gene_file": "genetic_data.fasta",
            }
            Params.update_from_dict(reference_gene_file)

            # Capture multiProcessor stdout to track sub-step progress
            _orig_stdout = sys.stdout
            sys.stdout = ProgressCapture(result_id, _orig_stdout)
            try:
                utils.run_genetic_pipeline(
                    result_id, climatic_file, genetic_file, climatic_trees
                )
            finally:
                sys.stdout = _orig_stdout

        elif aligned_genetic_file is not None:
            # Process pre-aligned genetic data
            loaded_seq_alignment = Alignment.from_json_string(aligned_genetic_file)
            msaSet = loaded_seq_alignment.msa

            results_ctrl.update_result(
                {"_id": result_id, "msaSet": msaSet}
            )

            # Capture multiProcessor stdout to track sub-step progress
            _orig_stdout = sys.stdout
            sys.stdout = ProgressCapture(result_id, _orig_stdout)
            try:
                genetic_trees = utils.create_genetic_trees(result_id, msaSet)
            finally:
                sys.stdout = _orig_stdout

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

            utils.create_output(
                result_id,
                climatic_trees,
                genetic_trees,
                pd.read_json(io.StringIO(climatic_file)),
            )

        update_task_status(result_id, "complete")

        # Send email notification if provided
        if email:
            try:
                results_url = f"/result/{result_id}"
                mail.send_results_ready_email(email, results_url)
            except Exception as e:
                print(f"[Warning] Could not send email: {e}")

    except Exception as e:
        print(f"[Error in background pipeline]: {e}")
        update_task_status(result_id, "error", str(e))
        results_ctrl.update_result(
            {
                "_id": result_id,
                "status": "error",
            }
        )
    finally:
        # Clean up after some delay to allow status checks
        def delayed_cleanup():
            import time
            time.sleep(60)  # Keep status for 1 minute after completion
            cleanup_task(result_id)

        threading.Thread(target=delayed_cleanup, daemon=True).start()
