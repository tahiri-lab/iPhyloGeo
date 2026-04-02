from apps.components.email_input import validate_email, get_button_id, get_error_id
import pytest


pytestmark = pytest.mark.unit


# --- validate_email ---

def test_valid_email():
    assert validate_email("user@example.com") is True


def test_valid_email_with_subdomain():
    assert validate_email("user@mail.example.com") is True


def test_valid_email_with_plus():
    assert validate_email("user+tag@example.com") is True


def test_valid_email_with_dots_in_name():
    assert validate_email("first.last@example.com") is True


def test_valid_email_with_numbers():
    assert validate_email("user123@example123.com") is True


def test_invalid_email_missing_at():
    assert validate_email("userexample.com") is False


def test_invalid_email_missing_domain():
    assert validate_email("user@") is False


def test_invalid_email_missing_tld():
    assert validate_email("user@example") is False


def test_invalid_email_empty_string():
    assert validate_email("") is False


def test_invalid_email_none():
    assert validate_email(None) is False


def test_invalid_email_only_at():
    assert validate_email("@") is False


def test_invalid_email_spaces():
    assert validate_email("user @example.com") is False


def test_invalid_email_double_at():
    assert validate_email("user@@example.com") is False


# --- get_button_id ---

def test_get_button_id_basic():
    assert get_button_id("email-input") == "email-input-button"


def test_get_button_id_any_string():
    assert get_button_id("my-id") == "my-id-button"


# --- get_error_id ---

def test_get_error_id_basic():
    assert get_error_id("email-input") == "email-input-error"


def test_get_error_id_any_string():
    assert get_error_id("my-id") == "my-id-error"
