import json
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path

from bson.objectid import ObjectId
from db.db_validator import results_db
from db.controllers import temp_results
from dotenv import dotenv_values, load_dotenv

load_dotenv()

ENV_CONFIG = {}
for key, value in dotenv_values().items():
    ENV_CONFIG[key] = value

if ENV_CONFIG["HOST"] == "local":
    if not os.path.exists("result"):
        os.makedirs("result")


def _is_temp_result_id(result_id):
    return temp_results.is_temp_result_id(result_id)


def is_temp_storage_available():
    return temp_results.is_available()


def _build_temp_result_document(result):
    created_at = datetime.utcnow()
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

    for result_id in ids:
        if _is_temp_result_id(result_id):
            temp_record = temp_results.get_temp_result(result_id)
            if temp_record:
                records_by_id[str(temp_record.get("_id", result_id))] = temp_record
        else:
            persistent_ids.append(result_id)

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
            res = results_db.find({"_id": {"$in": [ObjectId(id) for id in persistent_ids]}})
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
        with open(Path("result") / (str(id) + ".json")) as f:
            return json.load(f)

    res = results_db.find_one({"_id": ObjectId(id)})
    return res


def get_all_results():
    if ENV_CONFIG["HOST"] != "local":
        return
    results = []
    for file in os.listdir("result"):
        with open(Path("result") / file) as f:
            results.append(json.load(f))
    return results


def delete_result(id):
    if _is_temp_result_id(id):
        return temp_results.delete_temp_result(id)

    if ENV_CONFIG["HOST"] == "local":
        # look for id in the results directory
        os.remove(Path("result") / (str(id) + ".json"))
        return

    return results_db.delete_one({"_id": ObjectId(id)})


def create_result(result):

    document = parse_result(result)
    document["status"] = result["status"]
    document["created_at"] = datetime.utcnow()
    document["expired_at"] = datetime.utcnow() + timedelta(days=14)
    document["name"] = result["name"]
    document["result_type"] = result["result_type"]

    if ENV_CONFIG["HOST"] == "local":
        # save the file to the results directory and return the id
        id = ObjectId()
        document["_id"] = id
        with open(Path("result") / (str(id) + ".json"), "w") as f:
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
        with open(Path("result") / (str(document["_id"]) + ".json"), "r+") as f:
            data = json.load(f)
            f.close()

        for key, value in document.items():
            data[key] = value
        with open(Path("result") / (str(document["_id"]) + ".json"), "w") as f:
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
