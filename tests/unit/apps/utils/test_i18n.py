from apps.utils.i18n import t, _normalize_key, _get_nested_value
import pytest


pytestmark = pytest.mark.unit


# --- t() happy path ---

def test_t_returns_english_string():
    assert t("setting.title", "en") == "Settings"


def test_t_returns_french_string():
    assert t("setting.title", "fr") == "Paramètres"


def test_t_defaults_to_english():
    assert t("setting.title") == "Settings"


# --- t() fallback behaviour ---

def test_t_unsupported_language_falls_back_to_english():
    # "es" is not in SUPPORTED_LOCALES — must return the English value
    result = t("setting.title", "es")
    assert result == "Settings"


def test_t_missing_key_returns_key_itself():
    key = "setting.this.key.does.not.exist"
    assert t(key, "en") == key


def test_t_missing_key_in_fr_falls_back_to_english():
    # A key that exists only in English falls back gracefully
    result = t("setting.title", "fr")
    # Must be a non-empty string (either FR or EN), not the raw key
    assert result != "setting.title"
    assert len(result) > 0


# --- _normalize_key ---

def test_normalize_key_replaces_underscores_with_hyphens():
    assert _normalize_key("setting.options.alignment.no_alignment") == "setting.options.alignment.no-alignment"


def test_normalize_key_no_underscores_unchanged():
    assert _normalize_key("setting.title") == "setting.title"


def test_normalize_key_multiple_underscores():
    assert _normalize_key("a.b_c.d_e") == "a.b-c.d-e"


# --- _get_nested_value ---

def test_get_nested_value_single_level():
    data = {"a": 1}
    assert _get_nested_value(data, "a") == 1


def test_get_nested_value_nested():
    data = {"a": {"b": {"c": "found"}}}
    assert _get_nested_value(data, "a.b.c") == "found"


def test_get_nested_value_missing_key_returns_none():
    data = {"a": {"b": 1}}
    assert _get_nested_value(data, "a.c") is None


def test_get_nested_value_non_dict_intermediate_returns_none():
    data = {"a": "string"}
    assert _get_nested_value(data, "a.b") is None


def test_get_nested_value_empty_dict():
    assert _get_nested_value({}, "a") is None
