import secrets
import time
import pytest
from apps.db.controllers import temp_results


pytestmark = pytest.mark.integration


def _new_temp_id():
    return temp_results.build_temp_result_id(secrets.token_urlsafe(8))


def test_redis_temp_result_roundtrip():
    if not temp_results.is_available():
        pytest.skip("Redis is not available")

    result_id = _new_temp_id()
    payload = {"status": "pending", "name": "ci-test", "result_type": "genetic"}

    created_id = temp_results.create_temp_result(result_id, payload, ttl_seconds=30)
    assert created_id == result_id

    fetched = temp_results.get_temp_result(result_id)
    assert fetched is not None
    assert fetched["_id"] == result_id
    assert fetched["is_temporary"] is True
    assert fetched["status"] == "pending"

    updated_id = temp_results.update_temp_result(result_id, {"status": "done"}, ttl_seconds=30)
    assert updated_id == result_id
    assert temp_results.get_temp_result(result_id)["status"] == "done"

    deleted_count = temp_results.delete_temp_result(result_id)
    assert deleted_count == 1
    assert temp_results.get_temp_result(result_id) is None


def test_update_temp_result_preserves_ttl():
    """update_temp_result must reuse the remaining TTL, not reset it."""
    if not temp_results.is_available():
        pytest.skip("Redis is not available")

    result_id = _new_temp_id()
    temp_results.create_temp_result(result_id, {"status": "pending"}, ttl_seconds=30)

    time.sleep(1)  # let 1 second elapse so remaining TTL < 30

    temp_results.update_temp_result(result_id, {"status": "running"})

    redis_client = temp_results._get_redis_client()
    remaining = redis_client.ttl(temp_results._key_for_result(result_id))

    # TTL must have been preserved (< 30), not reset back to the default
    assert 0 < remaining < 30

    temp_results.delete_temp_result(result_id)


def test_get_temp_results_batch_with_partial_missing_keys():
    """get_temp_results must skip missing keys without raising."""
    if not temp_results.is_available():
        pytest.skip("Redis is not available")

    id_present = _new_temp_id()
    id_missing = _new_temp_id()

    temp_results.create_temp_result(id_present, {"status": "pending"}, ttl_seconds=30)
    # id_missing is intentionally never created

    results = temp_results.get_temp_results([id_present, id_missing])

    assert id_present in results
    assert results[id_present]["status"] == "pending"
    assert id_missing not in results

    temp_results.delete_temp_result(id_present)
