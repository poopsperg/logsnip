"""Export log entries to various file formats."""
from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from typing import List, Literal

from logsnip.parser import LogEntry

ExportFormat = Literal["csv", "json", "jsonl", "tsv"]

SUPPORTED_EXPORT_FORMATS: list[str] = ["csv", "json", "jsonl", "tsv"]


@dataclass
class ExportOptions:
    fmt: ExportFormat = "csv"
    include_line_number: bool = True


def _entry_row(entry: LogEntry, include_line: bool) -> dict:
    row = {
        "timestamp": entry.timestamp.isoformat() if entry.timestamp else "",
        "level": entry.level or "",
        "message": entry.message,
    }
    if include_line:
        row["line"] = str(entry.line_number)
    return row


def export_csv(entries: List[LogEntry], include_line: bool = True, delimiter: str = ",") -> str:
    buf = io.StringIO()
    fieldnames = ["timestamp", "level", "message"]
    if include_line:
        fieldnames.append("line")
    writer = csv.DictWriter(buf, fieldnames=fieldnames, delimiter=delimiter)
    writer.writeheader()
    for entry in entries:
        writer.writerow(_entry_row(entry, include_line))
    return buf.getvalue()


def export_json(entries: List[LogEntry], include_line: bool = True) -> str:
    rows = [_entry_row(e, include_line) for e in entries]
    return json.dumps(rows, indent=2)


def export_jsonl(entries: List[LogEntry], include_line: bool = True) -> str:
    lines = [json.dumps(_entry_row(e, include_line)) for e in entries]
    return "\n".join(lines)


def export_tsv(entries: List[LogEntry], include_line: bool = True) -> str:
    return export_csv(entries, include_line=include_line, delimiter="\t")


def export_entries(entries: List[LogEntry], options: ExportOptions | None = None) -> str:
    opts = options or ExportOptions()
    if opts.fmt == "csv":
        return export_csv(entries, opts.include_line_number)
    if opts.fmt == "json":
        return export_json(entries, opts.include_line_number)
    if opts.fmt == "jsonl":
        return export_jsonl(entries, opts.include_line_number)
    if opts.fmt == "tsv":
        return export_tsv(entries, opts.include_line_number)
    raise ValueError(f"Unsupported export format: {opts.fmt}")
