import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.alerter import AlertRule
from logsnip.alert_pipeline import AlertPipelineOptions, run_alert_pipeline, pipeline_summary


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="ERROR", message="disk full", line_number=1),
        LogEntry(timestamp=_ts(1), level="WARN", message="high memory", line_number=2),
        LogEntry(timestamp=_ts(2), level="INFO", message="startup ok", line_number=3),
        LogEntry(timestamp=_ts(3), level="ERROR", message="timeout error", line_number=4),
    ]


def test_run_pipeline_no_filter(sample_entries):
    rules = [AlertRule(name="all_errors", level="ERROR")]
    opts = AlertPipelineOptions(rules=rules)
    alerts = run_alert_pipeline(sample_entries, opts)
    assert len(alerts) == 2


def test_run_pipeline_with_level_filter(sample_entries):
    rules = [AlertRule(name="warn_pattern", pattern="memory")]
    opts = AlertPipelineOptions(rules=rules, level="WARN")
    alerts = run_alert_pipeline(sample_entries, opts)
    assert len(alerts) == 1
    assert alerts[0].rule_name == "warn_pattern"


def test_run_pipeline_with_pattern_filter(sample_entries):
    rules = [AlertRule(name="any_error", level="ERROR")]
    opts = AlertPipelineOptions(rules=rules, pattern="timeout")
    alerts = run_alert_pipeline(sample_entries, opts)
    assert len(alerts) == 1


def test_run_pipeline_no_match(sample_entries):
    rules = [AlertRule(name="critical", level="CRITICAL")]
    opts = AlertPipelineOptions(rules=rules)
    alerts = run_alert_pipeline(sample_entries, opts)
    assert alerts == []


def test_pipeline_summary(sample_entries):
    rules = [AlertRule(name="errors", level="ERROR")]
    opts = AlertPipelineOptions(rules=rules)
    alerts = run_alert_pipeline(sample_entries, opts)
    summary = pipeline_summary(alerts)
    assert summary["total"] == 2
    assert "errors" in summary["by_rule"]
