"""
E2E test: after submitting an analysis, the /results page must show a result
card with the correct dataset name.
"""
import importlib
import importlib.util
import os
import socket
import subprocess
import sys
import time
import pytest

try:
    PLAYWRIGHT_AVAILABLE = importlib.util.find_spec("playwright") is not None
except ModuleNotFoundError:
    PLAYWRIGHT_AVAILABLE = False

pytestmark = pytest.mark.e2e

PORT = 8053
DATASET_NAME = "E2E results list test"


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


@pytest.fixture(scope="module")
def dash_server():
    if not _wait_for_port("127.0.0.1", 27018, timeout=15):
        pytest.fail("MongoDB is required for e2e tests at localhost:27018")

    env = os.environ.copy()
    env.update(
        {
            "APP_ENV": "ci",
            "HOST": "localhost",
            "MONGO_URI": "mongodb://localhost:27018",
            "DB_NAME": "iPhyloGeo",
            "URL": "http://127.0.0.1",
            "PORT": str(PORT),
            "TEMP_RESULT_TTL_SECONDS": "7200",
            "REDIS_URL": "redis://localhost:6379/0",
        }
    )

    server = subprocess.Popen(
        [sys.executable, "apps/app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    if not _wait_for_port("127.0.0.1", PORT, timeout=45):
        stderr = ""
        try:
            _, stderr = server.communicate(timeout=3)
        except Exception:
            pass
        server.terminate()
        pytest.fail(f"Dash server did not start in time. stderr:\n{stderr}")

    yield f"http://127.0.0.1:{PORT}"

    server.terminate()
    try:
        server.wait(timeout=10)
    except subprocess.TimeoutExpired:
        server.kill()


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
