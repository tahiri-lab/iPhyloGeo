from bson.objectid import ObjectId

from db.db_validator import results_db

def get_results(ids):
    res = results_db.find({'_id': {'$in': [ObjectId(id) for id in ids]}})
    return list(res) # return a list of dictionaries to force convert the pymongo cursor to a list
