from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict
from logsnip.parser import LogEntry


@dataclass
class ProfileReport:
    total: int
    level_counts: Dict[str, int]
    first_ts: datetime | None
    last_ts: datetime | None
    duration_seconds: float
    top_sources: Dict[str, int]
    messages_per_minute: float


def _source(entry: LogEntry) -> str:
    parts = entry.message.split()
    return parts[0] if parts else "unknown"


def profile_entries(entries: List[LogEntry]) -> ProfileReport:
    if not entries:
        return ProfileReport(
            total=0,
            level_counts={},
            first_ts=None,
            last_ts=None,
            duration_seconds=0.0,
            top_sources={},
            messages_per_minute=0.0,
        )

    level_counts: Dict[str, int] = {}
    source_counts: Dict[str, int] = {}

    for e in entries:
        lvl = (e.level or "UNKNOWN").upper()
        level_counts[lvl] = level_counts.get(lvl, 0) + 1
        src = _source(e)
        source_counts[src] = source_counts.get(src, 0) + 1

    timestamps = [e.timestamp for e in entries if e.timestamp]
    first_ts = min(timestamps) if timestamps else None
    last_ts = max(timestamps) if timestamps else None

    duration = 0.0
    if first_ts and last_ts:
        duration = (last_ts - first_ts).total_seconds()

    mpm = 0.0
    if duration > 0:
        mpm = len(entries) / (duration / 60)

    top_sources = dict(sorted(source_counts.items(), key=lambda x: -x[1])[:5])

    return ProfileReport(
        total=len(entries),
        level_counts=level_counts,
        first_ts=first_ts,
        last_ts=last_ts,
        duration_seconds=duration,
        top_sources=top_sources,
        messages_per_minute=round(mpm, 2),
    )


def format_profile(report: ProfileReport) -> str:
    lines = [
        f"Total entries : {report.total}",
        f"Duration (s)  : {report.duration_seconds:.1f}",
        f"Msgs/min      : {report.messages_per_minute}",
        f"First         : {report.first_ts}",
        f"Last          : {report.last_ts}",
        "Levels:",
    ]
    for lvl, cnt in sorted(report.level_counts.items()):
        lines.append(f"  {lvl:<10} {cnt}")
    lines.append("Top sources:")
    for src, cnt in report.top_sources.items():
        lines.append(f"  {src:<20} {cnt}")
    return "\n".join(lines)
