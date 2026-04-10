import os
import subprocess
import sys

import pytest

from tests.e2e.helpers import _find_free_port, _wait_for_http_ready, _wait_for_port


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
