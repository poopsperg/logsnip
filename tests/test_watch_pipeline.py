"""Tests for logsnip.watch_pipeline."""
from __future__ import annotations

import time
import threading
from pathlib import Path

import pytest

from logsnip.watch_pipeline import WatchPipelineOptions, run_watch_pipeline, watch_pipeline_summary


def _write_after(path: Path, lines: list[str], delay: float = 0.06):
    def _go():
        time.sleep(delay)
        with path.open("a") as fh:
            fh.write("\n".join(lines) + "\n")

    t = threading.Thread(target=_go, daemon=True)
    t.start()
    return t


def test_run_pipeline_returns_entries(tmp_path: Path):
    p = tmp_path / "a.log"
    p.write_text("")
    opts = WatchPipelineOptions(path=p, poll_interval=0.05, max_idle=0.25)
    t = _write_after(p, ["2024-01-01T12:00:00Z INFO  hello"])
    entries = run_watch_pipeline(opts)
    t.join()
    assert len(entries) == 1


def test_run_pipeline_limit(tmp_path: Path):
    p = tmp_path / "b.log"
    p.write_text("")
    opts = WatchPipelineOptions(path=p, poll_interval=0.05, max_idle=0.3, limit=2)
    lines = [
        "2024-01-01T12:00:00Z INFO  one",
        "2024-01-01T12:01:00Z INFO  two",
        "2024-01-01T12:02:00Z INFO  three",
    ]
    t = _write_after(p, lines)
    entries = run_watch_pipeline(opts)
    t.join()
    assert len(entries) == 2


def test_run_pipeline_filter_level(tmp_path: Path):
    p = tmp_path / "c.log"
    p.write_text("")
    opts = WatchPipelineOptions(path=p, level=["ERROR"], poll_interval=0.05, max_idle=0.25)
    lines = [
        "2024-01-01T12:00:00Z INFO  info",
        "2024-01-01T12:01:00Z ERROR  err",
    ]
    t = _write_after(p, lines)
    entries = run_watch_pipeline(opts)
    t.join()
    assert all(e.level == "ERROR" for e in entries)


def test_watch_pipeline_summary_format(tmp_path: Path):
    p = tmp_path / "d.log"
    p.write_text("")
    opts = WatchPipelineOptions(path=p, poll_interval=0.05, max_idle=0.2)
    entries = run_watch_pipeline(opts)
    summary = watch_pipeline_summary(entries)
    assert "watched" in summary
    assert "0" in summary
