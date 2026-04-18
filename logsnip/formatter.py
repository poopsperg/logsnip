"""Output formatters for log entries."""

import json
from typing import Iterable
from logsnip.parser import LogEntry


SUPPORTED_FORMATS = ("text", "json", "jsonl")


def format_text(entries: Iterable[LogEntry]) -> str:
    """Return entries as plain text, one per line."""
    lines = []
    for entry in entries:
        parts = [entry.timestamp.isoformat(), entry.level.upper(), entry.message]
        if entry.extra:
            parts.append(str(entry.extra))
        lines.append("  ".join(parts))
    return "\n".join(lines)


def format_json(entries: Iterable[LogEntry]) -> str:
    """Return entries as a JSON array."""
    records = _entries_to_dicts(entries)
    return json.dumps(records, indent=2, default=str)


def format_jsonl(entries: Iterable[LogEntry]) -> str:
    """Return entries as newline-delimited JSON (one object per line)."""
    lines = []
    for record in _entries_to_dicts(entries):
        lines.append(json.dumps(record, default=str))
    return "\n".join(lines)


def _entries_to_dicts(entries: Iterable[LogEntry]) -> list[dict]:
    result = []
    for entry in entries:
        d = {
            "timestamp": entry.timestamp.isoformat(),
            "level": entry.level,
            "message": entry.message,
            "line": entry.line_number,
        }
        if entry.extra:
            d["extra"] = entry.extra
        result.append(d)
    return result


def format_entries(entries: Iterable[LogEntry], fmt: str) -> str:
    """Dispatch to the correct formatter."""
    entries = list(entries)
    if fmt == "json":
        return format_json(entries)
    if fmt == "jsonl":
        return format_jsonl(entries)
    return format_text(entries)
