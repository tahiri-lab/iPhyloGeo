"""
RQ worker entry point for iPhyloGeo.

The app lives in apps/ and its modules are imported as e.g. `utils.background_tasks`.
This script adds apps/ to sys.path before importing anything so the worker resolves
the same module paths that the Dash app uses.

Platform notes
--------------
- Linux / macOS : uses the forking Worker (job crash kills only the child process)
- Windows       : uses SimpleWorker (no fork) + a no-op death-penalty class because
                  Windows has neither os.fork() nor signal.SIGALRM.

Usage:
    python worker.py
"""

import warnings
warnings.filterwarnings("ignore", message=r"The Bio\.Application modules")

import os
import sys
from pathlib import Path

# ── Python path ───────────────────────────────────────────────────────────────
# Must happen before any app imports so every module resolves under `apps/`.
APPS_DIR = Path(__file__).parent / "apps"
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

# ── Environment ───────────────────────────────────────────────────────────────
from dotenv import load_dotenv

load_dotenv()

# ── Worker ────────────────────────────────────────────────────────────────────
from redis import Redis
from rq import Queue
from rq.worker import SimpleWorker, Worker


class _NoopDeathPenalty:
    """
    No-op replacement for UnixSignalDeathPenalty on Windows.

    RQ's default death penalty uses signal.SIGALRM to enforce job timeouts,
    which only exists on Unix. This class satisfies the same interface but
    does nothing, so jobs run to natural completion without hard timeout
    enforcement. The job_timeout value is still stored in Redis metadata so
    the UI can display it; it just won't forcibly kill the job process.
    """

    def __init__(self, timeout, exception=None, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def cancel(self):
        pass


if __name__ == "__main__":
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    conn = Redis.from_url(redis_url)
    queues = [Queue(connection=conn)]

    is_windows = sys.platform == "win32"

    print(f"[Worker] Platform: {'Windows' if is_windows else sys.platform}")
    print(f"[Worker] Redis: {redis_url}")
    print(f"[Worker] Python path includes: {APPS_DIR}")

    if is_windows:
        # Subclass to override death_penalty_class as a class attribute —
        # this version of RQ doesn't accept it as a constructor kwarg.
        class _WindowsWorker(SimpleWorker):
            death_penalty_class = _NoopDeathPenalty

        worker = _WindowsWorker(queues, connection=conn)
        worker.work()          # no with_scheduler — RQ scheduler also uses SIGALRM
    else:
        # Forking Worker: each job runs in an isolated child process.
        worker = Worker(queues, connection=conn)
        worker.work(with_scheduler=True)
