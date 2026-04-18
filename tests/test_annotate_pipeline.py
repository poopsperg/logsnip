"""Tests for logsnip.annotate_pipeline."""
from datetime import datetime, timezone

from logsnip.parser import LogEntry
from logsnip.annotator import AnnotationRule
from logsnip.annotate_pipeline import (
    AnnotatePipelineOptions,
    run_annotate_pipeline,
    annotate_summary,
)


def _ts(h: int) -> datetime:
    return datetime(2024, 1, 1, h, 0, 0, tzinfo=timezone.utc)


ENTRIES = [
    LogEntry(timestamp=_ts(1), level="ERROR", message="db connection failed", line_number=1),
    LogEntry(timestamp=_ts(2), level="INFO", message="service started", line_number=2),
    LogEntry(timestamp=_ts(3), level="WARN", message="high memory usage", line_number=3),
]

RULES = [
    AnnotationRule(tag="db", pattern=r"connection|db"),
    AnnotationRule(tag="infra", pattern=r"memory|cpu"),
]


def test_run_pipeline_no_filter():
    opts = AnnotatePipelineOptions(rules=RULES)
    result = run_annotate_pipeline(ENTRIES, opts)
    assert len(result) == 3


def test_run_pipeline_with_filter():
    opts = AnnotatePipelineOptions(rules=RULES, filter_tag="db")
    result = run_annotate_pipeline(ENTRIES, opts)
    assert len(result) == 1
    assert result[0].entry.message == "db connection failed"


def test_run_pipeline_filter_no_match():
    opts = AnnotatePipelineOptions(rules=RULES, filter_tag="auth")
    result = run_annotate_pipeline(ENTRIES, opts)
    assert result == []


def test_summary_total():
    opts = AnnotatePipelineOptions(rules=RULES)
    result = run_annotate_pipeline(ENTRIES, opts)
    summary = annotate_summary(result)
    assert summary["total"] == 3


def test_summary_by_tag():
    opts = AnnotatePipelineOptions(rules=RULES)
    result = run_annotate_pipeline(ENTRIES, opts)
    summary = annotate_summary(result)
    assert summary["by_tag"].get("db") == 1
    assert summary["by_tag"].get("infra") == 1


def test_summary_untagged():
    opts = AnnotatePipelineOptions(rules=RULES)
    result = run_annotate_pipeline(ENTRIES, opts)
    summary = annotate_summary(result)
    assert summary["untagged"] == 1
