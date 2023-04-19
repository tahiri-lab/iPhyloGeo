# Cron job to delete files from the server when they are expired
from dotenv import load_dotenv, dotenv_values
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

ENV_CONFIG = {}
for key, value in dotenv_values().items():
    ENV_CONFIG[key] = value

COLLECTION_NAMES = ['Files', 'Results']


if __name__ == '__main__':
    # connect to mongo db and get the database
    mongo_client = MongoClient(ENV_CONFIG['MONGO_URI'])
    mongo_client.get_database(ENV_CONFIG['DB_NAME'])

    # go to collection Files and
    for collection_name in COLLECTION_NAMES:
        collection = mongo_client[ENV_CONFIG['DB_NAME']][collection_name]
        expired_files = collection.find({'expired_at': {'$lt': datetime.utcnow()}})
        for expired_file in expired_files:
            collection.delete_one({'_id': expired_file['_id']})
