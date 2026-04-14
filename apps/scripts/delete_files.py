# Cron job to delete files from the server when they are expired
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

from dotenv import dotenv_values, load_dotenv
from pymongo import MongoClient

APPS_DIR = Path(__file__).resolve().parents[1]
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

from utils.time import to_utc_datetime

load_dotenv()

ENV_CONFIG = {}
for key, value in dotenv_values().items():
    ENV_CONFIG[key] = value

COLLECTION_NAMES = ["Files", "Results"]
LOCAL_COLLECTION_PATHS = {"Files": Path("files"), "Results": Path("result")}


def _cleanup_local_collection(path, now_utc):
    if not path.exists():
        return 0

    deleted_count = 0
    for item in path.glob("*.json"):
        try:
            with open(item) as local_file:
                payload = json.load(local_file)
        except (json.JSONDecodeError, OSError):
            continue

        expired_at = to_utc_datetime(payload.get("expired_at"))
        if expired_at and expired_at < now_utc:
            item.unlink(missing_ok=True)
            deleted_count += 1

    return deleted_count


def _cleanup_mongo_collections(now_utc):
    mongo_client = MongoClient(ENV_CONFIG["MONGO_URI"])
    mongo_client.get_database(ENV_CONFIG["DB_NAME"])

    deleted_counts = {}
    for collection_name in COLLECTION_NAMES:
        collection = mongo_client[ENV_CONFIG["DB_NAME"]][collection_name]
        deleted_result = collection.delete_many({"expired_at": {"$lt": now_utc}})
        deleted_counts[collection_name] = deleted_result.deleted_count

    return deleted_counts


def _cleanup_local_collections(now_utc):
    deleted_counts = {}
    for collection_name, path in LOCAL_COLLECTION_PATHS.items():
        deleted_counts[collection_name] = _cleanup_local_collection(path, now_utc)
    return deleted_counts


if __name__ == "__main__":
    now_utc = datetime.now(timezone.utc)

    if ENV_CONFIG["HOST"] == "local":
        deleted_counts = _cleanup_local_collections(now_utc)
        print(f"[cleanup] local mode - deleted {deleted_counts}")
    else:
        deleted_counts = _cleanup_mongo_collections(now_utc)
        print(f"[cleanup] mongo mode - deleted {deleted_counts}")
