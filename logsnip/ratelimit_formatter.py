"""Formatters for rate-limit pipeline output."""
from __future__ import annotations

import json
from typing import List

from logsnip.parser import LogEntry
from logsnip.ratelimiter import RateLimitReport


def _ts_str(entry: LogEntry) -> str:
    return entry.timestamp.isoformat()


def format_ratelimit_text(entries: List[LogEntry], report: RateLimitReport) -> str:
    lines = []
    for e in entries:
        lines.append(f"[{_ts_str(e)}] {e.level}: {e.message}")
    lines.append("")
    lines.append(
        f"--- {report.total_out}/{report.total_in} entries kept "
        f"({report.dropped} dropped, {report.drop_pct}%) ---"
    )
    return "\n".join(lines)


def format_ratelimit_json(entries: List[LogEntry], report: RateLimitReport) -> str:
    payload = {
        "entries": [
            {"timestamp": _ts_str(e), "level": e.level, "message": e.message}
            for e in entries
        ],
        "report": {
            "total_in": report.total_in,
            "total_out": report.total_out,
            "dropped": report.dropped,
            "drop_pct": report.drop_pct,
        },
    }
    return json.dumps(payload, indent=2)


def format_ratelimit_jsonl(entries: List[LogEntry]) -> str:
    lines = [
        json.dumps({"timestamp": _ts_str(e), "level": e.level, "message": e.message})
        for e in entries
    ]
    return "\n".join(lines)


def format_ratelimit_entries(
    entries: List[LogEntry],
    report: RateLimitReport,
    fmt: str = "text",
) -> str:
    if fmt == "json":
        return format_ratelimit_json(entries, report)
    if fmt == "jsonl":
        return format_ratelimit_jsonl(entries)
    return format_ratelimit_text(entries, report)
