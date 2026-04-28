"""Tests for logsnip.stats."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from logsnip.parser import LogEntry
from logsnip.stats import LogStats, compute_stats, format_stats


def _ts(hour: int, minute: int = 0) -> datetime:
    return datetime(2024, 1, 1, hour, minute, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries() -> list[LogEntry]:
    return [
        LogEntry(line_no=1, timestamp=_ts(10), level="INFO", source="app", message="started"),
        LogEntry(line_no=2, timestamp=_ts(10, 5), level="DEBUG", source="app", message="debug msg"),
        LogEntry(line_no=3, timestamp=_ts(10, 10), level="ERROR", source="db", message="connection failed"),
        LogEntry(line_no=4, timestamp=_ts(10, 15), level="info", source="app", message="done"),
    ]


def test_compute_stats_total(sample_entries):
    stats = compute_stats(sample_entries)
    assert stats.total == 4


def test_compute_stats_by_level(sample_entries):
    stats = compute_stats(sample_entries)
    assert stats.by_level["INFO"] == 2
    assert stats.by_level["DEBUG"] == 1
    assert stats.by_level["ERROR"] == 1


def test_compute_stats_timestamps(sample_entries):
    stats = compute_stats(sample_entries)
    assert "10:00" in stats.first_timestamp
    assert "10:15" in stats.last_timestamp


def test_compute_stats_unique_sources(sample_entries):
    stats = compute_stats(sample_entries)
    assert stats.unique_sources == 2


def test_compute_stats_empty():
    stats = compute_stats([])
    assert stats.total == 0
    assert stats.by_level == {}
    assert stats.first_timestamp is None
    assert stats.last_timestamp is None
    assert stats.unique_sources == 0


def test_as_dict(sample_entries):
    stats = compute_stats(sample_entries)
    d = stats.as_dict()
    assert d["total"] == 4
    assert isinstance(d["by_level"], dict)


def test_format_stats_contains_total(sample_entries):
    stats = compute_stats(sample_entries)
    text = format_stats(stats)
    assert "Total entries" in text
    assert "4" in text


def test_format_stats_contains_levels(sample_entries):
    stats = compute_stats(sample_entries)
    text = format_stats(stats)
    assert "ERROR" in text
    assert "DEBUG" in text


def test_format_stats_empty():
    """format_stats should handle an empty stats object without crashing."""
    stats = compute_stats([])
    text = format_stats(stats)
    assert "Total entries" in text
    assert "0" in text
