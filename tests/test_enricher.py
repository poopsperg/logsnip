from __future__ import annotations

from datetime import datetime, timezone
from typing import List

import pytest

from logsnip.enricher import (
    EnrichOptions,
    EnrichRule,
    EnrichedEntry,
    enrich_entries,
    enrich_entry,
    enrich_summary,
)
from logsnip.parser import LogEntry


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries() -> List[LogEntry]:
    return [
        LogEntry(timestamp=_ts(0), level="INFO", message="user=alice logged in", line_number=1),
        LogEntry(timestamp=_ts(1), level="ERROR", message="user=bob failed auth", line_number=2),
        LogEntry(timestamp=_ts(2), level="WARN", message="no user info here", line_number=3),
        LogEntry(timestamp=_ts(3), level="INFO", message="user=carol logged out", line_number=4),
    ]


@pytest.fixture
def user_rule() -> EnrichRule:
    return EnrichRule(field="message", pattern=r"user=(\w+)", extract_as="user")


def test_enrich_rule_invalid_empty_pattern():
    with pytest.raises(ValueError):
        EnrichRule(field="message", pattern="", extract_as="user")


def test_enrich_rule_invalid_empty_extract_as():
    with pytest.raises(ValueError):
        EnrichRule(field="message", pattern=r"user=(\w+)", extract_as="")


def test_enrich_rule_apply_match(sample_entries, user_rule):
    result = user_rule.apply(sample_entries[0])
    assert result == "alice"


def test_enrich_rule_apply_no_match(sample_entries, user_rule):
    result = user_rule.apply(sample_entries[2])
    assert result is None


def test_enrich_entry_extras_populated(sample_entries, user_rule):
    enriched = enrich_entry(sample_entries[0], [user_rule])
    assert enriched.extras.get("user") == "alice"


def test_enrich_entry_no_match_skip_empty(sample_entries, user_rule):
    enriched = enrich_entry(sample_entries[2], [user_rule], skip_empty=True)
    assert "user" not in enriched.extras


def test_enrich_entry_no_match_keep_none(sample_entries, user_rule):
    enriched = enrich_entry(sample_entries[2], [user_rule], skip_empty=False)
    assert "user" in enriched.extras
    assert enriched.extras["user"] is None


def test_enrich_entries_count(sample_entries, user_rule):
    opts = EnrichOptions(rules=[user_rule])
    results = enrich_entries(sample_entries, opts)
    assert len(results) == 4


def test_enrich_entries_correct_users(sample_entries, user_rule):
    opts = EnrichOptions(rules=[user_rule])
    results = enrich_entries(sample_entries, opts)
    users = [e.extras.get("user") for e in results if "user" in e.extras]
    assert set(users) == {"alice", "bob", "carol"}


def test_enrich_summary_contains_total(sample_entries, user_rule):
    opts = EnrichOptions(rules=[user_rule])
    results = enrich_entries(sample_entries, opts)
    summary = enrich_summary(results)
    assert "4" in summary


def test_enrich_summary_contains_field(sample_entries, user_rule):
    opts = EnrichOptions(rules=[user_rule])
    results = enrich_entries(sample_entries, opts)
    summary = enrich_summary(results)
    assert "user" in summary
