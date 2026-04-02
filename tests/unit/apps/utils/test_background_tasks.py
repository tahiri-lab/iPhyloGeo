import sys
import os
import json
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../apps"))

# Prevent DB and aphylogeo imports from running at module level
sys.modules.setdefault("db", MagicMock())
sys.modules.setdefault("db.db_validator", MagicMock())
sys.modules.setdefault("db.controllers.results", MagicMock())
sys.modules.setdefault("aphylogeo", MagicMock())
sys.modules.setdefault("aphylogeo.alignement", MagicMock())
sys.modules.setdefault("aphylogeo.genetic_trees", MagicMock())
sys.modules.setdefault("aphylogeo.params", MagicMock())
sys.modules.setdefault("aphylogeo.utils", MagicMock())
sys.modules.setdefault("utils.utils", MagicMock())
sys.modules.setdefault("utils.mail", MagicMock())
sys.modules.setdefault("enums", MagicMock())

from apps.utils.background_tasks import count_sequences, count_climatic_columns  # noqa: E402
import pytest


pytestmark = pytest.mark.unit


# --- count_sequences ---

def test_count_sequences_dict():
    genetic = {"seq1": "ATCG", "seq2": "GCTA", "seq3": "TTTT"}
    assert count_sequences(genetic) == 3


def test_count_sequences_empty_dict():
    assert count_sequences({}) == 0


def test_count_sequences_none():
    assert count_sequences(None) == 0


def test_count_sequences_fasta_string():
    fasta = ">seq1\nATCG\n>seq2\nGCTA\n"
    assert count_sequences(fasta) == 2


def test_count_sequences_fasta_string_single():
    fasta = ">seq1\nATCG\n"
    assert count_sequences(fasta) == 1


def test_count_sequences_empty_string_returns_one():
    # No '>' found → fallback to 1
    assert count_sequences("no-fasta-content") == 1


def test_count_sequences_unknown_type_returns_one():
    assert count_sequences(42) == 1


# --- count_climatic_columns ---

def test_count_climatic_columns_basic():
    # 1 ID column + 3 feature columns → 3
    df_json = json.dumps({"id": ["a", "b"], "temp": [1, 2], "rain": [3, 4], "wind": [5, 6]})
    assert count_climatic_columns(df_json) == 3


def test_count_climatic_columns_only_id_column():
    df_json = json.dumps({"id": ["a", "b"]})
    assert count_climatic_columns(df_json) == 0


def test_count_climatic_columns_empty_string():
    assert count_climatic_columns("") == 0


def test_count_climatic_columns_none():
    assert count_climatic_columns(None) == 0


def test_count_climatic_columns_invalid_json_returns_default():
    assert count_climatic_columns("not-json") == 2
