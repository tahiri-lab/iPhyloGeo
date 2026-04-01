import secrets

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
