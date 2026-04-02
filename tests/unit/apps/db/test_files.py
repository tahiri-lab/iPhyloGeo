import sys
from unittest.mock import MagicMock, patch
import pandas as pd
import pytest

# Mock db.db_validator before importing files.py (it connects to MongoDB at import time)
sys.modules.setdefault("db", MagicMock())
sys.modules.setdefault("db.db_validator", MagicMock())

# files.py reads dotenv_values() at module level — patch it before import so ENV_CONFIG
# is populated and the HOST key exists (avoids KeyError in CI where .env is absent)
with patch("dotenv.dotenv_values", return_value={"HOST": "localhost"}):
    from apps.db.controllers.files import str_csv_to_df, df_to_str_csv, parse_file  # noqa: E402


pytestmark = pytest.mark.unit


# --- str_csv_to_df ---
# Note: uses pd.DataFrame.from_dict on a list of lists, which produces integer
# column keys (0, 1, ...) and skips the first row with df[1:].

def test_str_csv_to_df_basic():
    data = [["name", "age"], ["Alice", 30], ["Bob", 25]]
    df = str_csv_to_df(data)
    assert list(df.columns) == [0, 1]
    assert len(df) == 2


def test_str_csv_to_df_numeric_conversion():
    data = [["value"], ["42"], ["3.14"]]
    df = str_csv_to_df(data)
    assert pd.api.types.is_numeric_dtype(df[0])


def test_str_csv_to_df_non_numeric_stays_string():
    data = [["name"], ["Alice"], ["Bob"]]
    df = str_csv_to_df(data)
    assert df[0].dtype == object


def test_str_csv_to_df_mixed_columns():
    data = [["name", "score"], ["Alice", "95"], ["Bob", "87"]]
    df = str_csv_to_df(data)
    assert pd.api.types.is_numeric_dtype(df[1])
    assert df[0].dtype == object


def test_str_csv_to_df_single_row():
    data = [["x", "y"], [1, 2]]
    df = str_csv_to_df(data)
    assert len(df) == 1


# --- df_to_str_csv ---

def test_df_to_str_csv_basic():
    df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
    result = df_to_str_csv(df)
    assert result[0] == ["name", "age"]
    assert len(result) == 3  # header + 2 rows


def test_df_to_str_csv_single_column():
    df = pd.DataFrame({"value": [1, 2, 3]})
    result = df_to_str_csv(df)
    assert result[0] == ["value"]
    assert len(result) == 4  # header + 3 rows


def test_df_to_str_csv_roundtrip():
    # df_to_str_csv produces [header_row, row1, row2, ...]
    # str_csv_to_df skips row 0 and uses integer column keys
    # so after roundtrip columns are integers, not original names
    df = pd.DataFrame({"name": ["Alice", "Bob"], "score": [95, 87]})
    csv = df_to_str_csv(df)
    df2 = str_csv_to_df(csv)
    assert len(df2) == len(df)
    assert len(df2.columns) == len(df.columns)


# --- parse_file ---

def test_parse_file_with_df():
    file = {"file_name": "data.csv", "type": "csv", "df": {"col": [1, 2]}}
    result = parse_file(file)
    assert result["file_name"] == "data.csv"
    assert result["type"] == "csv"
    assert result["file"] == {"col": [1, 2]}
    assert "created_at" in result
    assert "expired_at" in result


def test_parse_file_with_file():
    file = {"file_name": "seq.fasta", "type": "fasta", "file": ">seq1\nATCG\n"}
    result = parse_file(file)
    assert result["file_name"] == "seq.fasta"
    assert result["file"] == ">seq1\nATCG\n"


def test_parse_file_type_fallback():
    file = {"file_name": "data.csv", "type": None, "df": {}}
    result = parse_file(file)
    assert result["type"] == "unknown"


def test_parse_file_with_last_modified_date():
    file = {"file_name": "data.csv", "type": "csv", "df": {}, "last_modified_date": 0}
    result = parse_file(file)
    assert "last_modified_date" in result


def test_parse_file_expired_at_after_created_at():
    file = {"file_name": "data.csv", "type": "csv", "df": {}}
    result = parse_file(file)
    assert result["expired_at"] > result["created_at"]
