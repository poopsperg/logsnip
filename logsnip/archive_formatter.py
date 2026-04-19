from __future__ import annotations
import json
from typing import List

from logsnip.archiver import Archive


def format_archive_summary(archive: Archive) -> str:
    lines = [
        f"Label    : {archive.label}",
        f"Created  : {archive.created_at.isoformat()}",
        f"Entries  : {archive.count}",
        f"Start    : {archive.start}",
        f"End      : {archive.end}",
        f"Compressed: {archive.compressed}",
    ]
    return "\n".join(lines)


def format_archive_text(archive: Archive) -> str:
    parts = [format_archive_summary(archive), ""]
    for e in archive.entries:
        parts.append(f"[{e.timestamp.isoformat()}] {e.level:8s} {e.message}")
    return "\n".join(parts)


def format_archive_json(archive: Archive) -> str:
    data = {
        "label": archive.label,
        "created_at": archive.created_at.isoformat(),
        "count": archive.count,
        "start": archive.start.isoformat() if archive.start else None,
        "end": archive.end.isoformat() if archive.end else None,
        "entries": [
            {"timestamp": e.timestamp.isoformat(), "level": e.level, "message": e.message}
            for e in archive.entries
        ],
    }
    return json.dumps(data, indent=2)


def format_archive(archive: Archive, fmt: str = "text") -> str:
    if fmt == "json":
        return format_archive_json(archive)
    if fmt == "summary":
        return format_archive_summary(archive)
    return format_archive_text(archive)
