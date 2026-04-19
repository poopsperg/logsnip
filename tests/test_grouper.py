import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.grouper import (
    EntryGroup,
    GroupOptions,
    group_entries,
    group_summary,
)


def _ts(minute: int, second: int = 0) -> datetime:
    return datetime(2024, 1, 1, 10, minute, second, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="INFO", message="a", line_number=1),
        LogEntry(timestamp=_ts(1), level="WARN", message="b", line_number=2),
        LogEntry(timestamp=_ts(1), level="INFO", message="c", line_number=3),
        LogEntry(timestamp=_ts(2), level="ERROR", message="d", line_number=4),
        LogEntry(timestamp=_ts(2), level="ERROR", message="e", line_number=5),
    ]


def test_group_by_level_keys(sample_entries):
    groups = group_entries(sample_entries)
    assert set(groups.keys()) == {"INFO", "WARN", "ERROR"}


def test_group_by_level_counts(sample_entries):
    groups = group_entries(sample_entries)
    assert groups["INFO"].count == 2
    assert groups["ERROR"].count == 2
    assert groups["WARN"].count == 1


def test_group_by_minute(sample_entries):
    opts = GroupOptions(key="minute")
    groups = group_entries(sample_entries, opts)
    assert len(groups) == 3


def test_min_size_filters_small_groups(sample_entries):
    opts = GroupOptions(key="level", min_size=2)
    groups = group_entries(sample_entries, opts)
    assert "WARN" not in groups
    assert "INFO" in groups
    assert "ERROR" in groups


def test_entry_group_start_end(sample_entries):
    groups = group_entries(sample_entries)
    info = groups["INFO"]
    assert info.start == _ts(0)
    assert info.end == _ts(1)


def test_empty_entries():
    groups = group_entries([])
    assert groups == {}


def test_group_summary_contains_labels(sample_entries):
    groups = group_entries(sample_entries)
    summary = group_summary(groups)
    assert "INFO" in summary
    assert "ERROR" in summary
    assert "Groups:" in summary
