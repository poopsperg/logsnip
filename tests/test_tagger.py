import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.tagger import TagRule, tag_entries, filter_by_tag, tag_summary


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="ERROR", message="disk full", line_number=1),
        LogEntry(timestamp=_ts(1), level="WARN", message="memory low", line_number=2),
        LogEntry(timestamp=_ts(2), level="INFO", message="startup complete", line_number=3),
        LogEntry(timestamp=_ts(3), level="ERROR", message="connection refused", line_number=4),
    ]


@pytest.fixture
def rules():
    return [
        TagRule(tag="critical", level="ERROR"),
        TagRule(tag="disk", pattern="disk"),
        TagRule(tag="network", pattern="connection"),
    ]


def test_tag_rule_invalid():
    with pytest.raises(ValueError):
        TagRule(tag="")


def test_tag_entries_count(sample_entries, rules):
    tagged = tag_entries(sample_entries, rules)
    assert len(tagged) == len(sample_entries)


def test_tag_entries_critical(sample_entries, rules):
    tagged = tag_entries(sample_entries, rules)
    critical = [t for t in tagged if t.has_tag("critical")]
    assert len(critical) == 2


def test_tag_entries_disk(sample_entries, rules):
    tagged = tag_entries(sample_entries, rules)
    disk = [t for t in tagged if t.has_tag("disk")]
    assert len(disk) == 1
    assert disk[0].entry.message == "disk full"


def test_tag_entries_multiple_tags(sample_entries, rules):
    tagged = tag_entries(sample_entries, rules)
    first = tagged[0]
    assert first.has_tag("critical")
    assert first.has_tag("disk")


def test_filter_by_tag(sample_entries, rules):
    tagged = tag_entries(sample_entries, rules)
    network = filter_by_tag(tagged, "network")
    assert len(network) == 1
    assert network[0].entry.message == "connection refused"


def test_filter_by_tag_no_match(sample_entries, rules):
    tagged = tag_entries(sample_entries, rules)
    result = filter_by_tag(tagged, "nonexistent")
    assert result == []


def test_tag_summary(sample_entries, rules):
    tagged = tag_entries(sample_entries, rules)
    summary = tag_summary(tagged)
    assert summary["critical"] == 2
    assert summary["disk"] == 1
    assert summary["network"] == 1
