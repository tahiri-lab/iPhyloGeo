"""
E2E test: after submitting an analysis, the /results page must show a result
card with the correct dataset name.
"""
import importlib
import time
import pytest
from tests.e2e.helpers import (
    PLAYWRIGHT_AVAILABLE,
    _expect,
)

pytestmark = pytest.mark.e2e

DATASET_NAME = "E2E results list test"


def _select_all_analysis_columns(page):
    labels = page.locator("#col-analyze label")
    _expect(labels.first).to_be_visible(timeout=20000)
    for idx in range(labels.count()):
        cb = labels.nth(idx).locator("input[type='checkbox']")
        if not cb.is_checked():
            labels.nth(idx).click(force=True)


def _grant_consent(page):
    consent_group = page.locator("#consent-save-data")
    granted_input = consent_group.locator("input[value='granted']")
    if granted_input.count() > 0:
        granted_input.first.check(force=True)
    else:
        consent_group.locator("label").first.click(force=True)


def _wait_for_auth_cookie(page, timeout=30000):
    """Wait until the AUTH cookie exists and contains at least one result id."""
    deadline = time.time() + (timeout / 1000)
    while time.time() < deadline:
        cookies = page.context.cookies()
        auth_cookie = next((c for c in cookies if c.get("name") == "AUTH"), None)
        if auth_cookie and auth_cookie.get("value"):
            return auth_cookie["value"]
        time.sleep(0.2)
    pytest.fail("AUTH cookie was not set after submission")


@pytest.mark.e2e
@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed")
def test_submitted_result_appears_in_results_list(dash_server, page):
    """
    After submitting a demo analysis, navigating to /results must show a
    result card whose title matches the dataset name entered at submit time.
    """
    # --- Step 1: load demo data on getStarted ---
    page.goto(f"{dash_server}/getStarted", wait_until="domcontentloaded")
    page.locator("#upload-test-data").click()
    _expect(page.locator("#submit-dataset")).to_be_visible(timeout=40000)

    # --- Step 2: select all columns ---
    _select_all_analysis_columns(page)

    # --- Step 3: enter dataset name ---
    page.locator("#input-dataset-visible").fill(DATASET_NAME)

    # --- Step 4: grant consent then submit ---
    page.locator("#submit-dataset").click()
    _grant_consent(page)
    page.locator("#submit-dataset").click()

    # --- Step 5: wait for the progress popup to appear (analysis was submitted) ---
    # The popup becomes visible after the submit callback fires and the cookie is set.
    _expect(page.locator("#popup")).to_be_visible(timeout=30000)

    # Wait for the popup title to settle (confirms the callback fully completed
    # and the AUTH cookie has been written to the response).
    _expect(page.locator("#popup-title")).to_be_visible(timeout=10000)

    # CI runners can be slower; ensure the submit callback wrote AUTH before
    # navigating away, otherwise /results may render the empty state.
    _wait_for_auth_cookie(page, timeout=30000)

    # --- Step 6: navigate to /results ---
    # page.goto() preserves the browser cookies (AUTH cookie was set server-side).
    page.goto(f"{dash_server}/results", wait_until="networkidle")

    # --- Step 7: a card with the correct name must be visible ---
    cards = page.locator(".result-card__title")
    _expect(cards.first).to_be_visible(timeout=30000)

    titles = [cards.nth(i).inner_text() for i in range(cards.count())]
    assert DATASET_NAME in titles, (
        f"Expected a result card with name '{DATASET_NAME}', got: {titles}"
    )
