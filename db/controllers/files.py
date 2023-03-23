from datetime import datetime, timedelta
from bson.objectid import ObjectId
import pandas as pd

from app import app, files_db


def get_all_files():
    res = files_db.find({}, {'_id': 1, 'file_name': 1})
    return list(res) # return a list of dictionaries to force convert the pymongo cursor to a list

def save_files(files):
    for file in files:
        parsed_file = parse_file(file)
        files_db.insert_one(parsed_file)

def get_files_by_id(ids):
    if not isinstance(ids, list):
        ids = [ids]
    for id in ids:
        # check if its a objectId
        if not isinstance(id, ObjectId):
            id = ObjectId(id)

    results = files_db.find({'_id': {'$in': ids}})
    results = list(results)

    files = []
    for file in results:
        files.append(parse_document(file))

    return files[0] if len(files) == 1 else files

# utils
def parse_file(file):
    """Parse the file to a proper format to be stored in the database.

    Args:
        file (dict): The file to be parsed.
    """
    result = {
        'file_name': file['file_name'],
        'file': [list(file['df'].columns)] + file['df'].values.tolist(),
        'created_at': datetime.now(),
        'expired_at': datetime.now() + timedelta(days=14),
    }

    if 'last_modified_date' in file:
        result['last_modified_date'] = datetime.fromtimestamp(file['last_modified_date'])

    return result

# reverse so we need to take a document and parse it to the same format as the file
def parse_document(document):
    """Parse the document to a proper format to be returned to the user.

    Args:
        document (dict): The document to be parsed.
    """

    df = pd.DataFrame(document['file'])
    app.logger.info('befor df: {}'.format(df))
    # remove the first row wich is 0 1 2 3 4 ...
    # and the first colum wich is 0 1 2 3 4 ...

    app.logger.info('res df: {}'.format(df))


    result = {
        'file_name': document['file_name'],
        'df': df,
        'created_at': document['created_at'],
        'expired_at': document['expired_at'],
    }



    if 'last_modified_date' in document:
        result['last_modified_date'] = document['last_modified_date']

    return result






"""
[
['OM739053', 4.7, 14.803333333333336, 6.713333333333334, 1.623333333333333, 2.553333333333333],
['OU471040', 1.46, 4.19, 4.516666666666667, 0.12, 3.043333333333333],
['ON129429', 6.8933333333333335, 27.066666666666663, 15.156666666666665, 0.7166666666666667, 1.36],
['OL989074', 4.6466666666666665, 26.12, 18.10666666666668, 0.4733333333333334, 5.66],
['ON134852', 6.8400000000000025, 16.973333333333333, 5.576666666666667, 0.4966666666666666, 4.666666666666667]
]

[['OM739053', 'OU471040', 'ON129429', 'OL989074', 'ON134852'],
[4.7, 1.46, 6.8933333333333335, 4.6466666666666665, 6.8400000000000025],
...]

[
['OM739053', 4.7, 14.803333333333336, 6.713333333333334, 1.623333333333333, 2.553333333333333],
['OU471040', 1.46, 4.19, 4.516666666666667, 0.12, 3.043333333333333],
['ON129429', 6.8933333333333335, 27.066666666666663, 15.156666666666665, 0.7166666666666667, 1.36],
['OL989074', 4.6466666666666665, 26.12, 18.10666666666668, 0.4733333333333334, 5.66],
['ON134852', 6.8400000000000025, 16.973333333333333, 5.576666666666667, 0.4966666666666666, 4.666666666666667]
]

"""