"""Tests for logsnip.merger."""
import datetime
import pytest

from logsnip.parser import LogEntry
from logsnip.merger import MergeOptions, merge_entries, merge_files_entries


def _ts(hour: int, minute: int = 0) -> datetime.datetime:
    return datetime.datetime(2024, 1, 1, hour, minute, 0)


@pytest.fixture
def stream_a():
    return [
        LogEntry(timestamp=_ts(1), level="INFO", message="a1", raw="", line_number=1),
        LogEntry(timestamp=_ts(3), level="WARN", message="a2", raw="", line_number=2),
        LogEntry(timestamp=_ts(5), level="INFO", message="a3", raw="", line_number=3),
    ]


@pytest.fixture
def stream_b():
    return [
        LogEntry(timestamp=_ts(2), level="ERROR", message="b1", raw="", line_number=10),
        LogEntry(timestamp=_ts(4), level="INFO",  message="b2", raw="", line_number=11),
        LogEntry(timestamp=_ts(6), level="DEBUG", message="b3", raw="", line_number=12),
    ]


def test_merge_count(stream_a, stream_b):
    result = merge_files_entries([stream_a, stream_b])
    assert len(result) == 6


def test_merge_order(stream_a, stream_b):
    result = merge_files_entries([stream_a, stream_b])
    timestamps = [e.timestamp for e in result]
    assert timestamps == sorted(timestamps)


def test_merge_messages_interleaved(stream_a, stream_b):
    result = merge_files_entries([stream_a, stream_b])
    messages = [e.message for e in result]
    assert messages == ["a1", "b1", "a2", "b2", "a3", "b3"]


def test_merge_single_stream(stream_a):
    result = merge_files_entries([stream_a])
    assert [e.message for e in result] == ["a1", "a2", "a3"]


def test_merge_empty_streams():
    result = merge_files_entries([[], []])
    assert result == []


def test_merge_one_empty(stream_a):
    result = merge_files_entries([stream_a, []])
    assert len(result) == 3


def test_merge_dedup_removes_duplicates():
    ts = _ts(1)
    entry = LogEntry(timestamp=ts, level="INFO", message="dup", raw="", line_number=1)
    duplicate = LogEntry(timestamp=ts, level="INFO", message="dup", raw="", line_number=2)
    opts = MergeOptions(deduplicate=True)
    result = merge_files_entries([[entry], [duplicate]], options=opts)
    assert len(result) == 1


def test_merge_dedup_keeps_unique():
    a = LogEntry(timestamp=_ts(1), level="INFO", message="x", raw="", line_number=1)
    b = LogEntry(timestamp=_ts(1), level="INFO", message="y", raw="", line_number=2)
    opts = MergeOptions(deduplicate=True)
    result = merge_files_entries([[a], [b]], options=opts)
    assert len(result) == 2
