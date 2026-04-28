from __future__ import annotations

from datetime import datetime, timezone
from typing import List

import pytest

from logsnip.enrich_pipeline import EnrichPipelineOptions, run_enrich_pipeline, pipeline_summary
from logsnip.enricher import EnrichRule
from logsnip.parser import LogEntry


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries() -> List[LogEntry]:
    return [
        LogEntry(timestamp=_ts(0), level="INFO", message="user=alice action=login", line_number=1),
        LogEntry(timestamp=_ts(1), level="ERROR", message="user=bob action=fail", line_number=2),
        LogEntry(timestamp=_ts(2), level="INFO", message="no metadata", line_number=3),
        LogEntry(timestamp=_ts(3), level="DEBUG", message="user=carol action=logout", line_number=4),
    ]


@pytest.fixture
def user_rule() -> EnrichRule:
    return EnrichRule(field="message", pattern=r"user=(\w+)", extract_as="user")


@pytest.fixture
def action_rule() -> EnrichRule:
    return EnrichRule(field="message", pattern=r"action=(\w+)", extract_as="action")


def test_run_pipeline_returns_all(sample_entries, user_rule):
    opts = EnrichPipelineOptions(rules=[user_rule])
    results = run_enrich_pipeline(sample_entries, opts)
    assert len(results) == 4


def test_run_pipeline_filter_level(sample_entries, user_rule):
    opts = EnrichPipelineOptions(rules=[user_rule], level_filter="INFO")
    results = run_enrich_pipeline(sample_entries, opts)
    assert all(e.level == "INFO" for e in results)


def test_run_pipeline_filter_pattern(sample_entries, user_rule):
    opts = EnrichPipelineOptions(rules=[user_rule], pattern_filter="user=")
    results = run_enrich_pipeline(sample_entries, opts)
    assert len(results) == 3


def test_run_pipeline_multiple_rules(sample_entries, user_rule, action_rule):
    opts = EnrichPipelineOptions(rules=[user_rule, action_rule])
    results = run_enrich_pipeline(sample_entries, opts)
    matched = [e for e in results if "user" in e.extras and "action" in e.extras]
    assert len(matched) == 3


def test_run_pipeline_summary_string(sample_entries, user_rule):
    opts = EnrichPipelineOptions(rules=[user_rule])
    results = run_enrich_pipeline(sample_entries, opts)
    summary = pipeline_summary(results)
    assert isinstance(summary, str)
    assert "Enriched" in summary
