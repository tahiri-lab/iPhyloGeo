"""
E2E tests for:
- Settings page: save and persist a value across navigation
- Settings page: reset to default
- Submit form validation: missing dataset name error
- Submit form validation: missing column selection error
- Sidebar navigation links
"""
import importlib
import importlib.util
import os
import re
import socket
import subprocess
import sys
import time
import pytest
import requests

try:
    PLAYWRIGHT_AVAILABLE = importlib.util.find_spec("playwright") is not None
except ModuleNotFoundError:
    PLAYWRIGHT_AVAILABLE = False

pytestmark = pytest.mark.e2e


def _expect(locator):
    sync_api = importlib.import_module("playwright.sync_api")
    return sync_api.expect(locator)


def _wait_for_port(host, port, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            if sock.connect_ex((host, port)) == 0:
                return True
        time.sleep(0.5)
    return False


def _find_free_port(host="127.0.0.1"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return sock.getsockname()[1]


def _wait_for_http_ready(base_url, timeout=45):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = requests.get(f"{base_url}/", timeout=2)
            if response.status_code < 500:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


@pytest.fixture(scope="module")
def dash_server():
    if not _wait_for_port("127.0.0.1", 27018, timeout=15):
        pytest.fail("MongoDB is required for e2e tests at localhost:27018")

    port = _find_free_port()

    env = os.environ.copy()
    env.update(
        {
            "APP_ENV": "prod",
            "HOST": "localhost",
            "MONGO_URI": "mongodb://localhost:27018",
            "DB_NAME": "iPhyloGeo",
            "URL": "http://127.0.0.1",
            "PORT": str(port),
            "TEMP_RESULT_TTL_SECONDS": "7200",
            "REDIS_URL": "redis://localhost:6379/0",
        }
    )

    server = subprocess.Popen(
        [sys.executable, "apps/app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )

    base_url = f"http://127.0.0.1:{port}"

    if not _wait_for_port("127.0.0.1", port, timeout=45) or not _wait_for_http_ready(base_url, timeout=45):
        server.terminate()
        pytest.fail("Dash server did not start in time.")

    yield base_url

    server.terminate()
    try:
        server.wait(timeout=10)
    except subprocess.TimeoutExpired:
        server.kill()


def _go_to_settings(page, base_url):
    page.goto(f"{base_url}/settings", wait_until="domcontentloaded")
    _expect(page.locator("#save-settings-button")).to_be_visible(timeout=15000)


def _change_bootstrap_threshold(page, value: str):
    """Clear the bootstrap threshold input and type a new value."""
    field = page.locator("#bootstrap-threshold")
    field.click(click_count=3)
    field.fill(value)


# ---------------------------------------------------------------------------
# Settings — save and persist
# ---------------------------------------------------------------------------

@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_settings_save_shows_success_toast(dash_server, page):
    """Clicking Save must display a success toast notification."""
    _go_to_settings(page, dash_server)

    _change_bootstrap_threshold(page, "42")
    page.locator("#save-settings-button").click()

    # The toast container must contain a success message
    toast = page.locator("#toast-container .toast-message.success")
    _expect(toast).to_be_visible(timeout=10000)

    # Restore default so the JSON file is left in a clean state
    _change_bootstrap_threshold(page, "10")
    page.locator("#save-settings-button").click()


# ---------------------------------------------------------------------------
# Settings — reset to default
# ---------------------------------------------------------------------------

@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_settings_reset_restores_default(dash_server, page):
    """After changing a value in-memory and resetting, the field must return to default."""
    _go_to_settings(page, dash_server)

    # Change value in the UI only — do NOT save so the JSON file is not modified
    _change_bootstrap_threshold(page, "55")

    page.locator("#reset-button").click()

    # Default bootstrap threshold is 10
    field = page.locator("#bootstrap-threshold")
    _expect(field).to_have_value("10", timeout=10000)


# ---------------------------------------------------------------------------
# Submit form validation — missing dataset name
# ---------------------------------------------------------------------------

@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_submit_without_dataset_name_shows_error(dash_server, page):
    """Clicking Submit with an empty dataset name must show the name error."""
    page.goto(f"{dash_server}/getStarted", wait_until="domcontentloaded")

    # Load demo data so the submit button is rendered
    page.locator("#upload-test-data").click()
    _expect(page.locator("#submit-dataset")).to_be_visible(timeout=40000)

    # Clear the name field (may already be empty) and submit
    page.locator("#input-dataset-visible").fill("")
    page.locator("#submit-dataset").click()

    _expect(page.locator("#name-error-message")).to_have_text(
        re.compile(r"\S+"), timeout=10000
    )


# ---------------------------------------------------------------------------
# Submit form validation — missing column selection
# ---------------------------------------------------------------------------

@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_submit_without_columns_shows_error(dash_server, page):
    """Clicking Submit with no columns selected must show the column error."""
    page.goto(f"{dash_server}/getStarted", wait_until="domcontentloaded")

    page.locator("#upload-test-data").click()
    _expect(page.locator("#submit-dataset")).to_be_visible(timeout=40000)

    # Uncheck all analysis columns
    labels = page.locator("#col-analyze label")
    _expect(labels.first).to_be_visible(timeout=20000)
    for idx in range(labels.count()):
        cb = labels.nth(idx).locator("input[type='checkbox']")
        if cb.is_checked():
            labels.nth(idx).click(force=True)

    # Provide a name so only the column error fires
    page.locator("#input-dataset-visible").fill("test-dataset")
    page.locator("#submit-dataset").click()

    _expect(page.locator("#column-error-message")).to_have_text(
        re.compile(r"\S+"), timeout=10000
    )


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_sidebar_nav_links(dash_server, page):
    """Each sidebar link must navigate to the correct page."""
    page.goto(dash_server, wait_until="domcontentloaded")

    nav_cases = [
        ("nav-link-getstarted", "/getStarted"),
        ("nav-link-results", "/results"),
        ("nav-link-settings", "/settings"),
        ("nav-link-help", "/help"),
        ("nav-link-home", "/"),
    ]

    for link_id, expected_path in nav_cases:
        page.locator(f"#{link_id}").click()
        page.wait_for_url(f"**{expected_path}", timeout=10000)
        assert expected_path in page.url, f"Expected {expected_path} in URL, got {page.url}"
