import pytest
from datetime import datetime
from logsnip.parser import LogEntry
from logsnip.correlator import (
    correlate_entries,
    format_correlation,
    CorrelationGroup,
)
from logsnip.correlate_pipeline import (
    CorrelatePipelineOptions,
    run_correlate_pipeline,
    correlate_summary,
)


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="INFO", message="req_id=abc started", line_number=1),
        LogEntry(timestamp=_ts(1), level="ERROR", message="req_id=abc failed", line_number=2),
        LogEntry(timestamp=_ts(2), level="INFO", message="req_id=xyz started", line_number=3),
        LogEntry(timestamp=_ts(3), level="INFO", message="req_id=xyz finished", line_number=4),
        LogEntry(timestamp=_ts(4), level="DEBUG", message="no id here", line_number=5),
    ]


def test_correlate_entries_group_count(sample_entries):
    groups = correlate_entries(sample_entries, r"req_id=\w+")
    assert len(groups) == 2


def test_correlate_entries_keys(sample_entries):
    groups = correlate_entries(sample_entries, r"req_id=\w+")
    keys = {g.key for g in groups}
    assert keys == {"req_id=abc", "req_id=xyz"}


def test_correlate_entries_counts(sample_entries):
    groups = correlate_entries(sample_entries, r"req_id=\w+")
    by_key = {g.key: g.count for g in groups}
    assert by_key["req_id=abc"] == 2
    assert by_key["req_id=xyz"] == 2


def test_correlate_no_match(sample_entries):
    groups = correlate_entries(sample_entries, r"session=\w+")
    assert groups == []


def test_format_correlation(sample_entries):
    groups = correlate_entries(sample_entries, r"req_id=\w+")
    out = format_correlation(groups)
    assert "req_id=" in out
    assert "started" in out or "failed" in out


def test_pipeline_min_group_size(sample_entries):
    opts = CorrelatePipelineOptions(pattern=r"req_id=\w+", min_group_size=2)
    groups = run_correlate_pipeline(sample_entries, opts)
    assert all(g.count >= 2 for g in groups)


def test_pipeline_level_filter(sample_entries):
    opts = CorrelatePipelineOptions(pattern=r"req_id=\w+", level="error")
    groups = run_correlate_pipeline(sample_entries, opts)
    assert len(groups) == 1
    assert groups[0].key == "req_id=abc"


def test_correlate_summary(sample_entries):
    groups = correlate_entries(sample_entries, r"req_id=\w+")
    summary = correlate_summary(groups)
    assert "2" in summary
    assert "group" in summary
