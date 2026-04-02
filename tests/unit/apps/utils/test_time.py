import sys
import os

# apps/ uses relative imports like `from utils.i18n import t`
# so apps/ must be in sys.path when running from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../apps"))

from apps.utils.time import format_remaining_time
import pytest


pytestmark = pytest.mark.unit


# --- Hours ---

def test_format_remaining_time_hours_en():
    assert format_remaining_time(3600, "en") == "~1 hr remaining"


def test_format_remaining_time_hours_fr():
    assert format_remaining_time(3600, "fr") == "~1 h restantes"


def test_format_remaining_time_hours_rounds_down():
    # 7200s = 2h exactly
    assert format_remaining_time(7200, "en") == "~2 hr remaining"
    # 7259s = 2h (floor)
    assert format_remaining_time(7259, "en") == "~2 hr remaining"


def test_format_remaining_time_just_below_hour():
    # 3599s should be minutes (59 min)
    result = format_remaining_time(3599, "en")
    assert "59 min" in result


# --- Minutes ---

def test_format_remaining_time_minutes_en():
    assert format_remaining_time(120, "en") == "~2 min remaining"


def test_format_remaining_time_minutes_fr():
    assert format_remaining_time(120, "fr") == "~2 min restantes"


def test_format_remaining_time_minutes_rounds_down():
    # 89s = 1 min (floor)
    assert format_remaining_time(89, "en") == "~1 min remaining"


def test_format_remaining_time_exactly_60():
    assert format_remaining_time(60, "en") == "~1 min remaining"


def test_format_remaining_time_just_below_minute():
    # 59s should be seconds
    result = format_remaining_time(59, "en")
    assert "59 sec" in result


# --- Seconds ---

def test_format_remaining_time_seconds_en():
    assert format_remaining_time(30, "en") == "~30 sec remaining"


def test_format_remaining_time_seconds_fr():
    assert format_remaining_time(30, "fr") == "~30 sec restantes"


def test_format_remaining_time_zero():
    assert format_remaining_time(0, "en") == "~0 sec remaining"


def test_format_remaining_time_negative_clamps_to_zero():
    assert format_remaining_time(-10, "en") == "~0 sec remaining"


def test_format_remaining_time_one_second():
    assert format_remaining_time(1, "en") == "~1 sec remaining"
