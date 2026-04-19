import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.alerter import (
    AlertRule,
    AlertOptions,
    evaluate_entry,
    run_alerts,
    alert_summary,
)


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="ERROR", message="disk full", line_number=1),
        LogEntry(timestamp=_ts(1), level="WARN", message="high memory", line_number=2),
        LogEntry(timestamp=_ts(2), level="INFO", message="startup complete", line_number=3),
        LogEntry(timestamp=_ts(3), level="ERROR", message="connection refused", line_number=4),
    ]


@pytest.fixture
def rules():
    return [
        AlertRule(name="disk", pattern="disk"),
        AlertRule(name="errors", level="ERROR"),
    ]


def test_alert_rule_invalid():
    with pytest.raises(ValueError):
        AlertRule(name="bad")


def test_alert_rule_matches_pattern(sample_entries):
    rule = AlertRule(name="disk", pattern="disk")
    assert rule.matches(sample_entries[0])
    assert not rule.matches(sample_entries[1])


def test_alert_rule_matches_level(sample_entries):
    rule = AlertRule(name="errors", level="ERROR")
    assert rule.matches(sample_entries[0])
    assert not rule.matches(sample_entries[1])


def test_evaluate_entry_multiple_rules(sample_entries, rules):
    alerts = evaluate_entry(sample_entries[0], rules)
    assert len(alerts) == 2


def test_run_alerts_total(sample_entries, rules):
    opts = AlertOptions(rules=rules)
    alerts = run_alerts(sample_entries, opts)
    assert len(alerts) == 3  # disk(1) + errors(2)


def test_run_alerts_limit(sample_entries, rules):
    opts = AlertOptions(rules=rules, limit=2)
    alerts = run_alerts(sample_entries, opts)
    assert len(alerts) == 2


def test_alert_summary(sample_entries, rules):
    opts = AlertOptions(rules=rules)
    alerts = run_alerts(sample_entries, opts)
    summary = alert_summary(alerts)
    assert summary["total"] == 3
    assert summary["by_rule"]["errors"] == 2
    assert summary["by_rule"]["disk"] == 1
