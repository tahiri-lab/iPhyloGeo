import pytest
from apps.db.controllers import results as results_ctrl
from db.db_validator import results_db

pytestmark = pytest.mark.integration


def _mongo_available():
    try:
        results_db.find_one({})
        return True
    except Exception:
        return False


def _minimal_result(**kwargs):
    base = {
        "status": "pending",
        "name": "integration-test",
        "result_type": ["climatic"],
    }
    base.update(kwargs)
    return base


def test_create_and_get_result_roundtrip():
    if not _mongo_available():
        pytest.skip("MongoDB is not available")

    result_id = None
    try:
        result_id = results_ctrl.create_result(_minimal_result())
        assert result_id is not None

        fetched = results_ctrl.get_result(result_id)
        assert fetched is not None
        assert fetched["status"] == "pending"
        assert fetched["name"] == "integration-test"
        assert fetched["result_type"] == ["climatic"]
        assert "created_at" in fetched
        assert "expired_at" in fetched
        assert fetched["expired_at"] > fetched["created_at"]
    finally:
        if result_id:
            try:
                results_ctrl.delete_result(result_id)
            except Exception:
                pass


def test_update_result_persists_to_mongodb():
    if not _mongo_available():
        pytest.skip("MongoDB is not available")

    result_id = None
    try:
        result_id = results_ctrl.create_result(_minimal_result())

        results_ctrl.update_result({"_id": result_id, "status": "complete"})

        fetched = results_ctrl.get_result(result_id)
        assert fetched["status"] == "complete"
        # name and result_type must still be there (update must not wipe other fields)
        assert fetched["name"] == "integration-test"
    finally:
        if result_id:
            try:
                results_ctrl.delete_result(result_id)
            except Exception:
                pass


def test_get_results_returns_ordered():
    if not _mongo_available():
        pytest.skip("MongoDB is not available")

    id1 = id2 = None
    try:
        id1 = results_ctrl.create_result(_minimal_result(name="first"))
        id2 = results_ctrl.create_result(_minimal_result(name="second"))

        results = results_ctrl.get_results([id1, id2])
        assert len(results) == 2
        assert results[0]["name"] == "first"
        assert results[1]["name"] == "second"
    finally:
        for rid in [id1, id2]:
            if rid:
                try:
                    results_ctrl.delete_result(rid)
                except Exception:
                    pass


def test_get_results_skips_nonexistent_id():
    """A valid-format but non-existent ObjectId must be silently skipped."""
    if not _mongo_available():
        pytest.skip("MongoDB is not available")

    result_id = None
    try:
        result_id = results_ctrl.create_result(_minimal_result())
        ghost_id = "000000000000000000000000"  # valid format, no matching doc

        results = results_ctrl.get_results([result_id, ghost_id])
        assert len(results) == 1
        assert results[0]["name"] == "integration-test"
    finally:
        if result_id:
            try:
                results_ctrl.delete_result(result_id)
            except Exception:
                pass
