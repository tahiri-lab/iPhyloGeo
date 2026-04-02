import pytest
from bson.objectid import ObjectId
from db.db_validator import files_db
from apps.db.controllers.files import save_files

pytestmark = pytest.mark.integration


def _mongo_available():
    try:
        files_db.find_one({})
        return True
    except Exception:
        return False


def _minimal_csv_file(**kwargs):
    base = {
        "file_name": "test.csv",
        "type": "climatic",
        "df": [["col1", "col2"], [1, 2], [3, 4]],
    }
    base.update(kwargs)
    return base


def test_save_file_inserts_into_mongodb():
    """save_files() must persist the document and return a usable string ID."""
    if not _mongo_available():
        pytest.skip("MongoDB is not available")

    file_id = None
    try:
        file_id = save_files(_minimal_csv_file())
        assert file_id is not None

        doc = files_db.find_one({"_id": ObjectId(file_id)})
        assert doc is not None
        assert doc["file_name"] == "test.csv"
        assert doc["type"] == "climatic"
        assert "created_at" in doc
        assert "expired_at" in doc
        assert doc["expired_at"] > doc["created_at"]
    finally:
        if file_id:
            try:
                files_db.delete_one({"_id": ObjectId(file_id)})
            except Exception:
                pass


def test_save_multiple_files_returns_list_of_ids():
    """save_files() with a list of 2 files must return a list of 2 IDs."""
    if not _mongo_available():
        pytest.skip("MongoDB is not available")

    ids = []
    try:
        ids = save_files([
            _minimal_csv_file(file_name="a.csv"),
            _minimal_csv_file(file_name="b.csv"),
        ])
        assert isinstance(ids, list)
        assert len(ids) == 2

        for file_id in ids:
            doc = files_db.find_one({"_id": ObjectId(file_id)})
            assert doc is not None
    finally:
        for file_id in ids:
            try:
                files_db.delete_one({"_id": ObjectId(file_id)})
            except Exception:
                pass
