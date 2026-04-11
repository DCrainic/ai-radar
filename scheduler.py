"""
Background scheduler for automatic tweet refresh.
Runs in a daemon thread so it stops cleanly when the app exits.
"""

from __future__ import annotations

import threading
import time
import logging

import schedule

logger = logging.getLogger(__name__)


def _run_loop():
    while True:
        schedule.run_pending()
        time.sleep(30)


def start(fetch_fn, interval_minutes: int = 30):
    """
    Start a background thread that calls `fetch_fn()` every `interval_minutes`.

    The thread is a daemon — it shuts down automatically when the main
    process exits, so no cleanup is needed.
    """
    schedule.every(interval_minutes).minutes.do(_safe_fetch, fetch_fn)

    thread = threading.Thread(target=_run_loop, daemon=True, name="ai-radar-scheduler")
    thread.start()
    logger.info(f"Scheduler started — refreshing every {interval_minutes} min")
    return thread


def _safe_fetch(fetch_fn):
    try:
        fetch_fn()
    except Exception as exc:
        logger.error(f"Scheduled fetch failed: {exc}")
