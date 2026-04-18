"""Tests for logsnip.sorter."""
from datetime import datetime, timezone
from typing import List

import pytest

from logsnip.parser import LogEntry
from logsnip.sorter import SortOptions, sort_entries, sort_by_timestamp, sort_by_level


def _ts(hour: int, minute: int = 0) -> datetime:
    return datetime(2024, 1, 1, hour, minute, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries() -> List[LogEntry]:
    return [
        LogEntry(line_number=3, timestamp=_ts(10, 30), level="ERROR", message="err", raw=""),
        LogEntry(line_number=1, timestamp=_ts(9, 0),  level="INFO",  message="start", raw=""),
        LogEntry(line_number=2, timestamp=_ts(10, 0), level="DEBUG", message="dbg", raw=""),
        LogEntry(line_number=4, timestamp=_ts(9, 45), level="WARNING", message="warn", raw=""),
    ]


def test_sort_by_timestamp_asc(sample_entries):
    result = sort_by_timestamp(sample_entries)
    timestamps = [e.timestamp for e in result]
    assert timestamps == sorted(timestamps)


def test_sort_by_timestamp_desc(sample_entries):
    result = sort_by_timestamp(sample_entries, desc=True)
    timestamps = [e.timestamp for e in result]
    assert timestamps == sorted(timestamps, reverse=True)


def test_sort_by_level_asc(sample_entries):
    result = sort_by_level(sample_entries)
    levels = [e.level.lower() for e in result]
    assert levels[0] == "debug"
    assert levels[-1] == "error"


def test_sort_by_level_desc(sample_entries):
    result = sort_by_level(sample_entries, desc=True)
    assert result[0].level.upper() == "ERROR"


def test_sort_by_line_number(sample_entries):
    opts = SortOptions(key="line_number", order="asc")
    result = sort_entries(sample_entries, opts)
    assert [e.line_number for e in result] == [1, 2, 3, 4]


def test_sort_by_line_number_desc(sample_entries):
    opts = SortOptions(key="line_number", order="desc")
    result = sort_entries(sample_entries, opts)
    assert [e.line_number for e in result] == [4, 3, 2, 1]


def test_sort_empty():
    assert sort_by_timestamp([]) == []


def test_sort_default_options(sample_entries):
    """Default sort: timestamp asc."""
    result = sort_entries(sample_entries)
    assert result[0].message == "start"
