import sys
import os

# Make apps/ importable as root so that internal imports like
# `from db.db_validator import results_db` resolve correctly in integration tests.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps"))
