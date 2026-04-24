from datetime import datetime, timezone
import pytest

from logsnip.parser import LogEntry
from logsnip.trendline import (
    TrendOptions,
    compute_trend,
    format_trend,
)
from logsnip.trend_pipeline import TrendPipelineOptions, run_trend_pipeline, trend_summary


def _ts(h: int, m: int) -> datetime:
    return datetime(2024, 1, 1, h, m, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(10, 0), level="INFO", message="start", line_number=1),
        LogEntry(timestamp=_ts(10, 0), level="INFO", message="ping", line_number=2),
        LogEntry(timestamp=_ts(10, 1), level="WARN", message="slow", line_number=3),
        LogEntry(timestamp=_ts(10, 2), level="ERROR", message="fail", line_number=4),
        LogEntry(timestamp=_ts(10, 2), level="ERROR", message="crash", line_number=5),
    ]


def test_compute_trend_bucket_count(sample_entries):
    buckets = compute_trend(sample_entries)
    assert len(buckets) == 3


def test_compute_trend_counts(sample_entries):
    buckets = compute_trend(sample_entries)
    counts = [b.count for b in buckets]
    assert counts == [2, 1, 2]


def test_compute_trend_level_filter(sample_entries):
    opts = TrendOptions(level_filter="ERROR")
    buckets = compute_trend(sample_entries, opts)
    assert len(buckets) == 1
    assert buckets[0].count == 2


def test_compute_trend_pattern_filter(sample_entries):
    opts = TrendOptions(pattern="fail")
    buckets = compute_trend(sample_entries, opts)
    assert len(buckets) == 1
    assert buckets[0].count == 1


def test_compute_trend_window_minutes(sample_entries):
    opts = TrendOptions(window_minutes=2)
    buckets = compute_trend(sample_entries, opts)
    # minutes 0 and 1 collapse into same bucket (0), minute 2 stays
    assert len(buckets) == 2


def test_compute_trend_empty():
    buckets = compute_trend([])
    assert buckets == []


def test_format_trend_lines(sample_entries):
    buckets = compute_trend(sample_entries)
    output = format_trend(buckets)
    lines = output.strip().splitlines()
    assert len(lines) == 3


def test_format_trend_empty():
    assert format_trend([]) == "No trend data."


def test_run_trend_pipeline_returns_buckets(sample_entries):
    opts = TrendPipelineOptions()
    buckets = run_trend_pipeline(sample_entries, opts)
    assert len(buckets) == 3


def test_trend_summary_contains_peak(sample_entries):
    opts = TrendPipelineOptions()
    buckets = run_trend_pipeline(sample_entries, opts)
    summary = trend_summary(buckets)
    assert "peak" in summary
    assert "bucket" in summary


def test_trend_summary_empty():
    assert trend_summary([]) == "trend: no data"
