"""Tests for logsnip.normalizer and logsnip.normalize_pipeline."""
from datetime import datetime, timezone, timedelta

import pytest

from logsnip.parser import LogEntry
from logsnip.normalizer import (
    NormalizeOptions,
    normalize_level,
    normalize_entry,
    normalize_entries,
    normalize_summary,
)
from logsnip.normalize_pipeline import NormalizePipelineOptions, run_normalize_pipeline


def _ts(hour: int, minute: int = 0) -> datetime:
    return datetime(2024, 1, 1, hour, minute, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(10), level="warn", message="  disk low  ", raw="", line=1),
        LogEntry(timestamp=_ts(10, 1), level="err", message="connection failed", raw="", line=2),
        LogEntry(timestamp=_ts(10, 2), level="INFO", message="started", raw="", line=3),
        LogEntry(timestamp=_ts(10, 3), level="dbg", message="verbose output", raw="", line=4),
    ]


def test_normalize_level_aliases():
    assert normalize_level("warn") == "WARNING"
    assert normalize_level("err") == "ERROR"
    assert normalize_level("fatal") == "CRITICAL"
    assert normalize_level("dbg") == "DEBUG"


def test_normalize_level_passthrough():
    assert normalize_level("INFO") == "INFO"
    assert normalize_level("NOTICE") == "NOTICE"


def test_normalize_entry_strips_message(sample_entries):
    opts = NormalizeOptions(strip_message=True)
    result = normalize_entry(sample_entries[0], opts)
    assert result.message == "disk low"


def test_normalize_entry_canonical_level(sample_entries):
    opts = NormalizeOptions(canonical_level=True)
    result = normalize_entry(sample_entries[0], opts)
    assert result.level == "WARNING"


def test_normalize_entry_max_message_length(sample_entries):
    opts = NormalizeOptions(max_message_length=4, strip_message=False)
    result = normalize_entry(sample_entries[1], opts)
    assert len(result.message) == 4


def test_normalize_entry_utc_conversion():
    tz_plus2 = timezone(timedelta(hours=2))
    entry = LogEntry(timestamp=datetime(2024, 1, 1, 12, 0, tzinfo=tz_plus2), level="INFO", message="hi", raw="", line=1)
    opts = NormalizeOptions(utc_timestamps=True)
    result = normalize_entry(entry, opts)
    assert result.timestamp.tzinfo == timezone.utc
    assert result.timestamp.hour == 10


def test_normalize_entries_count(sample_entries):
    result = list(normalize_entries(sample_entries))
    assert len(result) == len(sample_entries)


def test_normalize_entries_all_levels_canonical(sample_entries):
    result = list(normalize_entries(sample_entries))
    for entry in result:
        assert entry.level == entry.level.upper()


def test_normalize_summary_contains_count(sample_entries):
    result = list(normalize_entries(sample_entries))
    summary = normalize_summary(sample_entries, result)
    assert str(len(result)) in summary


def test_run_pipeline_returns_all(sample_entries):
    opts = NormalizePipelineOptions()
    result = run_normalize_pipeline(sample_entries, opts)
    assert len(result) == len(sample_entries)


def test_run_pipeline_filter_level(sample_entries):
    opts = NormalizePipelineOptions(level="err")
    result = run_normalize_pipeline(sample_entries, opts)
    assert all(e.level == "ERROR" for e in result)
    assert len(result) == 1


def test_run_pipeline_filter_pattern(sample_entries):
    opts = NormalizePipelineOptions(pattern="disk")
    result = run_normalize_pipeline(sample_entries, opts)
    assert len(result) == 1
    assert "disk" in result[0].message
