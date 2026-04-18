"""Tests for logsnip.formatter."""

import json
from datetime import datetime, timezone
import pytest
from logsnip.parser import LogEntry
from logsnip.formatter import format_entries, SUPPORTED_FORMATS


def _ts(hour: int, minute: int = 0):
    return datetime(2024, 1, 15, hour, minute, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(10), level="info", message="server started", line_number=1),
        LogEntry(timestamp=_ts(10, 5), level="warn", message="high memory", line_number=4, extra={"pct": 92}),
        LogEntry(timestamp=_ts(10, 10), level="error", message="connection lost", line_number=7),
    ]


def test_supported_formats_constant():
    assert "text" in SUPPORTED_FORMATS
    assert "json" in SUPPORTED_FORMATS
    assert "jsonl" in SUPPORTED_FORMATS


def test_format_text_contains_messages(sample_entries):
    out = format_entries(sample_entries, "text")
    assert "server started" in out
    assert "high memory" in out
    assert "connection lost" in out


def test_format_text_contains_levels(sample_entries):
    out = format_entries(sample_entries, "text")
    assert "INFO" in out
    assert "WARN" in out
    assert "ERROR" in out


def test_format_json_valid(sample_entries):
    out = format_entries(sample_entries, "json")
    records = json.loads(out)
    assert isinstance(records, list)
    assert len(records) == 3
    assert records[1]["extra"] == {"pct": 92}


def test_format_json_has_line_numbers(sample_entries):
    out = format_entries(sample_entries, "json")
    records = json.loads(out)
    assert records[0]["line"] == 1
    assert records[2]["line"] == 7


def test_format_jsonl_line_count(sample_entries):
    out = format_entries(sample_entries, "jsonl")
    lines = [l for l in out.splitlines() if l.strip()]
    assert len(lines) == 3
    for line in lines:
        obj = json.loads(line)
        assert "timestamp" in obj
        assert "message" in obj


def test_format_text_no_extra_key_when_absent(sample_entries):
    # entry without extra should not show 'None' in text output
    out = format_entries([sample_entries[0]], "text")
    assert "None" not in out
