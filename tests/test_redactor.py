import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.redactor import RedactRule, RedactOptions, redact_message, redact_entry, redact_entries
from logsnip.redact_pipeline import RedactPipelineOptions, run_redact_pipeline, redact_summary


def _ts(minute: int = 0) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(_ts(0), "INFO", "user login from 192.168.1.1", "", 1),
        LogEntry(_ts(1), "WARN", "email sent to user@example.com", "", 2),
        LogEntry(_ts(2), "ERROR", "token=abc123 failed", "", 3),
        LogEntry(_ts(3), "DEBUG", "clean message", "", 4),
    ]


def test_redact_rule_basic():
    rule = RedactRule(r"\d+", "[NUM]")
    assert rule.apply("port 8080 open") == "port [NUM] open"


def test_redact_message_multiple_rules():
    rules = [RedactRule(r"foo", "[F]"), RedactRule(r"bar", "[B]")]
    assert redact_message("foo and bar", rules) == "[F] and [B]"


def test_redact_ip(sample_entries):
    opts = RedactOptions(redact_ip=True)
    result = redact_entry(sample_entries[0], opts)
    assert "[IP]" in result.message
    assert "192.168.1.1" not in result.message


def test_redact_email(sample_entries):
    opts = RedactOptions(redact_email=True)
    result = redact_entry(sample_entries[1], opts)
    assert "[EMAIL]" in result.message
    assert "user@example.com" not in result.message


def test_redact_preserves_other_fields(sample_entries):
    opts = RedactOptions(redact_ip=True)
    result = redact_entry(sample_entries[0], opts)
    assert result.level == "INFO"
    assert result.timestamp == _ts(0)


def test_redact_entries_count(sample_entries):
    opts = RedactOptions(redact_ip=True, redact_email=True)
    result = redact_entries(sample_entries, opts)
    assert len(result) == len(sample_entries)


def test_pipeline_custom_pattern(sample_entries):
    opts = RedactPipelineOptions(patterns=[r"token=\S+"])
    result = run_redact_pipeline(sample_entries, opts)
    assert "[REDACTED]" in result[2].message
    assert "token=abc123" not in result[2].message


def test_pipeline_no_change(sample_entries):
    opts = RedactPipelineOptions()
    result = run_redact_pipeline(sample_entries, opts)
    assert result[3].message == "clean message"


def test_redact_summary(sample_entries):
    opts = RedactPipelineOptions(redact_ip=True, redact_email=True)
    redacted = run_redact_pipeline(sample_entries, opts)
    summary = redact_summary(sample_entries, redacted)
    assert summary["total"] == 4
    assert summary["changed"] == 2
