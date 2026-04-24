from datetime import datetime, timezone
import pytest

from logsnip.parser import LogEntry
from logsnip.index_pipeline import IndexPipelineOptions, run_index_pipeline, index_pipeline_summary


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 10, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(line_number=1, timestamp=_ts(0), level="INFO", message="boot"),
        LogEntry(line_number=2, timestamp=_ts(1), level="ERROR", message="disk full"),
        LogEntry(line_number=3, timestamp=_ts(2), level="INFO", message="retry"),
        LogEntry(line_number=4, timestamp=_ts(3), level="DEBUG", message="trace"),
        LogEntry(line_number=5, timestamp=_ts(4), level="ERROR", message="timeout"),
    ]


def test_run_pipeline_no_filter(sample_entries):
    idx = run_index_pipeline(sample_entries)
    assert idx.total == 5


def test_run_pipeline_filter_level(sample_entries):
    opts = IndexPipelineOptions(level="ERROR")
    idx = run_index_pipeline(sample_entries, opts)
    assert idx.total == 2
    assert list(idx.by_level.keys()) == ["ERROR"]


def test_run_pipeline_filter_pattern(sample_entries):
    opts = IndexPipelineOptions(pattern="disk")
    idx = run_index_pipeline(sample_entries, opts)
    assert idx.total == 1


def test_run_pipeline_exclude(sample_entries):
    opts = IndexPipelineOptions(exclude="trace")
    idx = run_index_pipeline(sample_entries, opts)
    assert idx.total == 4
    messages = [e.message for e in idx.entries]
    assert "trace" not in messages


def test_run_pipeline_empty_input():
    idx = run_index_pipeline([])
    assert idx.total == 0
    assert idx.by_level == {}
    assert idx.by_minute == {}


def test_index_pipeline_summary(sample_entries):
    idx = run_index_pipeline(sample_entries)
    summary = index_pipeline_summary(idx)
    assert "5" in summary
    assert "ERROR" in summary
