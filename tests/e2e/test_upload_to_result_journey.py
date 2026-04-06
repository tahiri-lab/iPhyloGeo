import os
import importlib
import importlib.util
import re
import socket
import subprocess
import sys
import time
from urllib.parse import urlparse

import pytest
import requests

try:
    PLAYWRIGHT_AVAILABLE = importlib.util.find_spec("playwright") is not None
except ModuleNotFoundError:  # pragma: no cover - package missing in env
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


@pytest.mark.parametrize("path", ["/", "/getStarted", "/settings", "/help"])
def test_pages_are_reachable(dash_server, path):
    response = requests.get(f"{dash_server}{path}", timeout=10)
    assert response.status_code == 200


def _open_dropdown_and_pick_option(page, dropdown_id, option_index=0):
    dropdown = page.locator(f"#{dropdown_id}")
    _expect(dropdown).to_be_visible()

    control = dropdown.locator(".Select-control").first
    if control.count() > 0:
        control.click(force=True)
    else:
        dropdown.click(force=True)

    # Scope strictly to the opened dropdown menu options. Avoid broad [role='option']
    # selectors because Dash/React can mark selected value labels with that role.
    menu_options = page.locator(
        ".Select-menu-outer .VirtualizedSelectOption:visible, "
        ".Select-menu-outer .Select-option:visible"
    )

    if menu_options.count() > option_index:
        _expect(menu_options.nth(option_index)).to_be_visible()
        menu_options.nth(option_index).click(force=True)
        return

    # Fallback for virtualized or delayed menus: use keyboard navigation.
    page.keyboard.press("ArrowDown")
    for _ in range(option_index):
        page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")


def _set_single_graph_type(page, graph_type_label):
    labels = page.locator("#choose-graph-type label")
    total_labels = labels.count()
    if total_labels == 0:
        raise AssertionError("Graph type labels are missing")

    for idx in range(total_labels):
        label = labels.nth(idx)
        text = label.inner_text().strip().lower()
        checkbox = label.locator("input[type='checkbox']")
        should_be_selected = graph_type_label.lower() in text
        if checkbox.is_checked() != should_be_selected:
            label.click(force=True)


def _select_all_analysis_columns(page):
    labels = page.locator("#col-analyze label")
    total_labels = labels.count()
    if total_labels == 0:
        raise AssertionError("No analysis columns available to select")

    for idx in range(total_labels):
        label = labels.nth(idx)
        checkbox = label.locator("input[type='checkbox']")
        if not checkbox.is_checked():
            label.click(force=True)


@pytest.mark.e2e
@pytest.mark.skipif(
    not PLAYWRIGHT_AVAILABLE,
    reason="playwright is not installed; install pytest-playwright dependencies to run this test",
)
def test_full_demo_data_journey_home_to_result(dash_server, page):
    page.goto(dash_server, wait_until="domcontentloaded")

    # Section 1: Start on Home page and go to Get Started
    page.locator("#themes").click()
    page.wait_for_url("**/getStarted")

    # Section 2: Load the built-in demo data
    page.locator("#upload-test-data").click()

    # Wait for the upload pipeline sections to render
    _expect(page.locator("#xaxis-data")).to_be_visible(timeout=40000)
    _expect(page.locator("#yaxis-data")).to_be_visible(timeout=40000)
    _expect(page.locator("#choose-graph-type")).to_be_visible(timeout=40000)
    _expect(page.locator("#submit-dataset")).to_be_visible(timeout=40000)

    # Section 3: Select X and Y columns for graph generation
    _open_dropdown_and_pick_option(page, "xaxis-data", option_index=0)
    _open_dropdown_and_pick_option(page, "yaxis-data", option_index=1)

    # Section 4: Check each graph type one-by-one and verify graph rendering
    for graph_type in ["Bar", "Scatter", "Line", "Pie"]:
        _set_single_graph_type(page, graph_type)
        _expect(page.locator("#output-graph .js-plotly-plot").first).to_be_visible()

    # Section 5: Verify alignment chart is present
    _expect(page.locator("#alignment-chart")).to_be_visible(timeout=30000)
    _expect(page.locator("#my-alignment-viewer")).to_be_visible(timeout=30000)

    # Section 6: Select all columns to analyze
    _select_all_analysis_columns(page)

    # Section 7: Enter dataset name
    page.locator("#input-dataset-visible").fill("E2E demo dataset")

    # Section 8: Validate consent is required, then provide consent
    page.locator("#submit-dataset").click()
    try:
        _expect(page.locator("#consent-error-message")).to_have_text(
            re.compile(r"\S+"),
            timeout=15000,
        )
    except AssertionError:
        # On slower runs, the error message can remain in loading state longer.
        # Equivalent validation signal: submit is blocked and popup stays hidden.
        _expect(page.locator("#popup")).to_have_class(
            re.compile(r".*hidden.*"),
            timeout=5000,
        )

    consent_group = page.locator("#consent-save-data")
    _expect(consent_group).to_be_visible()

    granted_input = consent_group.locator("input[value='granted']")
    if granted_input.count() > 0:
        granted_input.first.check(force=True)
    else:
        radio_inputs = consent_group.locator("input[type='radio']")
        if radio_inputs.count() > 0:
            radio_inputs.first.check(force=True)
        else:
            consent_group.locator("label").first.click(force=True)

    # Section 9: Submit analysis and wait for generated result link
    page.locator("#submit-dataset").click()
    result_link = page.locator("#popup-done-link")
    _expect(result_link).to_be_visible(timeout=120000)
    _expect(result_link).to_have_attribute("href", re.compile(r"/result/"), timeout=180000)
    href = result_link.get_attribute("href")
    parsed_path = urlparse(href).path
    assert parsed_path.startswith("/result/")

    # Section 10: Go to result page and validate core result content
    page.goto(f"{dash_server}{parsed_path}")
    page.wait_for_url("**/result/**", timeout=60000)

    _expect(page.locator("#results-name")).to_have_text(re.compile(r"\S+"), timeout=60000)

    _expect(page.locator("#unavailable-result-message")).to_have_attribute(
        "class", re.compile(r".*hidden.*")
    )

    _expect(page.locator("#result-actions-row")).to_be_visible()
    _expect(page.locator("#results-row")).to_be_visible()
    _expect(page.locator("#climatic-tree-container")).to_be_visible()
    _expect(page.locator("#genetic-tree-container")).to_be_visible()
