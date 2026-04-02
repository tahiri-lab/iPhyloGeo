import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock

# Prevent heavy dependencies from connecting/importing at module level
sys.modules.setdefault("db", MagicMock())
sys.modules.setdefault("db.db_validator", MagicMock())
sys.modules.setdefault("db.controllers.files", MagicMock())
sys.modules.setdefault("db.controllers.results", MagicMock())
sys.modules.setdefault("Bio", MagicMock())
sys.modules.setdefault("Bio.SeqIO", MagicMock())
sys.modules.setdefault("Bio.Seq", MagicMock())
sys.modules.setdefault("Bio.SeqRecord", MagicMock())
sys.modules.setdefault("Bio.Align", MagicMock())
sys.modules.setdefault("numpy", MagicMock())
sys.modules.setdefault("scipy", MagicMock())
sys.modules.setdefault("scipy.spatial", MagicMock())
sys.modules.setdefault("scipy.spatial.distance", MagicMock())
sys.modules.setdefault("aphylogeo", MagicMock())
sys.modules.setdefault("aphylogeo.utils", MagicMock())
sys.modules.setdefault("aphylogeo.alignement", MagicMock())
sys.modules.setdefault("aphylogeo.params", MagicMock())
sys.modules.setdefault("dash", MagicMock())
sys.modules.setdefault("dash.dcc", MagicMock())
sys.modules.setdefault("dash.html", MagicMock())

from apps.utils.utils import format_card_date, to_datetime_utc, make_cookie, get_table_styles  # noqa: E402
import pytest


pytestmark = pytest.mark.unit


# --- format_card_date ---

def test_format_card_date_none():
    assert format_card_date(None) is None


def test_format_card_date_datetime_object():
    dt = datetime(2024, 3, 15)
    assert format_card_date(dt) == "15/03/2024"


def test_format_card_date_iso_string():
    assert format_card_date("2024-03-15T10:30:00") == "15/03/2024"


def test_format_card_date_iso_string_with_z():
    assert format_card_date("2024-03-15T00:00:00Z") == "15/03/2024"


def test_format_card_date_invalid_string_returns_original():
    assert format_card_date("not-a-date") == "not-a-date"


def test_format_card_date_non_string_non_datetime():
    # Fallback: str(value)
    assert format_card_date(42) == "42"


# --- to_datetime_utc ---

def test_to_datetime_utc_none_returns_min():
    result = to_datetime_utc(None)
    assert result == datetime.min.replace(tzinfo=timezone.utc)


def test_to_datetime_utc_naive_datetime_gets_utc():
    dt = datetime(2024, 6, 1, 12, 0, 0)
    result = to_datetime_utc(dt)
    assert result.tzinfo == timezone.utc
    assert result.year == 2024


def test_to_datetime_utc_aware_datetime_converted():
    from datetime import timedelta
    tz_plus2 = timezone(timedelta(hours=2))
    dt = datetime(2024, 6, 1, 14, 0, 0, tzinfo=tz_plus2)
    result = to_datetime_utc(dt)
    assert result.tzinfo == timezone.utc
    assert result.hour == 12  # 14:00+02:00 -> 12:00 UTC


def test_to_datetime_utc_iso_string():
    result = to_datetime_utc("2024-06-01T12:00:00")
    assert result.year == 2024
    assert result.tzinfo == timezone.utc


def test_to_datetime_utc_iso_string_with_z():
    result = to_datetime_utc("2024-06-01T12:00:00Z")
    assert result.year == 2024
    assert result.tzinfo == timezone.utc


def test_to_datetime_utc_invalid_string_returns_min():
    result = to_datetime_utc("not-a-date")
    assert result == datetime.min.replace(tzinfo=timezone.utc)


def test_to_datetime_utc_unknown_type_returns_min():
    result = to_datetime_utc(12345)
    assert result == datetime.min.replace(tzinfo=timezone.utc)


# --- make_cookie ---

def test_make_cookie_adds_id_to_empty_cookie():
    response = MagicMock()
    make_cookie("abc", None, response)
    response.set_cookie.assert_called_once()
    args = response.set_cookie.call_args[0]
    assert "abc" in args[1]


def test_make_cookie_appends_to_existing_cookie():
    response = MagicMock()
    make_cookie("new_id", "existing_id", response)
    args = response.set_cookie.call_args[0]
    assert "existing_id" in args[1]
    assert "new_id" in args[1]


def test_make_cookie_does_not_duplicate_existing_id():
    response = MagicMock()
    make_cookie("abc", "abc", response)
    args = response.set_cookie.call_args[0]
    # "abc" should appear only once
    assert args[1].count("abc") == 1


def test_make_cookie_empty_result_id_not_added():
    response = MagicMock()
    make_cookie("", "existing_id", response)
    args = response.set_cookie.call_args[0]
    # empty string should not be appended
    assert args[1] == "existing_id"


def test_make_cookie_multiple_ids_joined_with_dot():
    response = MagicMock()
    make_cookie("id2", "id1", response)
    args = response.set_cookie.call_args[0]
    assert args[1] == "id1.id2"


# --- get_table_styles ---

def test_get_table_styles_returns_required_dash_keys():
    styles = get_table_styles()
    assert "style_table" in styles
    assert "style_header" in styles
    assert "style_data" in styles
    assert "style_cell" in styles
    assert "style_data_conditional" in styles


def test_get_table_styles_conditional_has_odd_row():
    styles = get_table_styles()
    conditions = styles["style_data_conditional"]
    row_indices = [c["if"].get("row_index") for c in conditions if "if" in c]
    assert "odd" in row_indices
