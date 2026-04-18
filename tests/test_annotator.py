"""Tests for logsnip.annotator."""
from datetime import datetime, timezone
import pytest

from logsnip.parser import LogEntry
from logsnip.annotator import (
    AnnotationRule,
    AnnotatedEntry,
    annotate_entries,
    filter_by_tag,
    format_annotated,
)


def _ts(h: int) -> datetime:
    return datetime(2024, 1, 1, h, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(1), level="ERROR", message="connection refused", line_number=1),
        LogEntry(timestamp=_ts(2), level="WARN", message="timeout occurred", line_number=2),
        LogEntry(timestamp=_ts(3), level="INFO", message="user logged in", line_number=3),
        LogEntry(timestamp=_ts(4), level="ERROR", message="disk full error", line_number=4),
    ]


@pytest.fixture
def rules():
    return [
        AnnotationRule(tag="network", pattern=r"connection|timeout", note="check network"),
        AnnotationRule(tag="storage", pattern=r"disk"),
        AnnotationRule(tag="auth", pattern=r"login|logout"),
    ]


def test_annotate_entries_count(sample_entries, rules):
    result = annotate_entries(sample_entries, rules)
    assert len(result) == 4


def test_annotate_entries_tags(sample_entries, rules):
    result = annotate_entries(sample_entries, rules)
    assert result[0].has_tag("network")
    assert result[1].has_tag("network")
    assert result[3].has_tag("storage")
    assert result[2].has_tag("auth")


def test_annotate_entries_notes(sample_entries, rules):
    result = annotate_entries(sample_entries, rules)
    assert "check network" in result[0].notes


def test_annotate_no_match(sample_entries, rules):
    result = annotate_entries(sample_entries, rules)
    # disk full entry should not have network tag
    assert not result[3].has_tag("network")


def test_filter_by_tag(sample_entries, rules):
    annotated = annotate_entries(sample_entries, rules)
    network = filter_by_tag(annotated, "network")
    assert len(network) == 2


def test_filter_by_tag_empty(sample_entries, rules):
    annotated = annotate_entries(sample_entries, rules)
    result = filter_by_tag(annotated, "nonexistent")
    assert result == []


def test_format_annotated_contains_tag(sample_entries, rules):
    annotated = annotate_entries(sample_entries, rules)
    out = format_annotated(annotated)
    assert "network" in out
    assert "storage" in out


def test_format_annotated_contains_note(sample_entries, rules):
    annotated = annotate_entries(sample_entries, rules)
    out = format_annotated(annotated)
    assert "check network" in out


def test_annotation_rule_case_insensitive():
    rule = AnnotationRule(tag="test", pattern="ERROR")
    entry = LogEntry(timestamp=_ts(1), level="INFO", message="some error here", line_number=1)
    assert rule.matches(entry)
