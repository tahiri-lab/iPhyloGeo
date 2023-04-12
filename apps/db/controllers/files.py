from datetime import datetime, timedelta
from bson.objectid import ObjectId
import pandas as pd
from Bio import SeqIO
from io import StringIO
from db.db_validator import files_db
import json


def get_all_files():
    res = files_db.find({}, {'_id': 1, 'file_name': 1})
    return list(res)  # return a list of dictionaries to force convert the pymongo cursor to a list


def save_files(files):
    if not isinstance(files, list):
        files = [files]

    results = []
    for file in files:
        parsed_file = parse_file(file)
        if isinstance(parsed_file['file'], str):
            parsed_file['file'] = json.loads(parsed_file['file'])

        # save the file to the database and return the id
        result = files_db.insert_one(parsed_file)
        results.append(str(result.inserted_id))

    return results[0] if len(results) == 1 else results


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
        'type': file['type'],
        'created_at': datetime.now(),
        'expired_at': datetime.now() + timedelta(days=14),
    }

    if 'df' in file:
        result['file'] = file['df']

    elif 'file' in file:
        # fasta format SeqIO
        result['file'] = file['file']

    if 'last_modified_date' in file:
        result['last_modified_date'] = datetime.fromtimestamp(file['last_modified_date'])

    return result

# reverse so we need to take a document and parse it to the same format as the file


def parse_document(document):
    """Parse the document to a proper format to be returned to the user.

    Args:
        document (dict): The document to be parsed.
    """
    result = {
        'file_name': document['file_name'],
        'created_at': document['created_at'],
        'expired_at': document['expired_at']
    }

    if document['file_name'].endswith('.fasta'):
        fasta_str = ''
        for key, seq in document['file'].items():
            fasta_str += f'>{key}\n{seq}\n'

        result['file'] = SeqIO.FastaIO.FastaIterator(StringIO(fasta_str))

    elif document['file_name'].endswith('.csv') or document['file_name'].endswith('.xlsx'):
        result['df'] = str_csv_to_df(document['file'])

    if 'last_modified_date' in document:
        result['last_modified_date'] = document['last_modified_date']

    return result


def df_to_str_csv(df):
    return [list(df.columns)] + df.values.tolist()


def fasta_to_str(fasta):
    result = SeqIO.to_dict(fasta)
    for key in result:
        result[key] = str(result[key].seq)
    return result


def str_csv_to_df(str_csv):
    df = pd.DataFrame(str_csv)
    df = df.rename(columns=df.iloc[0]).drop(df.index[0])

    # convert all value to numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    return df
