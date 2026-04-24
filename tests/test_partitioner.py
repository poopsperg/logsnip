"""Tests for logsnip.partitioner."""
from datetime import datetime, timezone
from typing import List

import pytest

from logsnip.parser import LogEntry
from logsnip.partitioner import (
    Partition,
    PartitionOptions,
    PartitionRule,
    partition_entries,
    partition_summary,
)


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture()
def sample_entries() -> List[LogEntry]:
    return [
        LogEntry(timestamp=_ts(0), level="ERROR", message="disk full", line=1),
        LogEntry(timestamp=_ts(1), level="WARN", message="high memory", line=2),
        LogEntry(timestamp=_ts(2), level="INFO", message="request ok", line=3),
        LogEntry(timestamp=_ts(3), level="ERROR", message="timeout error", line=4),
        LogEntry(timestamp=_ts(4), level="DEBUG", message="trace data", line=5),
    ]


@pytest.fixture()
def rules() -> List[PartitionRule]:
    return [
        PartitionRule(name="errors", level="ERROR"),
        PartitionRule(name="warnings", level="WARN"),
    ]


def test_partition_rule_invalid_empty_name():
    with pytest.raises(ValueError, match="name"):
        PartitionRule(name="", level="ERROR")


def test_partition_rule_invalid_no_criteria():
    with pytest.raises(ValueError, match="at least one"):
        PartitionRule(name="bucket")


def test_partition_entries_bucket_count(sample_entries, rules):
    opts = PartitionOptions(rules=rules)
    result = partition_entries(sample_entries, opts)
    assert "errors" in result
    assert "warnings" in result
    assert "unmatched" in result


def test_partition_entries_errors_count(sample_entries, rules):
    opts = PartitionOptions(rules=rules)
    result = partition_entries(sample_entries, opts)
    assert result["errors"].count == 2


def test_partition_entries_warnings_count(sample_entries, rules):
    opts = PartitionOptions(rules=rules)
    result = partition_entries(sample_entries, opts)
    assert result["warnings"].count == 1


def test_partition_entries_unmatched(sample_entries, rules):
    opts = PartitionOptions(rules=rules)
    result = partition_entries(sample_entries, opts)
    assert result["unmatched"].count == 2


def test_partition_entries_custom_default(sample_entries, rules):
    opts = PartitionOptions(rules=rules, default_bucket="other")
    result = partition_entries(sample_entries, opts)
    assert "other" in result
    assert result["other"].count == 2


def test_partition_entries_pattern_rule(sample_entries):
    rules = [PartitionRule(name="timeouts", pattern="timeout")]
    opts = PartitionOptions(rules=rules)
    result = partition_entries(sample_entries, opts)
    assert result["timeouts"].count == 1


def test_partition_summary_contains_names(sample_entries, rules):
    opts = PartitionOptions(rules=rules)
    result = partition_entries(sample_entries, opts)
    summary = partition_summary(result)
    assert "errors" in summary
    assert "warnings" in summary
    assert "unmatched" in summary


def test_partition_start_end(sample_entries, rules):
    opts = PartitionOptions(rules=rules)
    result = partition_entries(sample_entries, opts)
    part = result["errors"]
    assert part.start == _ts(0)
    assert part.end == _ts(3)
