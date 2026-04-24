from datetime import datetime, timezone
from typing import List

import pytest

from logsnip.parser import LogEntry
from logsnip.validator import (
    ValidateOptions,
    ValidationReport,
    validate_entries,
    validate_entry,
    format_validation_report,
)
from logsnip.validate_pipeline import ValidatePipelineOptions, run_validate_pipeline, validate_summary


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries() -> List[LogEntry]:
    return [
        LogEntry(timestamp=_ts(0), level="INFO", message="service started", line_number=1, raw=""),
        LogEntry(timestamp=_ts(1), level="WARN", message="high memory", line_number=2, raw=""),
        LogEntry(timestamp=_ts(2), level="ERROR", message="connection failed", line_number=3, raw=""),
        LogEntry(timestamp=_ts(3), level="DEBUG", message="retrying", line_number=4, raw=""),
    ]


def test_validate_entries_all_valid(sample_entries):
    report = validate_entries(sample_entries)
    assert report.valid
    assert report.issue_count == 0


def test_validate_entry_missing_level():
    entry = LogEntry(timestamp=_ts(0), level="", message="hello", line_number=5, raw="")
    opts = ValidateOptions(require_level=True)
    issues = validate_entry(entry, opts)
    assert len(issues) == 1
    assert "level" in issues[0].message.lower()


def test_validate_entry_empty_message():
    entry = LogEntry(timestamp=_ts(0), level="INFO", message="   ", line_number=6, raw="")
    opts = ValidateOptions(require_message=True)
    issues = validate_entry(entry, opts)
    assert any("message" in i.message.lower() for i in issues)


def test_validate_entry_disallowed_level():
    entry = LogEntry(timestamp=_ts(0), level="TRACE", message="ok", line_number=7, raw="")
    opts = ValidateOptions(allowed_levels=["INFO", "WARN", "ERROR"])
    issues = validate_entry(entry, opts)
    assert len(issues) == 1
    assert "TRACE" in issues[0].message


def test_validate_entry_message_too_long():
    entry = LogEntry(timestamp=_ts(0), level="INFO", message="x" * 300, line_number=8, raw="")
    opts = ValidateOptions(max_message_length=100)
    issues = validate_entry(entry, opts)
    assert len(issues) == 1
    assert "max length" in issues[0].message


def test_format_report_valid():
    report = ValidationReport(issues=[])
    text = format_validation_report(report)
    assert "passed" in text.lower()


def test_format_report_invalid(sample_entries):
    entry = LogEntry(timestamp=_ts(0), level="", message="", line_number=9, raw="")
    report = validate_entries([entry])
    text = format_validation_report(report)
    assert "failed" in text.lower()
    assert "line 9" in text


def test_run_validate_pipeline_filter_level(sample_entries):
    opts = ValidatePipelineOptions(level="ERROR", allowed_levels=["INFO", "WARN"])
    report = run_validate_pipeline(sample_entries, opts)
    # ERROR is not in allowed_levels, so 1 issue expected
    assert report.issue_count == 1


def test_validate_summary_pass():
    report = ValidationReport()
    assert validate_summary(report).startswith("[PASS]")


def test_validate_summary_fail():
    from logsnip.validator import ValidationIssue
    report = ValidationReport(issues=[ValidationIssue(line_number=1, message="bad")])
    assert validate_summary(report).startswith("[FAIL]")
