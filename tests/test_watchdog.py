"""Tests for logsnip.watchdog."""
from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from logsnip.watchdog import WatchOptions, watch_file, watch_summary
from logsnip.parser import LogEntry


def _ts(minute: int = 0) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


LOG_LINES = [
    "2024-01-01T12:00:00Z INFO  started",
    "2024-01-01T12:01:00Z ERROR failed",
    "2024-01-01T12:02:00Z DEBUG  debug msg",
]


@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    p = tmp_path / "app.log"
    p.write_text("\n".join(LOG_LINES) + "\n")
    return p


def test_watch_file_reads_new_lines(tmp_path: Path):
    p = tmp_path / "live.log"
    p.write_text("")
    opts = WatchOptions(poll_interval=0.05, max_idle=0.2)

    import threading

    def _append():
        time.sleep(0.06)
        with p.open("a") as fh:
            fh.write("2024-01-01T12:00:00Z INFO  hello\n")

    t = threading.Thread(target=_append, daemon=True)
    t.start()
    entries = list(watch_file(p, opts))
    t.join()
    assert len(entries) == 1
    assert entries[0].message == "hello"


def test_watch_file_filter_by_level(tmp_path: Path):
    p = tmp_path / "live.log"
    p.write_text("")
    opts = WatchOptions(level=["ERROR"], poll_interval=0.05, max_idle=0.2)

    import threading

    def _append():
        time.sleep(0.06)
        with p.open("a") as fh:
            fh.write("2024-01-01T12:00:00Z INFO  info msg\n")
            fh.write("2024-01-01T12:01:00Z ERROR  err msg\n")

    t = threading.Thread(target=_append, daemon=True)
    t.start()
    entries = list(watch_file(p, opts))
    t.join()
    assert all(e.level == "ERROR" for e in entries)


def test_watch_file_max_idle_exits(tmp_path: Path):
    p = tmp_path / "idle.log"
    p.write_text("")
    opts = WatchOptions(poll_interval=0.05, max_idle=0.15)
    entries = list(watch_file(p, opts))
    assert entries == []


def test_watch_summary_counts():
    entries = [
        LogEntry(line_number=1, timestamp=_ts(0), level="INFO", message="a"),
        LogEntry(line_number=2, timestamp=_ts(1), level="ERROR", message="b"),
        LogEntry(line_number=3, timestamp=_ts(2), level="INFO", message="c"),
    ]
    s = watch_summary(entries)
    assert s["total"] == 3
    assert s["levels"]["INFO"] == 2
    assert s["levels"]["ERROR"] == 1


def test_watch_file_callback_called(tmp_path: Path):
    p = tmp_path / "cb.log"
    p.write_text("")
    opts = WatchOptions(poll_interval=0.05, max_idle=0.2)
    seen = []

    import threading

    def _append():
        time.sleep(0.06)
        with p.open("a") as fh:
            fh.write("2024-01-01T12:00:00Z INFO  cb test\n")

    t = threading.Thread(target=_append, daemon=True)
    t.start()
    list(watch_file(p, opts, callback=seen.append))
    t.join()
    assert len(seen) == 1
