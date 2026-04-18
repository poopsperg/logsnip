"""Tests for logsnip.dedup module."""
from datetime import datetime, timezone
from typing import List

import pytest

from logsnip.parser import LogEntry
from logsnip.dedup import dedup_entries, dedup_consecutive, count_duplicates


def _ts(hour: int, minute: int = 0) -> datetime:
    return datetime(2024, 1, 1, hour, minute, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries() -> List[LogEntry]:
    return [
        LogEntry(timestamp=_ts(10), level="INFO", message="startup", line_number=1),
        LogEntry(timestamp=_ts(10, 1), level="INFO", message="startup", line_number=2),
        LogEntry(timestamp=_ts(10, 2), level="ERROR", message="boom", line_number=3),
        LogEntry(timestamp=_ts(10, 3), level="INFO", message="startup", line_number=4),
        LogEntry(timestamp=_ts(10, 4), level="ERROR", message="boom", line_number=5),
    ]


def test_dedup_entries_removes_duplicates(sample_entries):
    result = list(dedup_entries(sample_entries))
    assert len(result) == 2


def test_dedup_entries_keeps_first(sample_entries):
    result = list(dedup_entries(sample_entries))
    assert result[0].line_number == 1
    assert result[1].line_number == 3


def test_dedup_entries_empty():
    assert list(dedup_entries([])) == []


def test_dedup_entries_no_duplicates():
    entries = [
        LogEntry(timestamp=_ts(10), level="INFO", message="a", line_number=1),
        LogEntry(timestamp=_ts(11), level="WARN", message="b", line_number=2),
    ]
    assert len(list(dedup_entries(entries))) == 2


def test_dedup_consecutive_only_adjacent(sample_entries):
    # startup, startup, boom, startup, boom -> startup, boom, startup, boom
    result = list(dedup_consecutive(sample_entries))
    assert len(result) == 4


def test_dedup_consecutive_messages(sample_entries):
    result = list(dedup_consecutive(sample_entries))
    messages = [e.message for e in result]
    assert messages == ["startup", "boom", "startup", "boom"]


def test_count_duplicates_correct(sample_entries):
    assert count_duplicates(sample_entries) == 3


def test_count_duplicates_no_dups():
    entries = [
        LogEntry(timestamp=_ts(10), level="INFO", message="x", line_number=1),
        LogEntry(timestamp=_ts(11), level="INFO", message="y", line_number=2),
    ]
    assert count_duplicates(entries) == 0


def test_dedup_custom_fields(sample_entries):
    # dedup on message only — same as default behaviour here
    result = list(dedup_entries(sample_entries, fields=["message"]))
    assert len(result) == 2
