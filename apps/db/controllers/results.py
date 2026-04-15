import secrets
from datetime import datetime, timedelta, timezone

from bson.objectid import ObjectId
from db.db_validator import results_db
from db.controllers import temp_results


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
        if str(result_id) in records_by_id:
            ordered_results.append(records_by_id[str(result_id)])

    return ordered_results


def get_result(id):
    if _is_temp_result_id(id):
        return temp_results.get_temp_result(id)

    res = results_db.find_one({"_id": ObjectId(id)})
    return res


def get_all_results():
    return list(results_db.find())


def delete_result(id):
    if _is_temp_result_id(id):
        return temp_results.delete_temp_result(id)

    return results_db.delete_one({"_id": ObjectId(id)})


def create_result(result):

    document = parse_result(result)
    document["status"] = result["status"]
    now_utc = datetime.now(timezone.utc)
    document["created_at"] = now_utc
    document["expired_at"] = now_utc + timedelta(days=14)
    document["name"] = result["name"]
    document["result_type"] = result["result_type"]

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
