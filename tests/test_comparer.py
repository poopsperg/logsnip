import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.comparer import (
    CompareOptions,
    compare_entries,
    compare_summary,
)
from logsnip.compare_pipeline import ComparePipelineOptions, run_compare_pipeline


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def stream_a():
    return [
        LogEntry(timestamp=_ts(0), level="INFO", message="startup complete", line_number=1),
        LogEntry(timestamp=_ts(1), level="WARN", message="disk space low", line_number=2),
        LogEntry(timestamp=_ts(2), level="ERROR", message="connection refused", line_number=3),
    ]


@pytest.fixture
def stream_b():
    return [
        LogEntry(timestamp=_ts(0), level="INFO", message="startup complete", line_number=1),
        LogEntry(timestamp=_ts(3), level="DEBUG", message="cache miss", line_number=2),
        LogEntry(timestamp=_ts(4), level="ERROR", message="timeout exceeded", line_number=3),
    ]


def test_compare_common_messages(stream_a, stream_b):
    result = compare_entries(stream_a, stream_b)
    assert "startup complete" in result.common_messages


def test_compare_only_in_a(stream_a, stream_b):
    result = compare_entries(stream_a, stream_b)
    messages = [e.message for e in result.only_in_a]
    assert "disk space low" in messages
    assert "connection refused" in messages


def test_compare_only_in_b(stream_a, stream_b):
    result = compare_entries(stream_a, stream_b)
    messages = [e.message for e in result.only_in_b]
    assert "cache miss" in messages
    assert "timeout exceeded" in messages


def test_compare_totals(stream_a, stream_b):
    result = compare_entries(stream_a, stream_b)
    assert result.total_a == 3
    assert result.total_b == 3


def test_compare_overlap_count(stream_a, stream_b):
    result = compare_entries(stream_a, stream_b)
    assert result.overlap_count == 1


def test_compare_labels(stream_a, stream_b):
    result = compare_entries(stream_a, stream_b, label_a="prod", label_b="staging")
    assert result.label_a == "prod"
    assert result.label_b == "staging"


def test_compare_with_level_filter(stream_a, stream_b):
    opts = CompareOptions(level="ERROR")
    result = compare_entries(stream_a, stream_b, opts=opts)
    assert result.total_a == 1
    assert result.total_b == 1


def test_compare_summary_contains_labels(stream_a, stream_b):
    result = compare_entries(stream_a, stream_b, label_a="X", label_b="Y")
    summary = compare_summary(result)
    assert "X" in summary
    assert "Y" in summary


def test_pipeline_basic(stream_a, stream_b):
    opts = ComparePipelineOptions(label_a="A", label_b="B")
    result = run_compare_pipeline(stream_a, stream_b, opts=opts)
    assert result.total_a == 3
    assert result.total_b == 3


def test_pipeline_with_filter(stream_a, stream_b):
    opts = ComparePipelineOptions(level="INFO")
    result = run_compare_pipeline(stream_a, stream_b, opts=opts)
    assert result.total_a == 1
    assert result.total_b == 1
    assert result.overlap_count == 1
