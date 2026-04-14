from apps.db.controllers.temp_results import (
    is_temp_result_id,
    build_temp_result_id,
    extract_temp_token,
)
import pytest


pytestmark = pytest.mark.unit


# --- is_temp_result_id ---

def test_is_temp_result_id_valid():
    assert is_temp_result_id("tmp_abc123") is True


def test_is_temp_result_id_without_prefix():
    assert is_temp_result_id("abc123") is False


def test_is_temp_result_id_empty_string():
    assert is_temp_result_id("") is False


def test_is_temp_result_id_none():
    assert is_temp_result_id(None) is False


def test_is_temp_result_id_integer():
    assert is_temp_result_id(123) is False


def test_is_temp_result_id_only_prefix():
    assert is_temp_result_id("tmp_") is True


def test_is_temp_result_id_similar_but_wrong_prefix():
    assert is_temp_result_id("temp_abc123") is False


# --- build_temp_result_id ---

def test_build_temp_result_id_basic():
    assert build_temp_result_id("abc123") == "tmp_abc123"


def test_build_temp_result_id_empty_token():
    assert build_temp_result_id("") == "tmp_"


def test_build_temp_result_id_result_is_recognized():
    result_id = build_temp_result_id("mytoken")
    assert is_temp_result_id(result_id) is True


# --- extract_temp_token ---

def test_extract_temp_token_valid():
    assert extract_temp_token("tmp_abc123") == "abc123"


def test_extract_temp_token_roundtrip():
    token = "mytoken123"
    result_id = build_temp_result_id(token)
    assert extract_temp_token(result_id) == token


def test_extract_temp_token_invalid_id():
    assert extract_temp_token("abc123") is None


def test_extract_temp_token_none():
    assert extract_temp_token(None) is None


def test_extract_temp_token_empty_string():
    assert extract_temp_token("") is None


def test_extract_temp_token_only_prefix():
    assert extract_temp_token("tmp_") == ""
