from dotenv import load_dotenv
import os
from flask_pymongo import PyMongo

from db.schema.files import schema_files
from db.schema.results import schema_results

load_dotenv()

def connect_db(app):
    # TODO Add a local and remote database
    mongo_uri = os.environ.get('MONGO_URI')
    db_name = os.environ.get('DB_NAME')

    app.server.config['DB_NAME'] = db_name

    mongo_client = PyMongo(app.server, uri=mongo_uri)

    db_schema_validator(mongo_client.cx[db_name])

    app.logger.info('MongoDB connected')

    return mongo_client

def db_schema_validator(db):
    if 'Files' not in db.list_collection_names():
        db.create_collection('Files')
    elif 'Results' not in db.list_collection_names():
        db.create_collection('Results')

    db.command('collMod', 'Files', validator=schema_files)
    db.command('collMod', 'Results', validator=schema_results)
