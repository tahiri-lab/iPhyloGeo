import json
from datetime import datetime

from dotenv import dotenv_values, load_dotenv
from redis import Redis

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
    return result_id[len(TEMP_RESULT_PREFIX) :]


def _key_for_result(result_id):
    return f"{TEMP_RESULT_KEY_PREFIX}{result_id}"


def create_temp_result(result_id, document, ttl_seconds=DEFAULT_TTL_SECONDS):
    redis_client = _get_redis_client()
    doc_to_store = dict(document)
    doc_to_store["_id"] = result_id
    doc_to_store["is_temporary"] = True
    doc_to_store["stored_at"] = datetime.utcnow().isoformat()
    redis_client.setex(
        _key_for_result(result_id),
        int(ttl_seconds),
        json.dumps(doc_to_store, default=str),
    )
    return result_id


def get_temp_result(result_id):
    redis_client = _get_redis_client()
    raw = redis_client.get(_key_for_result(result_id))
    if raw is None:
        return None
    return json.loads(raw)


def update_temp_result(result_id, updates, ttl_seconds=DEFAULT_TTL_SECONDS):
    redis_client = _get_redis_client()
    key = _key_for_result(result_id)
    existing = redis_client.get(key)
    if existing is None:
        return None

    current = json.loads(existing)
    for key_name, value in updates.items():
        current[key_name] = value

    remaining_ttl = redis_client.ttl(key)
    ttl_to_use = remaining_ttl if remaining_ttl and remaining_ttl > 0 else int(ttl_seconds)
    redis_client.setex(key, int(ttl_to_use), json.dumps(current, default=str))
    return result_id


def delete_temp_result(result_id):
    redis_client = _get_redis_client()
    return redis_client.delete(_key_for_result(result_id))
