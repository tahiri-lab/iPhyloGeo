import json
from datetime import datetime, timezone

from dotenv import dotenv_values, load_dotenv
from redis import Redis
from redis.exceptions import RedisError

load_dotenv()

ENV_CONFIG = {}
for key, value in dotenv_values().items():
    ENV_CONFIG[key] = value

TEMP_RESULT_PREFIX = "tmp_"
TEMP_RESULT_KEY_PREFIX = "iphylogeo:temp_result:"
DEFAULT_TTL_SECONDS = int(ENV_CONFIG.get("TEMP_RESULT_TTL_SECONDS", 7200))
DEFAULT_REDIS_URL = ENV_CONFIG.get("REDIS_URL", "redis://localhost:6379/0")


def _get_redis_client():
    return Redis.from_url(DEFAULT_REDIS_URL, decode_responses=True)


def get_default_ttl_seconds():
    return int(DEFAULT_TTL_SECONDS)


def is_available():
    try:
        return bool(_get_redis_client().ping())
    except Exception:
        return False


def is_temp_result_id(result_id):
    return isinstance(result_id, str) and result_id.startswith(TEMP_RESULT_PREFIX)


def build_temp_result_id(token):
    return f"{TEMP_RESULT_PREFIX}{token}"


def extract_temp_token(result_id):
    if not is_temp_result_id(result_id):
        return None
    return result_id[len(TEMP_RESULT_PREFIX):]


def _key_for_result(result_id):
    return f"{TEMP_RESULT_KEY_PREFIX}{result_id}"


def create_temp_result(result_id, document, ttl_seconds=DEFAULT_TTL_SECONDS):
    redis_client = _get_redis_client()
    doc_to_store = dict(document)
    doc_to_store["_id"] = result_id
    doc_to_store["is_temporary"] = True
    doc_to_store["stored_at"] = datetime.now(timezone.utc).isoformat()
    try:
        redis_client.setex(
            _key_for_result(result_id),
            int(ttl_seconds),
            json.dumps(doc_to_store, default=str),
        )
    except RedisError:
        return None
    return result_id


def get_temp_result(result_id):
    redis_client = _get_redis_client()
    try:
        raw = redis_client.get(_key_for_result(result_id))
    except RedisError:
        return None
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def get_temp_results(result_ids):
    if not result_ids:
        return {}

    redis_client = _get_redis_client()
    keys = [_key_for_result(result_id) for result_id in result_ids]
    try:
        raw_values = redis_client.mget(keys)
    except RedisError:
        return {}

    records_by_id = {}
    for result_id, raw in zip(result_ids, raw_values):
        if raw is None:
            continue
        try:
            records_by_id[result_id] = json.loads(raw)
        except json.JSONDecodeError:
            continue

    return records_by_id


def update_temp_result(result_id, updates, ttl_seconds=DEFAULT_TTL_SECONDS):
    redis_client = _get_redis_client()
    key = _key_for_result(result_id)
    try:
        existing = redis_client.get(key)
    except RedisError:
        return None
    if existing is None:
        return None

    try:
        current = json.loads(existing)
    except json.JSONDecodeError:
        return None

    for key_name, value in updates.items():
        current[key_name] = value

    try:
        remaining_ttl = redis_client.ttl(key)
        ttl_to_use = remaining_ttl if remaining_ttl and remaining_ttl > 0 else int(ttl_seconds)
        redis_client.setex(key, int(ttl_to_use), json.dumps(current, default=str))
    except RedisError:
        return None

    return result_id


def delete_temp_result(result_id):
    redis_client = _get_redis_client()
    try:
        return redis_client.delete(_key_for_result(result_id))
    except RedisError:
        return 0
