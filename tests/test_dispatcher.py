"""Tests for logsnip.dispatcher."""
import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.dispatcher import (
    DispatchRule,
    DispatchOptions,
    dispatch_entries,
    dispatch_summary,
)


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="ERROR", message="disk full", line_number=1),
        LogEntry(timestamp=_ts(1), level="WARN", message="low memory", line_number=2),
        LogEntry(timestamp=_ts(2), level="INFO", message="started", line_number=3),
        LogEntry(timestamp=_ts(3), level="ERROR", message="timeout occurred", line_number=4),
        LogEntry(timestamp=_ts(4), level="DEBUG", message="debug trace", line_number=5),
    ]


def test_dispatch_rule_invalid_empty_name():
    with pytest.raises(ValueError, match="name"):
        DispatchRule(name="", handler=lambda e: None, level="ERROR")


def test_dispatch_rule_invalid_no_criteria():
    with pytest.raises(ValueError, match="at least one"):
        DispatchRule(name="x", handler=lambda e: None)


def test_dispatch_rule_matches_level(sample_entries):
    rule = DispatchRule(name="errors", handler=lambda e: None, level="ERROR")
    matches = [e for e in sample_entries if rule.matches(e)]
    assert len(matches) == 2


def test_dispatch_rule_matches_pattern(sample_entries):
    rule = DispatchRule(name="mem", handler=lambda e: None, pattern="memory")
    matches = [e for e in sample_entries if rule.matches(e)]
    assert len(matches) == 1
    assert matches[0].message == "low memory"


def test_dispatch_rule_matches_level_and_pattern(sample_entries):
    rule = DispatchRule(name="err_timeout", handler=lambda e: None, level="ERROR", pattern="timeout")
    matches = [e for e in sample_entries if rule.matches(e)]
    assert len(matches) == 1
    assert "timeout" in matches[0].message


def test_dispatch_entries_total(sample_entries):
    collected = []
    rule = DispatchRule(name="errors", handler=collected.append, level="ERROR")
    opts = DispatchOptions(rules=[rule])
    result = dispatch_entries(sample_entries, opts)
    assert result.total == 5


def test_dispatch_entries_counts(sample_entries):
    collected = []
    rule = DispatchRule(name="errors", handler=collected.append, level="ERROR")
    opts = DispatchOptions(rules=[rule])
    result = dispatch_entries(sample_entries, opts)
    assert result.counts["errors"] == 2
    assert result.dispatched == 2


def test_dispatch_entries_unmatched(sample_entries):
    rule = DispatchRule(name="errors", handler=lambda e: None, level="ERROR")
    opts = DispatchOptions(rules=[rule])
    result = dispatch_entries(sample_entries, opts)
    assert result.unmatched == 3


def test_dispatch_entries_catch_all(sample_entries):
    caught = []
    rule = DispatchRule(name="errors", handler=lambda e: None, level="ERROR")
    opts = DispatchOptions(rules=[rule], catch_all=caught.append)
    dispatch_entries(sample_entries, opts)
    assert len(caught) == 3


def test_dispatch_summary_contains_keys(sample_entries):
    rule = DispatchRule(name="errors", handler=lambda e: None, level="ERROR")
    opts = DispatchOptions(rules=[rule])
    result = dispatch_entries(sample_entries, opts)
    summary = dispatch_summary(result)
    assert "Total" in summary
    assert "Dispatched" in summary
    assert "Unmatched" in summary
    assert "errors" in summary
