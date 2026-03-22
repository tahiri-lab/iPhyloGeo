import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SUPPORTED_LOCALES = ["en", "fr"]
LOCALE_PAGES = ["home", "setting", "upload", "help", "result", "results", "sidebar"]
LOCALE_DIR_CANDIDATES = ["locales"]


def _load_json_file(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as file:
            content = json.load(file)
            return content if isinstance(content, dict) else {}
    except FileNotFoundError:
        logger.warning("Translation file not found: %s", path)
        return {}
    except json.JSONDecodeError as exc:
        logger.warning("Invalid JSON in translation file %s: %s", path, exc)
        return {}
    except OSError as exc:
        logger.warning("Failed to read translation file %s: %s", path, exc)
        return {}


def _resolve_locale_base_dir() -> Path:
    apps_dir = Path(__file__).resolve().parents[1]

    for folder_name in LOCALE_DIR_CANDIDATES:
        candidate = apps_dir / folder_name
        if candidate.exists() and candidate.is_dir():
            return candidate

    default_dir = apps_dir / "locales"
    logger.warning(
        "No translation folder found in %s. Expected one of: %s",
        apps_dir,
        ", ".join(LOCALE_DIR_CANDIDATES),
    )
    return default_dir


def _load_translations() -> dict:
    base_dir = _resolve_locale_base_dir()

    translations = {}
    for locale in SUPPORTED_LOCALES:
        locale_data = {}
        for page in LOCALE_PAGES:
            translation_file = base_dir / locale / f"{page}.json"
            locale_data[page] = _load_json_file(translation_file)
        translations[locale] = locale_data

    return translations


LOCALES = _load_translations()
TRANSLATIONS = LOCALES
SUPPORTED_LANGUAGES = SUPPORTED_LOCALES


def _get_nested_value(data: dict, key: str):
    value = data
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def _normalize_key(key: str) -> str:
    return ".".join(part.replace("_", "-") for part in key.split("."))


def _resolve_translation(key: str, locale: str):
    keys_to_try = [key, _normalize_key(key)]
    locales_to_try = [locale, "en"]

    for locale_name in locales_to_try:
        locale_data = LOCALES.get(locale_name, {})
        for candidate_key in keys_to_try:
            value = _get_nested_value(locale_data, candidate_key)
            if isinstance(value, str):
                return value

    return None


def t(key: str, lang: str = "en") -> str:
    selected_locale = lang if lang in LOCALES else "en"
    value = _resolve_translation(key, selected_locale)

    if value is None:
        logger.warning("Missing translation key '%s' for locale '%s'", key, selected_locale)
        return key

    return value
