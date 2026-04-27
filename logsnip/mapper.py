from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from logsnip.parser import LogEntry


@dataclass
class MapRule:
    field: str  # 'level', 'message', or 'raw'
    pattern: str
    replacement: str

    def __post_init__(self) -> None:
        if self.field not in ("level", "message", "raw"):
            raise ValueError(f"Invalid field: {self.field!r}")
        if not self.pattern:
            raise ValueError("pattern must not be empty")
        re.compile(self.pattern)  # validate regex

    def apply(self, entry: LogEntry) -> LogEntry:
        value = getattr(entry, self.field)
        new_value = re.sub(self.pattern, self.replacement, value)
        return LogEntry(
            timestamp=entry.timestamp,
            level=new_value if self.field == "level" else entry.level,
            message=new_value if self.field == "message" else entry.message,
            raw=new_value if self.field == "raw" else entry.raw,
            line_number=entry.line_number,
        )


@dataclass
class MapOptions:
    rules: List[MapRule] = field(default_factory=list)
    level_filter: Optional[str] = None
    pattern_filter: Optional[str] = None


def map_entry(entry: LogEntry, rules: List[MapRule]) -> LogEntry:
    for rule in rules:
        entry = rule.apply(entry)
    return entry


def map_entries(
    entries: List[LogEntry],
    rules: List[MapRule],
    level_filter: Optional[str] = None,
    pattern_filter: Optional[str] = None,
) -> List[LogEntry]:
    result = []
    for entry in entries:
        if level_filter and entry.level.upper() != level_filter.upper():
            result.append(entry)
            continue
        if pattern_filter and not re.search(pattern_filter, entry.message):
            result.append(entry)
            continue
        result.append(map_entry(entry, rules))
    return result


def map_summary(original: List[LogEntry], mapped: List[LogEntry]) -> str:
    changed = sum(
        1 for a, b in zip(original, mapped)
        if a.level != b.level or a.message != b.message or a.raw != b.raw
    )
    return f"mapped {len(mapped)} entries, {changed} modified"
