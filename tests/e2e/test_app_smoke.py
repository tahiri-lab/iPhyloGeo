import os
import socket
import subprocess
import sys
import time

import pytest
import requests


pytestmark = pytest.mark.e2e


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
            "PORT": "8050",
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

    if not _wait_for_port("127.0.0.1", 8050, timeout=45):
        stderr = ""
        try:
            _, stderr = server.communicate(timeout=3)
        except Exception:
            pass
        server.terminate()
        pytest.fail(f"Dash server did not start in time. stderr:\n{stderr}")

    yield "http://127.0.0.1:8050"

    server.terminate()
    try:
        server.wait(timeout=10)
    except subprocess.TimeoutExpired:
        server.kill()


@pytest.mark.parametrize("path", ["/", "/getStarted", "/settings", "/help"])
def test_pages_are_reachable(dash_server, path):
    response = requests.get(f"{dash_server}{path}", timeout=10)
    assert response.status_code == 200
