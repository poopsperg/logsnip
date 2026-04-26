"""Tests for logsnip.throttler and logsnip.throttle_pipeline."""
from datetime import datetime, timezone
from typing import List

import pytest

from logsnip.parser import LogEntry
from logsnip.throttler import ThrottleOptions, throttle_entries, throttle_summary
from logsnip.throttle_pipeline import ThrottlePipelineOptions, run_throttle_pipeline


def _ts(second: int) -> datetime:
    return datetime(2024, 1, 1, 12, 0, second, tzinfo=timezone.utc)


@pytest.fixture()
def sample_entries() -> List[LogEntry]:
    return [
        LogEntry(timestamp=_ts(i), level="INFO", message=f"msg {i}", line=i)
        for i in range(20)
    ]


def test_throttle_basic_limit(sample_entries):
    opts = ThrottleOptions(max_per_window=5, window_seconds=60)
    result = list(throttle_entries(sample_entries, opts))
    assert len(result) == 5


def test_throttle_window_resets(sample_entries):
    # 10 entries in first 60 s, then 10 more 120 s later
    entries = [
        LogEntry(timestamp=_ts(i), level="INFO", message=f"early {i}", line=i)
        for i in range(10)
    ] + [
        LogEntry(
            timestamp=datetime(2024, 1, 1, 12, 3, i, tzinfo=timezone.utc),
            level="INFO",
            message=f"late {i}",
            line=10 + i,
        )
        for i in range(10)
    ]
    opts = ThrottleOptions(max_per_window=5, window_seconds=60)
    result = list(throttle_entries(entries, opts))
    # 5 from first window + 5 from second window
    assert len(result) == 10


def test_throttle_level_filter(sample_entries):
    mixed = [
        LogEntry(timestamp=_ts(i), level="ERROR" if i % 2 == 0 else "INFO", message=f"m{i}", line=i)
        for i in range(20)
    ]
    opts = ThrottleOptions(max_per_window=3, window_seconds=60, level="ERROR")
    result = list(throttle_entries(mixed, opts))
    assert len(result) == 3
    assert all(e.level == "ERROR" for e in result)


def test_throttle_invalid_max():
    with pytest.raises(ValueError, match="max_per_window"):
        list(throttle_entries([], ThrottleOptions(max_per_window=0)))


def test_throttle_invalid_window():
    with pytest.raises(ValueError, match="window_seconds"):
        list(throttle_entries([], ThrottleOptions(window_seconds=0)))


def test_throttle_summary_counts(sample_entries):
    opts = ThrottleOptions(max_per_window=5, window_seconds=60)
    kept = list(throttle_entries(sample_entries, opts))
    summary = throttle_summary(sample_entries, kept)
    assert "20" in summary
    assert "5" in summary
    assert "15" in summary


def test_pipeline_applies_prefilter():
    entries = [
        LogEntry(timestamp=_ts(i), level="DEBUG" if i < 10 else "ERROR", message=f"m{i}", line=i)
        for i in range(20)
    ]
    opts = ThrottlePipelineOptions(max_per_window=3, window_seconds=60, level="ERROR")
    result = run_throttle_pipeline(entries, opts)
    assert len(result) == 3
    assert all(e.level == "ERROR" for e in result)


def test_pipeline_no_filter(sample_entries):
    opts = ThrottlePipelineOptions(max_per_window=20, window_seconds=60)
    result = run_throttle_pipeline(sample_entries, opts)
    assert len(result) == 20
