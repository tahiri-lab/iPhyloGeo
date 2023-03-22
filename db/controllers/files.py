from app import files_db

def get_all_files():
    return files_db.find()