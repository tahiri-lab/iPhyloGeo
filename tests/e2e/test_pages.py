"""
E2E tests for each page in the navigation.
Verifies that each page loads, renders its key content, and is reachable
via both direct URL and sidebar link.
"""
import importlib
import pytest
from tests.e2e.helpers import (
    PLAYWRIGHT_AVAILABLE,
    _expect,
)

pytestmark = pytest.mark.e2e

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
