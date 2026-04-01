from apps.components.email_input import get_button_id, get_error_id, validate_email
import pytest


pytestmark = pytest.mark.unit


def test_validate_email_accepts_valid_email():
    assert validate_email("alice@example.com") is True


def test_validate_email_rejects_invalid_email():
    assert validate_email("not-an-email") is False
    assert validate_email("") is False
    assert validate_email(None) is False


def test_id_helpers_are_deterministic():
    assert get_button_id("foo") == "foo-button"
    assert get_error_id("foo") == "foo-error"
