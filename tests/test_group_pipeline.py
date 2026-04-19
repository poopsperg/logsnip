import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.group_pipeline import GroupPipelineOptions, run_group_pipeline, pipeline_summary


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 10, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="INFO", message="started", line_number=1),
        LogEntry(timestamp=_ts(1), level="ERROR", message="failed hard", line_number=2),
        LogEntry(timestamp=_ts(2), level="INFO", message="retry ok", line_number=3),
        LogEntry(timestamp=_ts(3), level="WARN", message="slow", line_number=4),
        LogEntry(timestamp=_ts(4), level="ERROR", message="failed again", line_number=5),
    ]


def test_run_pipeline_returns_groups(sample_entries):
    groups = run_group_pipeline(sample_entries)
    assert "INFO" in groups
    assert "ERROR" in groups


def test_run_pipeline_filter_level(sample_entries):
    opts = GroupPipelineOptions(level="error")
    groups = run_group_pipeline(sample_entries, opts)
    assert set(groups.keys()) == {"ERROR"}
    assert groups["ERROR"].count == 2


def test_run_pipeline_filter_pattern(sample_entries):
    opts = GroupPipelineOptions(pattern="failed")
    groups = run_group_pipeline(sample_entries, opts)
    total = sum(g.count for g in groups.values())
    assert total == 2


def test_run_pipeline_min_size(sample_entries):
    opts = GroupPipelineOptions(min_size=2)
    groups = run_group_pipeline(sample_entries, opts)
    assert "WARN" not in groups


def test_pipeline_summary_string(sample_entries):
    groups = run_group_pipeline(sample_entries)
    summary = pipeline_summary(groups)
    assert isinstance(summary, str)
    assert "Groups:" in summary
