"""Format watched log entries for display."""
from __future__ import annotations

import json
from datetime import datetime

from logsnip.parser import LogEntry


def _ts_str(ts: datetime | None) -> str:
    if ts is None:
        return ""
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def format_watch_text(entries: list[LogEntry], *, show_line: bool = False) -> str:
    lines = []
    for e in entries:
        prefix = f"[{e.line_number}] " if show_line else ""
        lines.append(f"{prefix}{_ts_str(e.timestamp)} {e.level:<8} {e.message}")
    return "\n".join(lines)


def format_watch_json(entries: list[LogEntry]) -> str:
    data = [
        {
            "line_number": e.line_number,
            "timestamp": _ts_str(e.timestamp),
            "level": e.level,
            "message": e.message,
        }
        for e in entries
    ]
    return json.dumps(data, indent=2)


def format_watch_jsonl(entries: list[LogEntry]) -> str:
    rows = []
    for e in entries:
        rows.append(json.dumps({
            "line_number": e.line_number,
            "timestamp": _ts_str(e.timestamp),
            "level": e.level,
            "message": e.message,
        }))
    return "\n".join(rows)


SUPPORTED_FORMATS = ("text", "json", "jsonl")


def format_watch_entries(
    entries: list[LogEntry],
    fmt: str = "text",
    *,
    show_line: bool = False,
) -> str:
    if fmt == "json":
        return format_watch_json(entries)
    if fmt == "jsonl":
        return format_watch_jsonl(entries)
    return format_watch_text(entries, show_line=show_line)
