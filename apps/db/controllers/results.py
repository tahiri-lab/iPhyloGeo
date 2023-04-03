from bson.objectid import ObjectId
from datetime import datetime, timedelta

from db.db_validator import results_db

def get_results(ids):
    res = results_db.find({'_id': {'$in': [ObjectId(id) for id in ids]}})
    return list(res) # return a list of dictionaries to force convert the pymongo cursor to a list
def get_result(id):
    res = results_db.find_one({'_id': ObjectId(id)})
    return res

# TODO: remove this function just for testing
def get_all_results():
    res = results_db.find({})
    return list(res)

def create_result(result):
    document = parse_result(result)
    document['status'] = 'pending'
    document['created_at'] = datetime.utcnow()
    document['expired_at'] = datetime.utcnow() + timedelta(days=14)
    document['name'] = 'result'

    res = results_db.insert_one(document)
    return str(res.inserted_id)

def update_result(result):
    document = parse_result(result)
    return results_db.update_one({'_id': document['_id']}, {'$set': document})

def parse_result(result):
    document = {}
    if '_id' in result:
        document['_id'] = ObjectId(result['_id'])
    if 'climatic_files_id' in result:
        document['climatic_files_id'] = ObjectId(result['climatic_files_id'])
    if 'genetic_files_id' in result:
        document['genetic_files_id'] = ObjectId(result['genetic_files_id'])
    if 'climatic_params' in result:
        document['climatic_params'] = result['climatic_params']
    if 'climatic_trees' in result:
        climatic_trees = {}
        for key, value in result['climatic_trees'].items():
            climatic_trees[key] = value.format('newick')
        document['climatic_trees'] = climatic_trees
    if 'genetic_trees' in result:
        genetic_trees = {}
        for key, value in result['genetic_trees'].items():
            genetic_trees[key] = value.format('newick')
        document['genetic_trees'] = genetic_trees
    if 'genetic_params' in result:
        document['genetic_params'] = result['genetic_params']
    if 'msaSet' in result:
        msaSet = {}
        for key, value in result['msaSet'].items():
            msaSet[key] = [seq.format("fasta") for seq in value]
        document['msaSet'] = msaSet
    if 'status' in result:
        document['status'] = result['status']
    if 'output' in result:
        document['output'] = result['output']
    if 'name' in result:
        document['name'] = result['name']

    return document

def parse_document(document):
    pass
