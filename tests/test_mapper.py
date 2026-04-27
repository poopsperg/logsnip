import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.mapper import (
    MapRule,
    map_entry,
    map_entries,
    map_summary,
)


def _ts(minute: int = 0) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(_ts(0), "INFO", "service started", "INFO service started", 1),
        LogEntry(_ts(1), "WARN", "disk usage high", "WARN disk usage high", 2),
        LogEntry(_ts(2), "ERROR", "connection failed", "ERROR connection failed", 3),
        LogEntry(_ts(3), "DEBUG", "retry attempt 1", "DEBUG retry attempt 1", 4),
    ]


def test_map_rule_invalid_field():
    with pytest.raises(ValueError, match="Invalid field"):
        MapRule(field="body", pattern="foo", replacement="bar")


def test_map_rule_empty_pattern():
    with pytest.raises(ValueError, match="pattern"):
        MapRule(field="message", pattern="", replacement="bar")


def test_map_rule_invalid_regex():
    with pytest.raises(re.error if False else Exception):
        MapRule(field="message", pattern="[invalid", replacement="x")


def test_map_entry_replaces_message(sample_entries):
    rule = MapRule(field="message", pattern=r"failed", replacement="timeout")
    result = map_entry(sample_entries[2], [rule])
    assert "timeout" in result.message
    assert "failed" not in result.message


def test_map_entry_replaces_level(sample_entries):
    rule = MapRule(field="level", pattern=r"WARN", replacement="WARNING")
    result = map_entry(sample_entries[1], [rule])
    assert result.level == "WARNING"


def test_map_entry_preserves_timestamp(sample_entries):
    rule = MapRule(field="message", pattern=r"started", replacement="booted")
    result = map_entry(sample_entries[0], [rule])
    assert result.timestamp == sample_entries[0].timestamp


def test_map_entries_applies_to_all(sample_entries):
    rule = MapRule(field="message", pattern=r"\d+", replacement="N")
    results = map_entries(sample_entries, [rule])
    assert results[3].message == "DEBUG retry attempt N"


def test_map_entries_level_filter(sample_entries):
    rule = MapRule(field="message", pattern=r".*", replacement="redacted")
    results = map_entries(sample_entries, [rule], level_filter="ERROR")
    assert results[2].message == "redacted"
    assert results[0].message == "service started"  # untouched


def test_map_entries_pattern_filter(sample_entries):
    rule = MapRule(field="message", pattern=r"high", replacement="elevated")
    results = map_entries(sample_entries, [rule], pattern_filter=r"disk")
    assert "elevated" in results[1].message
    assert results[0].message == "service started"


def test_map_summary_counts_changes(sample_entries):
    rule = MapRule(field="message", pattern=r"failed", replacement="timeout")
    mapped = map_entries(sample_entries, [rule])
    summary = map_summary(sample_entries, mapped)
    assert "1 modified" in summary
    assert "4 entries" in summary


import re
