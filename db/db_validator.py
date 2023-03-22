from db.schema.files import schema_files
from db.schema.results import schema_results

def db_schema_validator(db):
    if 'Files' not in db.list_collection_names():
        db.create_collection('Files')
    elif 'Results' not in db.list_collection_names():
        db.create_collection('Results')

    db.command('collMod', 'Files', validator=schema_files)
    db.command('collMod', 'Results', validator=schema_results)

