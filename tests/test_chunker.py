"""Tests for logsnip.chunker."""
from datetime import datetime, timedelta, timezone

import pytest

from logsnip.chunker import Chunk, chunk_by_size, chunk_by_time
from logsnip.parser import LogEntry


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    levels = ["INFO", "WARN", "ERROR", "DEBUG", "INFO", "ERROR"]
    msgs = [f"msg {i}" for i in range(6)]
    return [
        LogEntry(line_number=i + 1, timestamp=_ts(i * 2), level=levels[i], message=msgs[i], raw=msgs[i])
        for i in range(6)
    ]


def test_chunk_by_size_basic(sample_entries):
    chunks = list(chunk_by_size(sample_entries, 2))
    assert len(chunks) == 3
    assert all(c.size == 2 for c in chunks)


def test_chunk_by_size_remainder(sample_entries):
    chunks = list(chunk_by_size(sample_entries, 4))
    assert len(chunks) == 2
    assert chunks[0].size == 4
    assert chunks[1].size == 2


def test_chunk_by_size_invalid():
    with pytest.raises(ValueError):
        list(chunk_by_size([], 0))


def test_chunk_by_size_indices(sample_entries):
    chunks = list(chunk_by_size(sample_entries, 3))
    assert chunks[0].index == 0
    assert chunks[1].index == 3


def test_chunk_by_time_basic(sample_entries):
    # entries at minutes 0,2,4,6,8,10 — window of 6 minutes => groups: [0,2,4], [6,8,10]
    chunks = list(chunk_by_time(sample_entries, timedelta(minutes=6)))
    assert len(chunks) == 2
    assert chunks[0].size == 3
    assert chunks[1].size == 3


def test_chunk_by_time_single_window(sample_entries):
    chunks = list(chunk_by_time(sample_entries, timedelta(hours=1)))
    assert len(chunks) == 1
    assert chunks[0].size == 6


def test_chunk_by_time_empty():
    chunks = list(chunk_by_time([], timedelta(minutes=5)))
    assert chunks == []


def test_chunk_by_time_invalid(sample_entries):
    with pytest.raises(ValueError):
        list(chunk_by_time(sample_entries, timedelta(seconds=0)))


def test_chunk_start_end(sample_entries):
    chunks = list(chunk_by_size(sample_entries, 3))
    assert chunks[0].start == _ts(0)
    assert chunks[0].end == _ts(4)
