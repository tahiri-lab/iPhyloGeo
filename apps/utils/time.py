from utils.i18n import t


def format_remaining_time(seconds: float, lang: str = "en") -> str:
    """Return a localised human-readable string for a remaining time in seconds.

    Thresholds:
      >= 3600 s  -> hours   (upload.popup.time-remaining-hr)
      >= 60 s    -> minutes (upload.popup.time-remaining-min)
      < 60 s     -> seconds (upload.popup.time-remaining-sec)
    """
    seconds = max(0, int(seconds))
    if seconds >= 3600:
        key, n = "upload.popup.time-remaining-hr", seconds // 3600
    elif seconds >= 60:
        key, n = "upload.popup.time-remaining-min", seconds // 60
    else:
        key, n = "upload.popup.time-remaining-sec", seconds
    return t(key, lang).replace("{n}", str(n))
