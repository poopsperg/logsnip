"""Tests for logsnip.detect_pipeline."""
from datetime import datetime, timezone
import pytest
from logsnip.parser import LogEntry
from logsnip.detect_pipeline import DetectPipelineOptions, run_detect_pipeline, detect_pipeline_summary


def _ts(second: int) -> datetime:
    return datetime(2024, 1, 1, 12, 0, second, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    repeated_errors = [
        LogEntry(timestamp=_ts(i), level="ERROR", message="connection refused", line=i)
        for i in range(4)
    ]
    info_entries = [
        LogEntry(timestamp=_ts(10 + i), level="INFO", message=f"ok {i}", line=10 + i)
        for i in range(3)
    ]
    return repeated_errors + info_entries


def test_run_pipeline_returns_anomalies(sample_entries):
    opts = DetectPipelineOptions(min_occurrences=3)
    result = run_detect_pipeline(sample_entries, opts)
    assert len(result) >= 1


def test_run_pipeline_filter_level(sample_entries):
    opts = DetectPipelineOptions(level="INFO", min_occurrences=2)
    result = run_detect_pipeline(sample_entries, opts)
    assert all(a.level == "INFO" for a in result)


def test_run_pipeline_top_n(sample_entries):
    opts = DetectPipelineOptions(min_occurrences=2, top_n=1)
    result = run_detect_pipeline(sample_entries, opts)
    assert len(result) <= 1


def test_run_pipeline_no_anomalies_when_threshold_high(sample_entries):
    opts = DetectPipelineOptions(min_occurrences=100)
    result = run_detect_pipeline(sample_entries, opts)
    assert result == []


def test_pipeline_summary_format(sample_entries):
    opts = DetectPipelineOptions(min_occurrences=3)
    anomalies = run_detect_pipeline(sample_entries, opts)
    summary = detect_pipeline_summary(anomalies)
    assert "anomalies=" in summary
    assert "max_score=" in summary
