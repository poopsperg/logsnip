"""Compute summary statistics over a collection of log entries."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import List

from logsnip.parser import LogEntry


@dataclass
class LogStats:
    total: int
    by_level: dict[str, int]
    first_timestamp: str | None
    last_timestamp: str | None
    unique_sources: int

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "by_level": dict(self.by_level),
            "first_timestamp": self.first_timestamp,
            "last_timestamp": self.last_timestamp,
            "unique_sources": self.unique_sources,
        }


def compute_stats(entries: List[LogEntry]) -> LogStats:
    """Return a LogStats summary for the given entries."""
    if not entries:
        return LogStats(
            total=0,
            by_level={},
            first_timestamp=None,
            last_timestamp=None,
            unique_sources=0,
        )

    level_counter: Counter = Counter()
    sources: set[str] = set()

    for entry in entries:
        level = (entry.level or "UNKNOWN").upper()
        level_counter[level] += 1
        if entry.source:
            sources.add(entry.source)

    timestamps = [
        e.timestamp.isoformat() for e in entries if e.timestamp is not None
    ]

    return LogStats(
        total=len(entries),
        by_level=dict(level_counter),
        first_timestamp=timestamps[0] if timestamps else None,
        last_timestamp=timestamps[-1] if timestamps else None,
        unique_sources=len(sources),
    )


def format_stats(stats: LogStats) -> str:
    """Render stats as a human-readable string."""
    lines = [
        f"Total entries : {stats.total}",
        f"First timestamp: {stats.first_timestamp or 'n/a'}",
        f"Last timestamp : {stats.last_timestamp or 'n/a'}",
        f"Unique sources : {stats.unique_sources}",
        "Level breakdown:",
    ]
    for level, count in sorted(stats.by_level.items()):
        lines.append(f"  {level:<10} {count}")
    return "\n".join(lines)
