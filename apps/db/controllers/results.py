import json
import os
import tempfile
from datetime import datetime, timedelta
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bson.objectid import ObjectId
from db.db_validator import results_db
from db.controllers import temp_results
from dotenv import dotenv_values, load_dotenv

load_dotenv()

ENV_CONFIG = {}
for key, value in dotenv_values().items():
    ENV_CONFIG[key] = value

RESULT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "result"

if ENV_CONFIG["HOST"] == "local":
    if not RESULT_DIR.exists():
        RESULT_DIR.mkdir(parents=True)


def _is_temp_result_id(result_id):
    return temp_results.is_temp_result_id(result_id)


def is_temp_storage_available():
    return temp_results.is_available()


def _build_temp_result_document(result):
    created_at = datetime.now(timezone.utc)
    ttl_seconds = temp_results.get_default_ttl_seconds()
    document = {
        "status": result["status"],
        "created_at": created_at,
        "expired_at": created_at + timedelta(seconds=ttl_seconds),
        "name": result["name"],
        "result_type": result["result_type"],
    }
    if "climatic_params" in result:
        document["climatic_params"] = result["climatic_params"]
    if "genetic_params" in result:
        document["genetic_params"] = result["genetic_params"]
    return document


def get_results(ids):
    records_by_id = {}
    persistent_ids = []
    temp_ids = []

    for result_id in ids:
        if _is_temp_result_id(result_id):
            temp_ids.append(result_id)
        else:
            persistent_ids.append(result_id)

    if temp_ids:
        temp_records = temp_results.get_temp_results(temp_ids)
        for result_id in temp_ids:
            temp_record = temp_records.get(result_id)
            if temp_record:
                records_by_id[str(temp_record.get("_id", result_id))] = temp_record

    if persistent_ids:
        if ENV_CONFIG["HOST"] == "local":
            for result_id in persistent_ids:
                try:
                    with open(Path("result") / (str(result_id) + ".json")) as f:
                        result_doc = json.load(f)
                    records_by_id[str(result_doc.get("_id", result_id))] = result_doc
                except FileNotFoundError:
                    continue
        else:
            valid_object_ids = []
            for result_id in persistent_ids:
                if ObjectId.is_valid(str(result_id)):
                    valid_object_ids.append(ObjectId(str(result_id)))

            if valid_object_ids:
                res = results_db.find({"_id": {"$in": valid_object_ids}})
                for result_doc in res:
                    records_by_id[str(result_doc["_id"])] = result_doc

    ordered_results = []
    for result_id in ids:
        if result_id in records_by_id:
            ordered_results.append(records_by_id[result_id])

    return ordered_results


def get_result(id):
    if _is_temp_result_id(id):
        return temp_results.get_temp_result(id)

    if ENV_CONFIG["HOST"] == "local":
        # look for id in the results directory
        with open(RESULT_DIR / (str(id) + ".json")) as f:
            return json.load(f)

    res = results_db.find_one({"_id": ObjectId(id)})
    return res


def get_all_results():
    if ENV_CONFIG["HOST"] != "local":
        return
    results = []
    for file in os.listdir(RESULT_DIR):
        with open(RESULT_DIR / file) as f:
            results.append(json.load(f))
    return results


def delete_result(id):
    if _is_temp_result_id(id):
        return temp_results.delete_temp_result(id)

    if ENV_CONFIG["HOST"] == "local":
        # look for id in the results directory
        os.remove(RESULT_DIR / (str(id) + ".json"))
        return

    return results_db.delete_one({"_id": ObjectId(id)})


def create_result(result):

    document = parse_result(result)
    document["status"] = result["status"]
    now_utc = datetime.now(timezone.utc)
    document["created_at"] = now_utc
    document["expired_at"] = now_utc + timedelta(days=14)
    document["name"] = result["name"]
    document["result_type"] = result["result_type"]

    if ENV_CONFIG["HOST"] == "local":
        # save the file to the results directory and return the id
        id = ObjectId()
        document["_id"] = id
        with open(RESULT_DIR / (str(id) + ".json"), "w") as f:
            f.write(json.dumps(document, indent=4, sort_keys=True, default=str))
        return str(id)

    res = results_db.insert_one(document)
    return str(res.inserted_id)


def create_temp_result(result):
    document = _build_temp_result_document(result)
    token = secrets.token_urlsafe(18)
    temp_id = temp_results.build_temp_result_id(token)
    return temp_results.create_temp_result(temp_id, document)


def update_result(result):
    if _is_temp_result_id(result.get("_id")):
        document = parse_result(result)
        return temp_results.update_temp_result(document["_id"], document)

    document = parse_result(result)

    if ENV_CONFIG["HOST"] == "local":
        # save the file to the results directory and return the id
        with open(RESULT_DIR / (str(document["_id"]) + ".json"), "r+") as f:
            data = json.load(f)
            f.close()

        for key, value in document.items():
            data[key] = value
        with open(RESULT_DIR / (str(document["_id"]) + ".json"), "w") as f:
            f.write(json.dumps(data, indent=4, sort_keys=True, default=str))
        return str(document["_id"])

    return results_db.update_one({"_id": document["_id"]}, {"$set": document})


def parse_result(result):
    document = {}
    if "_id" in result:
        if _is_temp_result_id(result["_id"]):
            document["_id"] = result["_id"]
        else:
            document["_id"] = ObjectId(result["_id"])
    if "climatic_files_id" in result:
        document["climatic_files_id"] = ObjectId(result["climatic_files_id"])
    if "genetic_files_id" in result:
        document["genetic_files_id"] = ObjectId(result["genetic_files_id"])
    if "aligned_genetic_files_id" in result:
        document["aligned_genetic_files_id"] = ObjectId(result["aligned_genetic_files_id"])
    if "genetic_tree_files_id" in result:
        document["genetic_tree_files_id"] = ObjectId(result["genetic_tree_files_id"])
    if "climatic_params" in result:
        document["climatic_params"] = result["climatic_params"]
    if "climatic_trees" in result:
        climatic_trees = {}
        for key, value in result["climatic_trees"].items():
            climatic_trees[key] = value.format("newick")
        document["climatic_trees"] = climatic_trees
    if "genetic_trees" in result:
        genetic_trees = {}
        for key, value in result["genetic_trees"].items():
            genetic_trees[key] = value.format("newick")
        document["genetic_trees"] = genetic_trees
    if "genetic_params" in result:
        document["genetic_params"] = result["genetic_params"]
    if "msaSet" in result:
        msaSet = {}
        for key, value in result["msaSet"].items():
            msaSet[key] = [seq.format("fasta") for seq in value]
        document["msaSet"] = msaSet
    if "status" in result:
        document["status"] = result["status"]
    if "output" in result:
        document["output"] = result["output"]
    if "name" in result:
        document["name"] = result["name"]

    return document


def parse_document(document):
    pass


PENDING_STATUSES = {"pending", "running", "queued", "climatic_trees", "alignement", "alignment", "genetic_trees", "output"}


def mark_stuck_results_as_error():
    """
    On app startup, mark any results stuck in a non-terminal state as 'error'.
    These were interrupted by an app crash or restart.
    """
    _STARTUP_SENTINEL = Path(tempfile.gettempdir()) / "iphylogeo_startup_done"

    if _STARTUP_SENTINEL.exists():
        return
    _STARTUP_SENTINEL.touch()
    if ENV_CONFIG["HOST"] == "local":
        for file in os.listdir(RESULT_DIR):
            filepath = RESULT_DIR / file
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                if data.get("status", "").lower() in PENDING_STATUSES:
                    data["status"] = "error"
                    with open(filepath, "w") as f:
                        f.write(json.dumps(data, indent=4, sort_keys=True, default=str))
                    print(f"[Startup] Marked stuck result {file} as error")
            except Exception as e:
                print(f"[Startup] Could not process result file {file}: {e}")
        return

    try:
        results_db.update_many(
            {"status": {"$in": list(PENDING_STATUSES)}},
            {"$set": {"status": "error"}},
        )
        print("[Startup] Marked all stuck results as error")
    except Exception as e:
        print(f"[Startup] Could not mark stuck results: {e}")
