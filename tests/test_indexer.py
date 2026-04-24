from datetime import datetime, timezone
import pytest

from logsnip.parser import LogEntry
from logsnip.indexer import build_index, index_summary, _minute_key


def _ts(minute: int, second: int = 0) -> datetime:
    return datetime(2024, 1, 1, 12, minute, second, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(line_number=1, timestamp=_ts(0), level="INFO", message="started"),
        LogEntry(line_number=2, timestamp=_ts(0, 30), level="DEBUG", message="debug msg"),
        LogEntry(line_number=3, timestamp=_ts(1), level="ERROR", message="oops"),
        LogEntry(line_number=4, timestamp=_ts(1, 15), level="INFO", message="recovered"),
        LogEntry(line_number=5, timestamp=_ts(2), level="WARN", message="slow query"),
    ]


def test_build_index_total(sample_entries):
    idx = build_index(sample_entries)
    assert idx.total == 5


def test_build_index_by_level_keys(sample_entries):
    idx = build_index(sample_entries)
    assert set(idx.by_level.keys()) == {"INFO", "DEBUG", "ERROR", "WARN"}


def test_build_index_by_level_counts(sample_entries):
    idx = build_index(sample_entries)
    assert len(idx.by_level["INFO"]) == 2
    assert len(idx.by_level["ERROR"]) == 1


def test_lookup_level_returns_entries(sample_entries):
    idx = build_index(sample_entries)
    results = idx.lookup_level("info")
    assert len(results) == 2
    assert all(e.level == "INFO" for e in results)


def test_lookup_level_unknown_returns_empty(sample_entries):
    idx = build_index(sample_entries)
    assert idx.lookup_level("CRITICAL") == []


def test_build_index_by_minute(sample_entries):
    idx = build_index(sample_entries)
    assert len(idx.by_minute) == 3


def test_lookup_minute(sample_entries):
    idx = build_index(sample_entries)
    key = "2024-01-01T12:01"
    results = idx.lookup_minute(key)
    assert len(results) == 2


def test_index_summary_contains_total(sample_entries):
    idx = build_index(sample_entries)
    summary = index_summary(idx)
    assert "5" in summary


def test_index_summary_contains_minutes(sample_entries):
    idx = build_index(sample_entries)
    summary = index_summary(idx)
    assert "minutes spanned: 3" in summary


def test_minute_key_format():
    ts = datetime(2024, 6, 15, 9, 5, 42, tzinfo=None)
    assert _minute_key(ts) == "2024-06-15T09:05"
