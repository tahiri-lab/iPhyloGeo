import sys
import os
import pytest

# Make apps/ importable as root so that internal imports like
# `from db.db_validator import results_db` resolve correctly in integration tests.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps"))


@pytest.fixture(autouse=True)
def reset_db_modules():
    """
    Unit tests register db.* as MagicMocks via sys.modules.setdefault() at
    collection time. This fixture purges those mocked entries before each
    integration test so the real implementations are imported instead.
    """
    to_purge = [
        key for key in list(sys.modules)
        if key == "db"
        or key.startswith("db.")
        or key == "apps.db"
        or key.startswith("apps.db.")
    ]
    for mod in to_purge:
        sys.modules.pop(mod, None)
    yield
