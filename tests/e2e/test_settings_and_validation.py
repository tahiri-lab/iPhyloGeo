"""
E2E tests for:
- Settings page: save and persist a value across navigation
- Settings page: reset to default
- Submit form validation: missing dataset name error
- Submit form validation: missing column selection error
- Sidebar navigation links
"""
import importlib
import re
import pytest
from tests.e2e.helpers import (
    PLAYWRIGHT_AVAILABLE,
    _expect,
)

pytestmark = pytest.mark.e2e


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
