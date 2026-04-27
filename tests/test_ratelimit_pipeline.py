"""Tests for logsnip.ratelimit_pipeline."""
from datetime import datetime, timedelta
from typing import List

import pytest

from logsnip.parser import LogEntry
from logsnip.ratelimit_pipeline import (
    RateLimitPipelineOptions,
    pipeline_summary,
    run_ratelimit_pipeline,
)


def _ts(offset_seconds: int) -> datetime:
    base = datetime(2024, 1, 1, 12, 0, 0)
    return base + timedelta(seconds=offset_seconds)


@pytest.fixture
def sample_entries() -> List[LogEntry]:
    levels = ["ERROR", "WARN", "INFO", "ERROR", "ERROR",
              "WARN", "ERROR", "INFO", "ERROR", "ERROR"]
    return [
        LogEntry(timestamp=_ts(i * 5), level=levels[i], message=f"msg {i}", line_number=i)
        for i in range(10)
    ]


def test_run_pipeline_returns_results(sample_entries):
    opts = RateLimitPipelineOptions(max_per_window=10, window_seconds=3600)
    result, report = run_ratelimit_pipeline(sample_entries, opts)
    assert len(result) == len(sample_entries)
    assert report.dropped == 0


def test_run_pipeline_drops_excess(sample_entries):
    opts = RateLimitPipelineOptions(max_per_window=2, window_seconds=3600, level_filter="ERROR")
    result, report = run_ratelimit_pipeline(sample_entries, opts)
    error_out = [e for e in result if e.level == "ERROR"]
    assert len(error_out) == 2
    assert report.dropped > 0


def test_run_pipeline_pre_filter_level(sample_entries):
    opts = RateLimitPipelineOptions(
        max_per_window=100,
        window_seconds=3600,
        pre_filter_level="ERROR",
    )
    result, report = run_ratelimit_pipeline(sample_entries, opts)
    assert all(e.level == "ERROR" for e in result)


def test_run_pipeline_pre_filter_pattern(sample_entries):
    opts = RateLimitPipelineOptions(
        max_per_window=100,
        window_seconds=3600,
        pre_filter_pattern="msg [02]",
    )
    result, report = run_ratelimit_pipeline(sample_entries, opts)
    assert all("msg 0" in e.message or "msg 2" in e.message for e in result)


def test_pipeline_summary_format(sample_entries):
    opts = RateLimitPipelineOptions(max_per_window=2, window_seconds=3600, level_filter="ERROR")
    _, report = run_ratelimit_pipeline(sample_entries, opts)
    summary = pipeline_summary(report)
    assert "rate-limit" in summary
    assert "dropped" in summary
    assert "%" in summary
