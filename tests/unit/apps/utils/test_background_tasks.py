import json
import os
import sys
import time
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../apps"))

# Prevent DB and aphylogeo imports from running at module level
sys.modules.setdefault("db", MagicMock())
sys.modules.setdefault("db.db_validator", MagicMock())
sys.modules.setdefault("db.controllers", MagicMock())
sys.modules.setdefault("db.controllers.results", MagicMock())
sys.modules.setdefault("aphylogeo", MagicMock())
sys.modules.setdefault("aphylogeo.alignement", MagicMock())
sys.modules.setdefault("aphylogeo.genetic_trees", MagicMock())
sys.modules.setdefault("aphylogeo.params", MagicMock())
sys.modules.setdefault("aphylogeo.utils", MagicMock())
sys.modules.setdefault("utils.utils", MagicMock())
sys.modules.setdefault("utils.mail", MagicMock())
sys.modules.setdefault("enums", MagicMock())

import apps.utils.background_tasks as background_tasks  # noqa: E402
from apps.utils.background_tasks import count_climatic_columns, count_sequences  # noqa: E402


pytestmark = pytest.mark.unit


class FakeJob:
    def __init__(self, job_id="job-1", status="started", meta=None):
        self.id = job_id
        self._status = status
        self.meta = meta or {}
        self.saved = False
        self.exc_info = None

    def get_status(self, refresh=False):
        return self._status

    def save_meta(self):
        self.saved = True


@pytest.fixture(autouse=True)
def reset_background_mocks():
    background_tasks.results_ctrl.get_result.reset_mock()
    background_tasks.results_ctrl.get_result.return_value = None
    yield


# --- count_sequences ---


def test_count_sequences_dict():
    genetic = {"seq1": "ATCG", "seq2": "GCTA", "seq3": "TTTT"}
    assert count_sequences(genetic) == 3



def test_count_sequences_empty_dict():
    assert count_sequences({}) == 0



def test_count_sequences_none():
    assert count_sequences(None) == 0



def test_count_sequences_fasta_string():
    fasta = ">seq1\nATCG\n>seq2\nGCTA\n"
    assert count_sequences(fasta) == 2



def test_count_sequences_fasta_string_single():
    fasta = ">seq1\nATCG\n"
    assert count_sequences(fasta) == 1



def test_count_sequences_empty_string_returns_one():
    assert count_sequences("no-fasta-content") == 1



def test_count_sequences_unknown_type_returns_one():
    assert count_sequences(42) == 1


# --- count_climatic_columns ---


def test_count_climatic_columns_basic():
    df_json = json.dumps(
        {
            "id": ["a", "b"],
            "temp": [1, 2],
            "rain": [3, 4],
            "wind": [5, 6],
        }
    )
    assert count_climatic_columns(df_json) == 3



def test_count_climatic_columns_only_id_column():
    df_json = json.dumps({"id": ["a", "b"]})
    assert count_climatic_columns(df_json) == 0



def test_count_climatic_columns_empty_string():
    assert count_climatic_columns("") == 0



def test_count_climatic_columns_none():
    assert count_climatic_columns(None) == 0



def test_count_climatic_columns_invalid_json_returns_default():
    assert count_climatic_columns("not-json") == 2


# --- RQ metadata behaviors ---


def test_get_task_status_uses_job_meta_and_phase_floor(monkeypatch):
    result_id = "result-1"
    fake_job = FakeJob(
        job_id=result_id,
        status="started",
        meta={
            "status": "pending",
            "estimated_time": 120.0,
            "start_time": time.time() - 2,
            "progress": 0,
        },
    )

    monkeypatch.setattr(background_tasks, "_fetch_job", lambda rid: fake_job)
    background_tasks.results_ctrl.get_result.return_value = {"status": "genetic_trees"}

    status = background_tasks.get_task_status(result_id)

    assert status["status"] == "pending"
    assert status["progress"] >= background_tasks.PHASE_PROGRESS_FLOOR["genetic_trees"]
    assert status["elapsed_time"] > 0



def test_get_task_status_db_fallback_when_job_missing(monkeypatch):
    monkeypatch.setattr(background_tasks, "_fetch_job", lambda rid: None)
    background_tasks.results_ctrl.get_result.return_value = {"status": "complete"}

    status = background_tasks.get_task_status("result-db")

    assert status["status"] == "complete"
    assert status["progress"] == 100



def test_update_task_status_complete_calibrates_time_per_operation(monkeypatch):
    result_id = "result-calib"
    fake_job = FakeJob(
        job_id=result_id,
        status="started",
        meta={
            "start_time": time.time() - 30,
            "num_operations": 100,
        },
    )

    calibrated_values = []
    monkeypatch.setattr(background_tasks, "_resolve_job_for_result", lambda rid: fake_job)
    monkeypatch.setattr(background_tasks, "_get_calibrated_time_per_operation", lambda: None)
    monkeypatch.setattr(
        background_tasks,
        "_set_calibrated_time_per_operation",
        lambda value: calibrated_values.append(value),
    )

    background_tasks.update_task_status(result_id, "complete")

    assert fake_job.meta["progress"] == 100
    assert fake_job.saved
    assert len(calibrated_values) == 1
    assert 0.2 <= calibrated_values[0] <= 0.5



def test_update_task_sub_progress_updates_estimate(monkeypatch):
    result_id = "result-progress"
    fake_job = FakeJob(
        job_id=result_id,
        status="started",
        meta={
            "start_time": time.time() - 10,
            "estimated_time": 120.0,
            "pipeline_mode": "genetic",
        },
    )

    monkeypatch.setattr(background_tasks, "_resolve_job_for_result", lambda rid: fake_job)

    background_tasks.update_task_sub_progress(result_id, done=5, total=20)

    assert "sub_progress" in fake_job.meta
    assert fake_job.meta["sub_progress"] >= 0
    assert "estimated_time" in fake_job.meta
    assert fake_job.saved



def test_record_step_elapsed_appends_duration(monkeypatch):
    result_id = "result-elapsed"
    fake_job = FakeJob(job_id=result_id, status="started", meta={"mp_completed": []})
    monkeypatch.setattr(background_tasks, "_resolve_job_for_result", lambda rid: fake_job)

    background_tasks.record_step_elapsed(result_id, 1.5)

    assert fake_job.meta["mp_completed"] == [1.5]
    assert fake_job.saved



def test_run_pipeline_async_enqueues_with_result_id_as_job_id(monkeypatch):
    captured = {}

    class FakeQueue:
        def enqueue(self, func, *args, **kwargs):
            captured["func"] = func
            captured["args"] = args
            captured["kwargs"] = kwargs
            return FakeJob(job_id=kwargs.get("job_id", "no-id"), status="queued", meta={})

    monkeypatch.setattr(background_tasks, "task_queue", FakeQueue())
    monkeypatch.setattr(background_tasks, "estimate_processing_time", lambda *a, **k: 30.0)

    result_id = "result-enqueue"
    returned_id = background_tasks.run_pipeline_async(
        result_id=result_id,
        climatic_file="{}",
        genetic_file={"a": "ATCG", "b": "ATCA"},
    )

    assert returned_id == result_id
    assert captured["kwargs"]["job_id"] == result_id
    assert captured["kwargs"]["result_ttl"] == background_tasks.RQ_RESULT_TTL_SECONDS



def test_progress_capture_dispatches_progress_and_elapsed(monkeypatch):
    calls = {"progress": [], "elapsed": []}

    monkeypatch.setattr(
        background_tasks,
        "update_task_sub_progress",
        lambda rid, done, total: calls["progress"].append((rid, done, total)),
    )
    monkeypatch.setattr(
        background_tasks,
        "record_step_elapsed",
        lambda rid, elapsed: calls["elapsed"].append((rid, elapsed)),
    )

    sink = []

    class Sink:
        def write(self, s):
            sink.append(s)
            return len(s)

        def flush(self):
            return None

    capture = background_tasks.ProgressCapture("result-cap", Sink())
    capture.write("Finished: 3 / 10\n")
    capture.write("Time elapsed: 1.25 seconds\n")

    assert calls["progress"] == [("result-cap", 3, 10)]
    assert calls["elapsed"] == [("result-cap", 1.25)]
    assert len(sink) == 2
