import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.score_pipeline import ScorePipelineOptions, run_score_pipeline, score_summary


def _ts(minute: int = 0):
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="ERROR", message="connection failed", line=1),
        LogEntry(timestamp=_ts(1), level="INFO", message="ready", line=2),
        LogEntry(timestamp=_ts(2), level="WARNING", message="slow response", line=3),
        LogEntry(timestamp=_ts(3), level="DEBUG", message="trace output", line=4),
        LogEntry(timestamp=_ts(4), level="ERROR", message="timeout error", line=5),
    ]


def test_run_pipeline_returns_all(sample_entries):
    opts = ScorePipelineOptions()
    result = run_score_pipeline(sample_entries, opts)
    assert len(result) == len(sample_entries)


def test_run_pipeline_top_n(sample_entries):
    opts = ScorePipelineOptions(top_n=2)
    result = run_score_pipeline(sample_entries, opts)
    assert len(result) == 2


def test_run_pipeline_min_score(sample_entries):
    opts = ScorePipelineOptions(min_score=4)
    result = run_score_pipeline(sample_entries, opts)
    assert all(s.score >= 4 for s in result)


def test_run_pipeline_filter_level(sample_entries):
    opts = ScorePipelineOptions(level="error")
    result = run_score_pipeline(sample_entries, opts)
    assert all(s.level.upper() == "ERROR" for s in result)


def test_run_pipeline_keyword_boost(sample_entries):
    opts = ScorePipelineOptions(keywords=["failed"], keyword_weight=5)
    result = run_score_pipeline(sample_entries, opts)
    failed = next(s for s in result if "failed" in s.message)
    assert failed.score > 4


def test_score_summary_keys(sample_entries):
    from logsnip.scorer import score_entries
    scored = score_entries(sample_entries)
    summary = score_summary(scored)
    assert "total" in summary
    assert "max_score" in summary
    assert "avg_score" in summary


def test_score_summary_empty():
    summary = score_summary([])
    assert summary["total"] == 0
    assert summary["avg_score"] == 0.0
