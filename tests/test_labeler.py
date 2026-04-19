import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.labeler import LabelRule, LabeledEntry, label_entries, filter_by_label


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="ERROR", message="disk full", line_number=1),
        LogEntry(timestamp=_ts(1), level="WARN", message="retry attempt", line_number=2),
        LogEntry(timestamp=_ts(2), level="INFO", message="connection ok", line_number=3),
        LogEntry(timestamp=_ts(3), level="ERROR", message="timeout error", line_number=4),
    ]


@pytest.fixture
def rules():
    return [
        LabelRule(label="critical", level="ERROR"),
        LabelRule(label="retry", pattern="retry"),
    ]


def test_label_rule_invalid_empty_label():
    with pytest.raises(ValueError):
        LabelRule(label="", pattern="foo")


def test_label_rule_invalid_no_criteria():
    with pytest.raises(ValueError):
        LabelRule(label="x")


def test_label_entries_count(sample_entries, rules):
    result = label_entries(sample_entries, rules)
    assert len(result) == 4


def test_label_entries_error_labeled(sample_entries, rules):
    result = label_entries(sample_entries, rules)
    assert result[0].has_label("critical")
    assert result[3].has_label("critical")


def test_label_entries_no_label_for_info(sample_entries, rules):
    result = label_entries(sample_entries, rules)
    assert not result[2].has_label("critical")
    assert not result[2].has_label("retry")


def test_label_entries_pattern_match(sample_entries, rules):
    result = label_entries(sample_entries, rules)
    assert result[1].has_label("retry")


def test_filter_by_label(sample_entries, rules):
    labeled = label_entries(sample_entries, rules)
    critical = filter_by_label(labeled, "critical")
    assert len(critical) == 2


def test_labeled_entry_properties(sample_entries, rules):
    labeled = label_entries(sample_entries, rules)
    e = labeled[0]
    assert e.timestamp == _ts(0)
    assert e.level == "ERROR"
    assert "disk" in e.message
