"""Tests for logsnip.exporter."""
import json
from datetime import datetime, timezone

import pytest

from logsnip.exporter import (
    ExportOptions,
    SUPPORTED_EXPORT_FORMATS,
    export_csv,
    export_entries,
    export_json,
    export_jsonl,
    export_tsv,
)
from logsnip.parser import LogEntry


def _ts(h: int, m: int = 0) -> datetime:
    return datetime(2024, 1, 1, h, m, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(10), level="INFO", message="started", line_number=1),
        LogEntry(timestamp=_ts(11), level="WARN", message="slow query", line_number=5),
        LogEntry(timestamp=_ts(12), level="ERROR", message="failed", line_number=9),
    ]


def test_supported_formats():
    assert set(SUPPORTED_EXPORT_FORMATS) == {"csv", "json", "jsonl", "tsv"}


def test_export_csv_headers(sample_entries):
    out = export_csv(sample_entries)
    first_line = out.splitlines()[0]
    assert "timestamp" in first_line
    assert "level" in first_line
    assert "message" in first_line
    assert "line" in first_line


def test_export_csv_row_count(sample_entries):
    out = export_csv(sample_entries)
    lines = [l for l in out.splitlines() if l.strip()]
    assert len(lines) == len(sample_entries) + 1  # header + rows


def test_export_csv_no_line_number(sample_entries):
    out = export_csv(sample_entries, include_line=False)
    assert "line" not in out.splitlines()[0]


def test_export_json_is_list(sample_entries):
    out = export_json(sample_entries)
    data = json.loads(out)
    assert isinstance(data, list)
    assert len(data) == 3


def test_export_json_fields(sample_entries):
    data = json.loads(export_json(sample_entries))
    assert data[0]["level"] == "INFO"
    assert data[1]["message"] == "slow query"


def test_export_jsonl_line_count(sample_entries):
    out = export_jsonl(sample_entries)
    lines = out.strip().splitlines()
    assert len(lines) == 3
    assert json.loads(lines[0])["level"] == "INFO"


def test_export_tsv_delimiter(sample_entries):
    out = export_tsv(sample_entries)
    assert "\t" in out.splitlines()[0]


def test_export_entries_dispatch(sample_entries):
    for fmt in SUPPORTED_EXPORT_FORMATS:
        opts = ExportOptions(fmt=fmt)
        result = export_entries(sample_entries, opts)
        assert isinstance(result, str)
        assert len(result) > 0


def test_export_entries_invalid_format(sample_entries):
    opts = ExportOptions(fmt="xml")  # type: ignore
    with pytest.raises(ValueError, match="Unsupported"):
        export_entries(sample_entries, opts)


def test_export_empty_entries():
    """All export functions should handle an empty list without errors."""
    empty = []
    assert export_json(empty) == "[]"
    assert export_jsonl(empty) == ""

    csv_out = export_csv(empty)
    lines = [l for l in csv_out.splitlines() if l.strip()]
    assert len(lines) == 1  # header only

    tsv_out = export_tsv(empty)
    lines = [l for l in tsv_out.splitlines() if l.strip()]
    assert len(lines) == 1  # header only
