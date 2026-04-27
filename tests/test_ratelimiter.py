"""Tests for logsnip.ratelimiter."""
from datetime import datetime, timedelta
from typing import List

import pytest

from logsnip.parser import LogEntry
from logsnip.ratelimiter import (
    RateLimitOptions,
    RateLimitReport,
    ratelimit_entries,
    ratelimit_summary,
)


def _ts(offset_seconds: int) -> datetime:
    base = datetime(2024, 1, 1, 12, 0, 0)
    return base + timedelta(seconds=offset_seconds)


@pytest.fixture
def sample_entries() -> List[LogEntry]:
    return [
        LogEntry(timestamp=_ts(i), level="ERROR", message=f"err {i}", line_number=i)
        for i in range(15)
    ]


def test_ratelimit_basic_drops_excess(sample_entries):
    opts = RateLimitOptions(max_per_window=5, window_seconds=120)
    result = list(ratelimit_entries(sample_entries, opts))
    assert len(result) == 5


def test_ratelimit_window_resets(sample_entries):
    # 10 entries in first 60s, 5 in next 60s
    opts = RateLimitOptions(max_per_window=5, window_seconds=60)
    result = list(ratelimit_entries(sample_entries, opts))
    # first window (0-59s): keep 5; second window (60-119s): keep 5 more
    assert len(result) == 10


def test_ratelimit_invalid_max():
    with pytest.raises(ValueError):
        list(ratelimit_entries([], RateLimitOptions(max_per_window=0)))


def test_ratelimit_invalid_window():
    with pytest.raises(ValueError):
        list(ratelimit_entries([], RateLimitOptions(window_seconds=0)))


def test_ratelimit_skips_other_levels():
    entries = [
        LogEntry(timestamp=_ts(i), level="INFO" if i % 2 == 0 else "ERROR", message=f"msg {i}", line_number=i)
        for i in range(10)
    ]
    opts = RateLimitOptions(max_per_window=2, window_seconds=120, level_filter="ERROR")
    result = list(ratelimit_entries(entries, opts))
    info_count = sum(1 for e in result if e.level == "INFO")
    error_count = sum(1 for e in result if e.level == "ERROR")
    assert info_count == 5
    assert error_count == 2


def test_ratelimit_pattern_filter():
    entries = [
        LogEntry(timestamp=_ts(i), level="WARN", message="timeout" if i < 8 else "ok", line_number=i)
        for i in range(10)
    ]
    opts = RateLimitOptions(max_per_window=3, window_seconds=120, pattern="timeout")
    result = list(ratelimit_entries(entries, opts))
    timeout_out = [e for e in result if "timeout" in e.message]
    ok_out = [e for e in result if e.message == "ok"]
    assert len(timeout_out) == 3
    assert len(ok_out) == 2


def test_ratelimit_summary_counts(sample_entries):
    opts = RateLimitOptions(max_per_window=5, window_seconds=120)
    result = list(ratelimit_entries(sample_entries, opts))
    report = ratelimit_summary(sample_entries, result)
    assert report.total_in == 15
    assert report.total_out == 5
    assert report.dropped == 10


def test_ratelimit_summary_drop_pct(sample_entries):
    opts = RateLimitOptions(max_per_window=5, window_seconds=120)
    result = list(ratelimit_entries(sample_entries, opts))
    report = ratelimit_summary(sample_entries, result)
    assert report.drop_pct == pytest.approx(66.67)


def test_ratelimit_empty_input():
    opts = RateLimitOptions(max_per_window=5, window_seconds=60)
    result = list(ratelimit_entries([], opts))
    assert result == []
