from dotenv import load_dotenv
import os
from pymongo import MongoClient
from db.schema.files import schema_files
from db.schema.results import schema_results

load_dotenv()

def connect_db():
    # TODO Add a local and remote database
    mongo_uri = os.environ.get('MONGO_URI')
    db_name = os.environ.get('DB_NAME')
    mongo_client = MongoClient(mongo_uri)
    db_schema_validator(mongo_client.get_database(db_name))

    return mongo_client

def db_schema_validator(db):
    if 'Files' not in db.list_collection_names():
        db.create_collection('Files')
    elif 'Results' not in db.list_collection_names():
        db.create_collection('Results')

    db.command('collMod', 'Files', validator=schema_files)
    db.command('collMod', 'Results', validator=schema_results)


mongo_client = connect_db()
db_name = os.environ.get('DB_NAME')

files_db = mongo_client[db_name].Files
results_db = mongo_client[db_name].Results
