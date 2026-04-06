"""
E2E tests for each page in the navigation.
Verifies that each page loads, renders its key content, and is reachable
via both direct URL and sidebar link.
"""
import importlib
import importlib.util
import os
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


# ---------------------------------------------------------------------------
# Home page ( / )
# ---------------------------------------------------------------------------

@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_home_page_loads(dash_server, page):
    """Home page must show the title and the Get Started button."""
    page.goto(dash_server, wait_until="domcontentloaded")

    _expect(page.locator("#home-title")).to_be_visible(timeout=15000)
    _expect(page.locator("#themes")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_home_page_via_sidebar(dash_server, page):
    """Sidebar home link must navigate to / and render the home page."""
    page.goto(f"{dash_server}/settings", wait_until="domcontentloaded")

    page.locator("#nav-link-home").click()
    page.wait_for_url("**/", timeout=10000)

    _expect(page.locator("#home-title")).to_be_visible(timeout=15000)


# ---------------------------------------------------------------------------
# Get Started / Upload page ( /getStarted )
# ---------------------------------------------------------------------------

@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_getstarted_page_loads(dash_server, page):
    """getStarted page must show the file upload section."""
    page.goto(f"{dash_server}/getStarted", wait_until="domcontentloaded")

    _expect(page.locator("#drop-file-section-container")).to_be_visible(timeout=15000)
    _expect(page.locator("#upload-test-data")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_getstarted_page_via_sidebar(dash_server, page):
    """Sidebar upload link must navigate to /getStarted."""
    page.goto(dash_server, wait_until="domcontentloaded")

    page.locator("#nav-link-getstarted").click()
    page.wait_for_url("**/getStarted", timeout=10000)

    _expect(page.locator("#drop-file-section-container")).to_be_visible(timeout=15000)


# ---------------------------------------------------------------------------
# Results page ( /results )
# ---------------------------------------------------------------------------

@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_results_page_loads(dash_server, page):
    """Results page must render the results title and list container."""
    page.goto(f"{dash_server}/results", wait_until="domcontentloaded")

    _expect(page.locator("#results-page-content")).to_be_visible(timeout=15000)
    _expect(page.locator("#results-title")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_results_page_via_sidebar(dash_server, page):
    """Sidebar results link must navigate to /results."""
    page.goto(dash_server, wait_until="domcontentloaded")

    page.locator("#nav-link-results").click()
    page.wait_for_url("**/results", timeout=10000)

    _expect(page.locator("#results-page-content")).to_be_visible(timeout=15000)


# ---------------------------------------------------------------------------
# Settings page ( /settings )
# ---------------------------------------------------------------------------

@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_settings_page_loads(dash_server, page):
    """Settings page must render the form fields and action buttons."""
    page.goto(f"{dash_server}/settings", wait_until="domcontentloaded")

    _expect(page.locator("#settings-page-content")).to_be_visible(timeout=15000)
    _expect(page.locator("#alignment-method")).to_be_visible()
    _expect(page.locator("#save-settings-button")).to_be_visible()
    _expect(page.locator("#reset-button")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_settings_page_via_sidebar(dash_server, page):
    """Sidebar settings link must navigate to /settings."""
    page.goto(dash_server, wait_until="domcontentloaded")

    page.locator("#nav-link-settings").click()
    page.wait_for_url("**/settings", timeout=10000)

    _expect(page.locator("#settings-page-content")).to_be_visible(timeout=15000)


# ---------------------------------------------------------------------------
# Help page ( /help )
# ---------------------------------------------------------------------------

@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_help_page_loads(dash_server, page):
    """Help page must render the help content."""
    page.goto(f"{dash_server}/help", wait_until="domcontentloaded")

    _expect(page.locator("#help-page-content")).to_be_visible(timeout=15000)


@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_help_page_via_sidebar(dash_server, page):
    """Sidebar help link must navigate to /help."""
    page.goto(dash_server, wait_until="domcontentloaded")

    page.locator("#nav-link-help").click()
    page.wait_for_url("**/help", timeout=10000)

    _expect(page.locator("#help-page-content")).to_be_visible(timeout=15000)
