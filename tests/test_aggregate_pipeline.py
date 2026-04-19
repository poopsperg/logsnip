"""Tests for logsnip.aggregate_pipeline."""
import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.aggregate_pipeline import (
    AggregatePipelineOptions,
    run_aggregate_pipeline,
    aggregate_summary,
)


def _ts(offset: int) -> datetime:
    return datetime(2024, 1, 1, 0, offset // 60, offset % 60, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(line_no=i, timestamp=_ts(i * 30), level="INFO", message=f"msg {i}")
        for i in range(8)
    ]


def test_run_pipeline_returns_buckets(sample_entries):
    opts = AggregatePipelineOptions(window_seconds=60)
    buckets = run_aggregate_pipeline(sample_entries, opts)
    assert len(buckets) >= 1


def test_run_pipeline_min_bucket_size(sample_entries):
    opts = AggregatePipelineOptions(window_seconds=10, min_bucket_size=5)
    buckets = run_aggregate_pipeline(sample_entries, opts)
    for b in buckets:
        assert b.count >= 5


def test_run_pipeline_group_by_level(sample_entries):
    opts = AggregatePipelineOptions(group_by_level=True)
    buckets = run_aggregate_pipeline(sample_entries, opts)
    keys = {b.key for b in buckets}
    assert "INFO" in keys


def test_summary_buckets_count(sample_entries):
    opts = AggregatePipelineOptions(window_seconds=60)
    buckets = run_aggregate_pipeline(sample_entries, opts)
    summary = aggregate_summary(buckets)
    assert summary["buckets"] == len(buckets)


def test_summary_total_entries(sample_entries):
    opts = AggregatePipelineOptions(window_seconds=3600)
    buckets = run_aggregate_pipeline(sample_entries, opts)
    summary = aggregate_summary(buckets)
    assert summary["total_entries"] == len(sample_entries)


def test_summary_empty():
    summary = aggregate_summary([])
    assert summary["buckets"] == 0
    assert summary["avg_bucket_size"] == 0
