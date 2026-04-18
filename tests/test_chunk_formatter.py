"""Tests for logsnip.chunk_formatter."""
import json
from datetime import datetime, timezone

import pytest

from logsnip.chunk_formatter import (
    format_chunk_json,
    format_chunk_summary,
    format_chunk_text,
    format_chunks,
)
from logsnip.chunker import Chunk
from logsnip.parser import LogEntry


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_chunk():
    entries = [
        LogEntry(line_number=1, timestamp=_ts(0), level="INFO", message="hello", raw="hello"),
        LogEntry(line_number=2, timestamp=_ts(5), level="ERROR", message="boom", raw="boom"),
    ]
    return Chunk(index=0, entries=entries)


def test_summary_contains_index(sample_chunk):
    s = format_chunk_summary(sample_chunk)
    assert "Chunk 0" in s


def test_summary_contains_size(sample_chunk):
    s = format_chunk_summary(sample_chunk)
    assert "2 entries" in s


def test_summary_contains_timestamps(sample_chunk):
    s = format_chunk_summary(sample_chunk)
    assert "2024-01-01" in s


def test_format_chunk_text_has_header(sample_chunk):
    out = format_chunk_text(sample_chunk, show_header=True)
    assert "Chunk 0" in out
    assert "---" in out


def test_format_chunk_text_no_header(sample_chunk):
    out = format_chunk_text(sample_chunk, show_header=False)
    assert "Chunk" not in out


def test_format_chunk_json_valid(sample_chunk):
    raw = format_chunk_json(sample_chunk)
    data = json.loads(raw)
    assert data["chunk_index"] == 0
    assert data["size"] == 2
    assert len(data["entries"]) == 2


def test_format_chunks_summary(sample_chunk):
    out = format_chunks([sample_chunk, sample_chunk], fmt="summary")
    lines = out.strip().splitlines()
    assert len(lines) == 2


def test_format_chunks_json(sample_chunk):
    out = format_chunks([sample_chunk], fmt="json")
    data = json.loads(out)
    assert isinstance(data, list)
    assert data[0]["size"] == 2
