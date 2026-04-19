"""Tests for logsnip.filter module."""
from datetime import datetime, timezone
from typing import List

import pytest

from logsnip.parser import LogEntry
from logsnip.filter import (
    filter_by_level,
    filter_by_pattern,
    filter_by_exclude,
    apply_filters,
)


def _ts(hour: int) -> datetime:
    return datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries() -> List[LogEntry]:
    return [
        LogEntry(timestamp=_ts(1), level="INFO", message="service started", line_number=1),
        LogEntry(timestamp=_ts(2), level="DEBUG", message="connecting to db", line_number=2),
        LogEntry(timestamp=_ts(3), level="ERROR", message="connection refused", line_number=3),
        LogEntry(timestamp=_ts(4), level="INFO", message="retrying connection", line_number=4),
        LogEntry(timestamp=_ts(5), level="WARN", message="slow query detected", line_number=5),
    ]


def test_filter_by_level_single(sample_entries):
    result = list(filter_by_level(sample_entries, ["ERROR"]))
    assert len(result) == 1
    assert result[0].level == "ERROR"


def test_filter_by_level_multiple(sample_entries):
    result = list(filter_by_level(sample_entries, ["INFO", "WARN"]))
    assert len(result) == 3


def test_filter_by_level_case_insensitive(sample_entries):
    result = list(filter_by_level(sample_entries, ["info"]))
    assert len(result) == 2


def test_filter_by_level_no_match(sample_entries):
    result = list(filter_by_level(sample_entries, ["CRITICAL"]))
    assert result == []


def test_filter_by_pattern_found(sample_entries):
    result = list(filter_by_pattern(sample_entries, r"connect"))
    assert len(result) == 2


def test_filter_by_pattern_ignore_case(sample_entries):
    result = list(filter_by_pattern(sample_entries, r"CONNECTION", ignore_case=True))
    assert len(result) == 2


def test_filter_by_pattern_not_found(sample_entries):
    result = list(filter_by_pattern(sample_entries, r"timeout"))
    assert result == []


def test_filter_by_exclude(sample_entries):
    result = list(filter_by_exclude(sample_entries, r"connect"))
    assert len(result) == 3
    assert all("connect" not in e.message for e in result)


def test_filter_by_exclude_no_match(sample_entries):
    """Excluding a pattern that matches nothing should return all entries."""
    result = list(filter_by_exclude(sample_entries, r"timeout"))
    assert len(result) == len(sample_entries)


def test_filter_by_exclude_all_match(sample_entries):
    """Excluding a pattern that matches everything should return empty list."""
    result = list(filter_by_exclude(sample_entries, r"."))
    assert result == []


def test_apply_filters_combined(sample_entries):
    result = list(apply_filters(sample_entries, levels=["INFO"], pattern=r"retry"))
    assert len(result) == 1
    assert result[0].message == "retrying connection"


def test_apply_filters_no_filters(sample_entries):
    result = list(apply_filters(sample_entries))
    assert len(result) == len(sample_entries)
