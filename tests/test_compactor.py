"""Tests for logsnip.compactor."""
import pytest
from datetime import datetime, timezone

from logsnip.parser import LogEntry
from logsnip.compactor import (
    CompactOptions,
    CompactedEntry,
    compact_entries,
    compact_summary,
)


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="INFO",  message="startup",    line_number=1),
        LogEntry(timestamp=_ts(1), level="INFO",  message="heartbeat",  line_number=2),
        LogEntry(timestamp=_ts(2), level="INFO",  message="heartbeat",  line_number=3),
        LogEntry(timestamp=_ts(3), level="INFO",  message="heartbeat",  line_number=4),
        LogEntry(timestamp=_ts(4), level="ERROR", message="disk full",  line_number=5),
        LogEntry(timestamp=_ts(5), level="ERROR", message="disk full",  line_number=6),
        LogEntry(timestamp=_ts(6), level="INFO",  message="shutdown",   line_number=7),
    ]


def test_compact_reduces_count(sample_entries):
    result = list(compact_entries(sample_entries))
    assert len(result) == 4  # startup, heartbeat(x3), disk full(x2), shutdown


def test_compact_repeat_counts(sample_entries):
    result = list(compact_entries(sample_entries))
    counts = {r.message: r.repeat_count for r in result}
    assert counts["heartbeat"] == 3
    assert counts["disk full"] == 2
    assert counts["startup"] == 1
    assert counts["shutdown"] == 1


def test_compact_preserves_first_entry(sample_entries):
    result = list(compact_entries(sample_entries))
    heartbeat = next(r for r in result if r.message == "heartbeat")
    assert heartbeat.entry.line_number == 2


def test_compact_is_repeated_flag(sample_entries):
    result = list(compact_entries(sample_entries))
    repeated = [r for r in result if r.is_repeated]
    assert len(repeated) == 2


def test_compact_ignore_level():
    entries = [
        LogEntry(timestamp=_ts(0), level="INFO",  message="same", line_number=1),
        LogEntry(timestamp=_ts(1), level="ERROR", message="same", line_number=2),
    ]
    opts = CompactOptions(ignore_level=True)
    result = list(compact_entries(entries, opts))
    assert len(result) == 1
    assert result[0].repeat_count == 2


def test_compact_min_repeats_filters(sample_entries):
    opts = CompactOptions(min_repeats=2)
    result = list(compact_entries(sample_entries, opts))
    assert all(r.repeat_count >= 2 for r in result)
    messages = {r.message for r in result}
    assert "heartbeat" in messages
    assert "disk full" in messages
    assert "startup" not in messages


def test_compact_empty():
    result = list(compact_entries([]))
    assert result == []


def test_compact_summary(sample_entries):
    result = list(compact_entries(sample_entries))
    s = compact_summary(result)
    assert s["total_original"] == 7
    assert s["total_compacted"] == 4
    assert s["repeated_groups"] == 2
    assert s["max_repeats"] == 3


def test_compact_summary_empty():
    s = compact_summary([])
    assert s["total_original"] == 0
    assert s["max_repeats"] == 0
