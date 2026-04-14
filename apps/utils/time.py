from datetime import datetime, timezone


def to_utc_datetime(value):
    """Convert a datetime or ISO string to a UTC-aware datetime.

    Returns None for unsupported or invalid values.
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    return None


def format_remaining_time(seconds: float, lang: str = "en") -> str:
    """Return a localised human-readable string for a remaining time in seconds.

    Thresholds:
      >= 3600 s  -> hours   (upload.popup.time-remaining-hr)
      >= 60 s    -> minutes (upload.popup.time-remaining-min)
      < 60 s     -> seconds (upload.popup.time-remaining-sec)
    """
    from utils.i18n import t

    seconds = max(0, int(seconds))
    if seconds >= 3600:
        key, n = "upload.popup.time-remaining-hr", seconds // 3600
    elif seconds >= 60:
        key, n = "upload.popup.time-remaining-min", seconds // 60
    else:
        key, n = "upload.popup.time-remaining-sec", seconds
    return t(key, lang).replace("{n}", str(n))
