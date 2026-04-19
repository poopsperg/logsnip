"""Tests for logsnip.differ and logsnip.diff_pipeline."""
import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.differ import diff_entries, format_diff, DiffResult
from logsnip.diff_pipeline import DiffPipelineOptions, run_diff_pipeline, diff_summary


def _ts(hour: int):
    return datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def stream_a():
    return [
        LogEntry(line_number=1, timestamp=_ts(1), level="INFO", message="startup complete"),
        LogEntry(line_number=2, timestamp=_ts(2), level="ERROR", message="disk full"),
        LogEntry(line_number=3, timestamp=_ts(3), level="INFO", message="shutdown"),
    ]


@pytest.fixture
def stream_b():
    return [
        LogEntry(line_number=1, timestamp=_ts(1), level="INFO", message="startup complete"),
        LogEntry(line_number=2, timestamp=_ts(2), level="WARN", message="low memory"),
        LogEntry(line_number=3, timestamp=_ts(3), level="INFO", message="shutdown"),
    ]


def test_diff_common_count(stream_a, stream_b):
    result = diff_entries(stream_a, stream_b)
    assert len(result.common) == 2


def test_diff_only_a(stream_a, stream_b):
    result = diff_entries(stream_a, stream_b)
    assert len(result.only_in_a) == 1
    assert result.only_in_a[0].message == "disk full"


def test_diff_only_b(stream_a, stream_b):
    result = diff_entries(stream_a, stream_b)
    assert len(result.only_in_b) == 1
    assert result.only_in_b[0].message == "low memory"


def test_diff_totals(stream_a, stream_b):
    result = diff_entries(stream_a, stream_b)
    assert result.total_a == 3
    assert result.total_b == 3


def test_diff_identical():
    entries = [LogEntry(line_number=1, timestamp=_ts(1), level="INFO", message="hello")]
    result = diff_entries(entries, entries)
    assert len(result.common) == 1
    assert result.only_in_a == []
    assert result.only_in_b == []


def test_format_diff_contains_counts(stream_a, stream_b):
    result = diff_entries(stream_a, stream_b)
    text = format_diff(result)
    assert "Common" in text
    assert "Only in A" in text
    assert "disk full" in text


def test_pipeline_with_level_filter(stream_a, stream_b):
    opts = DiffPipelineOptions(level="ERROR")
    result = run_diff_pipeline(stream_a, stream_b, opts)
    assert len(result.only_in_a) == 1
    assert result.only_in_a[0].message == "disk full"


def test_diff_summary_keys(stream_a, stream_b):
    result = diff_entries(stream_a, stream_b)
    s = diff_summary(result)
    assert set(s.keys()) == {"common", "only_in_a", "only_in_b", "total_a", "total_b"}
