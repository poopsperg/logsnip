import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.profile_pipeline import ProfilePipelineOptions, run_profile_pipeline, profile_summary


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(line_number=1, timestamp=_ts(0), level="INFO", message="service boot"),
        LogEntry(line_number=2, timestamp=_ts(1), level="ERROR", message="service error"),
        LogEntry(line_number=3, timestamp=_ts(2), level="INFO", message="service ok"),
        LogEntry(line_number=4, timestamp=_ts(3), level="DEBUG", message="service debug"),
    ]


def test_run_pipeline_total(sample_entries):
    opts = ProfilePipelineOptions()
    report = run_profile_pipeline(sample_entries, opts)
    assert report.total == 4


def test_run_pipeline_filter_level(sample_entries):
    opts = ProfilePipelineOptions(level="INFO")
    report = run_profile_pipeline(sample_entries, opts)
    assert report.total == 2
    assert "INFO" in report.level_counts
    assert "ERROR" not in report.level_counts


def test_run_pipeline_filter_pattern(sample_entries):
    opts = ProfilePipelineOptions(pattern="error")
    report = run_profile_pipeline(sample_entries, opts)
    assert report.total == 1


def test_run_pipeline_empty_after_filter(sample_entries):
    opts = ProfilePipelineOptions(pattern="nonexistent")
    report = run_profile_pipeline(sample_entries, opts)
    assert report.total == 0
    assert report.first_ts is None


def test_profile_summary_string(sample_entries):
    opts = ProfilePipelineOptions()
    report = run_profile_pipeline(sample_entries, opts)
    summary = profile_summary(report)
    assert isinstance(summary, str)
    assert len(summary) > 0
