from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from logsnip.parser import LogEntry


@dataclass
class IndexEntry:
    line_number: int
    timestamp: datetime
    level: str
    message: str


@dataclass
class LogIndex:
    entries: List[IndexEntry] = field(default_factory=list)
    by_level: Dict[str, List[int]] = field(default_factory=dict)
    by_minute: Dict[str, List[int]] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return len(self.entries)

    def lookup_level(self, level: str) -> List[IndexEntry]:
        level = level.upper()
        indices = self.by_level.get(level, [])
        return [self.entries[i] for i in indices]

    def lookup_minute(self, minute_key: str) -> List[IndexEntry]:
        indices = self.by_minute.get(minute_key, [])
        return [self.entries[i] for i in indices]


def _minute_key(ts: datetime) -> str:
    return ts.strftime("%Y-%m-%dT%H:%M")


def build_index(entries: List[LogEntry]) -> LogIndex:
    index = LogIndex()
    for pos, entry in enumerate(entries):
        ie = IndexEntry(
            line_number=entry.line_number,
            timestamp=entry.timestamp,
            level=entry.level.upper(),
            message=entry.message,
        )
        index.entries.append(ie)
        index.by_level.setdefault(ie.level, []).append(pos)
        mk = _minute_key(entry.timestamp)
        index.by_minute.setdefault(mk, []).append(pos)
    return index


def index_summary(index: LogIndex) -> str:
    level_counts = ", ".join(
        f"{lvl}={len(idx)}" for lvl, idx in sorted(index.by_level.items())
    )
    minutes = len(index.by_minute)
    return (
        f"Indexed {index.total} entries | "
        f"levels: [{level_counts}] | "
        f"minutes spanned: {minutes}"
    )
