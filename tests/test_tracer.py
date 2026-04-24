import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.tracer import (
    TraceOptions,
    TraceSpan,
    extract_trace_id,
    trace_entries,
    trace_summary,
)
from logsnip.trace_pipeline import TracePipelineOptions, run_trace_pipeline


def _ts(minute: int) -> float:
    return datetime(2024, 1, 1, 0, minute, 0, tzinfo=timezone.utc).timestamp()


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="INFO", message="start trace_id=abc123", line=1),
        LogEntry(timestamp=_ts(1), level="DEBUG", message="processing trace_id=abc123", line=2),
        LogEntry(timestamp=_ts(2), level="ERROR", message="failed trace_id=abc123", line=3),
        LogEntry(timestamp=_ts(3), level="INFO", message="start trace_id=xyz789", line=4),
        LogEntry(timestamp=_ts(4), level="INFO", message="no trace here", line=5),
    ]


def test_extract_trace_id_found():
    tid = extract_trace_id("request trace_id=abc123 done", r"trace[_-]?id[=:]\s*([\w-]+)")
    assert tid == "abc123"


def test_extract_trace_id_not_found():
    tid = extract_trace_id("no trace info here", r"trace[_-]?id[=:]\s*([\w-]+)")
    assert tid is None


def test_trace_entries_group_count(sample_entries):
    spans = trace_entries(sample_entries)
    assert len(spans) == 2


def test_trace_entries_span_size(sample_entries):
    spans = trace_entries(sample_entries)
    assert spans["abc123"].count == 3
    assert spans["xyz789"].count == 1


def test_trace_span_duration(sample_entries):
    spans = trace_entries(sample_entries)
    span = spans["abc123"]
    assert span.duration == pytest.approx(_ts(2) - _ts(0))


def test_trace_span_levels(sample_entries):
    spans = trace_entries(sample_entries)
    assert spans["abc123"].levels == ["INFO", "DEBUG", "ERROR"]


def test_min_span_size_filters(sample_entries):
    opts = TraceOptions(min_span_size=2)
    spans = trace_entries(sample_entries, opts)
    assert "xyz789" not in spans
    assert "abc123" in spans


def test_trace_summary_no_spans():
    result = trace_summary({})
    assert "No trace" in result


def test_trace_summary_with_spans(sample_entries):
    spans = trace_entries(sample_entries)
    result = trace_summary(spans)
    assert "abc123" in result
    assert "entries=3" in result


def test_run_trace_pipeline_filter_level(sample_entries):
    opts = TracePipelineOptions(level="ERROR")
    spans = run_trace_pipeline(sample_entries, opts)
    assert "abc123" in spans
    assert spans["abc123"].count == 1
    assert spans["abc123"].levels == ["ERROR"]
