"""Tests for logsnip.compact_pipeline."""
import pytest
from datetime import datetime, timezone

from logsnip.parser import LogEntry
from logsnip.compact_pipeline import CompactPipelineOptions, run_compact_pipeline, pipeline_summary


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="INFO",  message="start",     line_number=1),
        LogEntry(timestamp=_ts(1), level="INFO",  message="ping",      line_number=2),
        LogEntry(timestamp=_ts(2), level="INFO",  message="ping",      line_number=3),
        LogEntry(timestamp=_ts(3), level="ERROR", message="timeout",   line_number=4),
        LogEntry(timestamp=_ts(4), level="ERROR", message="timeout",   line_number=5),
        LogEntry(timestamp=_ts(5), level="INFO",  message="recovered", line_number=6),
    ]


def test_run_pipeline_returns_compacted(sample_entries):
    result = run_compact_pipeline(sample_entries)
    assert len(result) == 4


def test_run_pipeline_filter_level(sample_entries):
    opts = CompactPipelineOptions(level="ERROR")
    result = run_compact_pipeline(sample_entries, opts)
    assert all(r.level == "ERROR" for r in result)
    assert len(result) == 1
    assert result[0].repeat_count == 2


def test_run_pipeline_filter_pattern(sample_entries):
    opts = CompactPipelineOptions(pattern="ping")
    result = run_compact_pipeline(sample_entries, opts)
    assert len(result) == 1
    assert result[0].message == "ping"


def test_run_pipeline_min_repeats(sample_entries):
    opts = CompactPipelineOptions(min_repeats=2)
    result = run_compact_pipeline(sample_entries, opts)
    assert all(r.repeat_count >= 2 for r in result)


def test_pipeline_summary_string(sample_entries):
    result = run_compact_pipeline(sample_entries)
    summary = pipeline_summary(result)
    assert "original=" in summary
    assert "compacted=" in summary
    assert "repeated_groups=" in summary
    assert "max_repeats=" in summary


def test_run_pipeline_empty():
    result = run_compact_pipeline([])
    assert result == []
