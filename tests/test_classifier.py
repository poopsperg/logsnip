from datetime import datetime, timezone
import pytest
from logsnip.parser import LogEntry
from logsnip.classifier import (
    ClassifyRule,
    ClassifyOptions,
    classify_entries,
    group_by_label,
)
from logsnip.classify_pipeline import (
    ClassifyPipelineOptions,
    run_classify_pipeline,
    classify_summary,
)


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="ERROR", message="disk full", line_number=1),
        LogEntry(timestamp=_ts(1), level="WARN", message="memory low", line_number=2),
        LogEntry(timestamp=_ts(2), level="INFO", message="disk check ok", line_number=3),
        LogEntry(timestamp=_ts(3), level="ERROR", message="connection refused", line_number=4),
        LogEntry(timestamp=_ts(4), level="DEBUG", message="heartbeat ok", line_number=5),
    ]


@pytest.fixture
def rules():
    return [
        ClassifyRule(label="disk", pattern="disk"),
        ClassifyRule(label="errors", level="ERROR"),
        ClassifyRule(label="warnings", level="WARN"),
    ]


def test_classify_rule_invalid_empty_label():
    with pytest.raises(ValueError):
        ClassifyRule(label="", pattern="foo")


def test_classify_rule_invalid_no_criteria():
    with pytest.raises(ValueError):
        ClassifyRule(label="x")


def test_classify_entries_count(sample_entries, rules):
    opts = ClassifyOptions(rules=rules)
    result = classify_entries(sample_entries, opts)
    assert len(result) == len(sample_entries)


def test_classify_entries_labels(sample_entries, rules):
    opts = ClassifyOptions(rules=rules)
    result = classify_entries(sample_entries, opts)
    disk_entry = result[0]  # "disk full" ERROR
    assert "disk" in disk_entry.labels
    assert "errors" in disk_entry.labels


def test_classify_entries_default_label(sample_entries, rules):
    opts = ClassifyOptions(rules=rules, default_label="other")
    result = classify_entries(sample_entries, opts)
    debug_entry = result[4]  # heartbeat ok DEBUG
    assert debug_entry.labels == ["other"]


def test_classify_entries_no_match_no_default(sample_entries, rules):
    opts = ClassifyOptions(rules=rules)
    result = classify_entries(sample_entries, opts)
    debug_entry = result[4]
    assert debug_entry.labels == []


def test_group_by_label(sample_entries, rules):
    opts = ClassifyOptions(rules=rules)
    classified = classify_entries(sample_entries, opts)
    groups = group_by_label(classified)
    assert "disk" in groups
    assert "errors" in groups
    assert len(groups["errors"]) == 2


def test_run_pipeline_filter_level(sample_entries, rules):
    opts = ClassifyPipelineOptions(rules=rules, level="ERROR")
    result = run_classify_pipeline(sample_entries, opts)
    assert all(ce.level == "ERROR" for ce in result)


def test_classify_summary(sample_entries, rules):
    opts = ClassifyPipelineOptions(rules=rules)
    classified = run_classify_pipeline(sample_entries, opts)
    summary = classify_summary(classified)
    assert "errors" in summary
    assert summary["errors"] == 2
