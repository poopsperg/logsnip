"""Tests for logsnip.deduplicator."""
from datetime import datetime, timezone
from typing import List

import pytest

from logsnip.parser import LogEntry
from logsnip.deduplicator import (
    DeduplicateOptions,
    DeduplicateReport,
    deduplicate_entries,
    deduplicate_summary,
    _window_key,
)


def _ts(minute: int, second: int = 0) -> datetime:
    return datetime(2024, 1, 1, 12, minute, second, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries() -> List[LogEntry]:
    return [
        LogEntry(timestamp=_ts(0, 0), level="INFO", message="startup", line_number=1),
        LogEntry(timestamp=_ts(0, 5), level="INFO", message="startup", line_number=2),
        LogEntry(timestamp=_ts(0, 10), level="INFO", message="startup", line_number=3),
        LogEntry(timestamp=_ts(0, 15), level="ERROR", message="disk full", line_number=4),
        LogEntry(timestamp=_ts(0, 20), level="ERROR", message="disk full", line_number=5),
        LogEntry(timestamp=_ts(2, 0), level="INFO", message="startup", line_number=6),
    ]


def test_window_key_same_window():
    t1 = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2024, 1, 1, 12, 0, 59, tzinfo=timezone.utc)
    assert _window_key(t1, 60) == _window_key(t2, 60)


def test_window_key_different_window():
    t1 = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2024, 1, 1, 12, 1, 0, tzinfo=timezone.utc)
    assert _window_key(t1, 60) != _window_key(t2, 60)


def test_deduplicate_drops_repeats(sample_entries):
    opts = DeduplicateOptions(window_seconds=60, max_repeats=1)
    result = list(deduplicate_entries(sample_entries, opts))
    messages = [e.message for e in result]
    assert messages.count("startup") == 2  # once in window 0, once in window 2
    assert messages.count("disk full") == 1


def test_deduplicate_max_repeats_two(sample_entries):
    opts = DeduplicateOptions(window_seconds=60, max_repeats=2)
    result = list(deduplicate_entries(sample_entries, opts))
    messages = [e.message for e in result]
    assert messages.count("startup") == 3  # two in window 0 + one in window 2
    assert messages.count("disk full") == 2


def test_deduplicate_level_filter_skips_others(sample_entries):
    opts = DeduplicateOptions(window_seconds=60, max_repeats=1, level="ERROR")
    result = list(deduplicate_entries(sample_entries, opts))
    # INFO entries are passed through untouched; only ERROR is deduplicated
    info_entries = [e for e in result if e.level == "INFO"]
    assert len(info_entries) == 4  # all INFO kept
    error_entries = [e for e in result if e.level == "ERROR"]
    assert len(error_entries) == 1


def test_deduplicate_pattern_filter(sample_entries):
    opts = DeduplicateOptions(window_seconds=60, max_repeats=1, pattern="disk")
    result = list(deduplicate_entries(sample_entries, opts))
    disk_entries = [e for e in result if "disk" in e.message]
    assert len(disk_entries) == 1
    startup_entries = [e for e in result if e.message == "startup"]
    assert len(startup_entries) == 3  # untouched


def test_deduplicate_empty():
    opts = DeduplicateOptions()
    result = list(deduplicate_entries([], opts))
    assert result == []


def test_summary_report_fields(sample_entries):
    opts = DeduplicateOptions(window_seconds=60, max_repeats=1)
    report = deduplicate_summary(sample_entries, opts)
    assert isinstance(report, DeduplicateReport)
    assert report.total_in == 6
    assert report.total_out < report.total_in
    assert report.dropped == report.total_in - report.total_out
    assert report.windows_seen >= 1


def test_summary_reduction_pct(sample_entries):
    opts = DeduplicateOptions(window_seconds=60, max_repeats=1)
    report = deduplicate_summary(sample_entries, opts)
    assert 0.0 < report.reduction_pct <= 100.0


def test_summary_empty_entries():
    opts = DeduplicateOptions()
    report = deduplicate_summary([], opts)
    assert report.total_in == 0
    assert report.reduction_pct == 0.0
