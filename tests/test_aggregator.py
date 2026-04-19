"""Tests for logsnip.aggregator."""
import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.aggregator import (
    AggregateOptions,
    aggregate_by_window,
    aggregate_by_level,
    aggregate,
)


def _ts(offset: int) -> datetime:
    return datetime(2024, 1, 1, 0, offset // 60, offset % 60, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(line_no=i, timestamp=_ts(i * 20), level="INFO", message=f"msg {i}")
        for i in range(6)
    ] + [
        LogEntry(line_no=10, timestamp=_ts(0), level="ERROR", message="err"),
        LogEntry(line_no=11, timestamp=_ts(10), level="WARN", message="warn"),
    ]


def test_aggregate_by_window_basic(sample_entries):
    buckets = aggregate_by_window(sample_entries[:6], window_seconds=60)
    assert len(buckets) >= 1
    total = sum(b.count for b in buckets)
    assert total == 6


def test_aggregate_by_window_empty():
    assert aggregate_by_window([], 60) == []


def test_aggregate_by_window_single_bucket():
    entries = [
        LogEntry(line_no=i, timestamp=_ts(i), level="INFO", message=f"m{i}")
        for i in range(5)
    ]
    buckets = aggregate_by_window(entries, window_seconds=300)
    assert len(buckets) == 1
    assert buckets[0].count == 5


def test_aggregate_by_level_groups(sample_entries):
    buckets = aggregate_by_level(sample_entries)
    keys = {b.key for b in buckets}
    assert "INFO" in keys
    assert "ERROR" in keys


def test_aggregate_by_level_counts(sample_entries):
    buckets = aggregate_by_level(sample_entries)
    info = next(b for b in buckets if b.key == "INFO")
    assert info.count == 6


def test_aggregate_dispatch_level():
    entries = [
        LogEntry(line_no=0, timestamp=_ts(0), level="DEBUG", message="d"),
        LogEntry(line_no=1, timestamp=_ts(1), level="INFO", message="i"),
    ]
    opts = AggregateOptions(group_by_level=True)
    buckets = aggregate(entries, opts)
    assert len(buckets) == 2


def test_aggregate_dispatch_window():
    entries = [
        LogEntry(line_no=i, timestamp=_ts(i * 5), level="INFO", message=f"m{i}")
        for i in range(4)
    ]
    opts = AggregateOptions(window_seconds=30, group_by_level=False)
    buckets = aggregate(entries, opts)
    assert sum(b.count for b in buckets) == 4
