"""Partition log entries into named buckets based on rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

from logsnip.parser import LogEntry


@dataclass
class PartitionRule:
    name: str
    level: Optional[str] = None
    pattern: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("PartitionRule name must not be empty")
        if self.level is None and self.pattern is None:
            raise ValueError("PartitionRule must have at least one of level or pattern")

    def matches(self, entry: LogEntry) -> bool:
        if self.level and entry.level.upper() != self.level.upper():
            return False
        if self.pattern and not re.search(self.pattern, entry.message, re.IGNORECASE):
            return False
        return True


@dataclass
class Partition:
    name: str
    entries: List[LogEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)

    @property
    def start(self) -> Optional[object]:
        return self.entries[0].timestamp if self.entries else None

    @property
    def end(self) -> Optional[object]:
        return self.entries[-1].timestamp if self.entries else None


@dataclass
class PartitionOptions:
    rules: List[PartitionRule]
    default_bucket: str = "unmatched"


def partition_entries(
    entries: List[LogEntry],
    options: PartitionOptions,
) -> Dict[str, Partition]:
    buckets: Dict[str, Partition] = {}
    for rule in options.rules:
        if rule.name not in buckets:
            buckets[rule.name] = Partition(name=rule.name)
    if options.default_bucket not in buckets:
        buckets[options.default_bucket] = Partition(name=options.default_bucket)

    for entry in entries:
        matched = False
        for rule in options.rules:
            if rule.matches(entry):
                buckets[rule.name].entries.append(entry)
                matched = True
                break
        if not matched:
            buckets[options.default_bucket].entries.append(entry)

    return buckets


def partition_summary(partitions: Dict[str, Partition]) -> str:
    lines = ["Partition summary:"]
    for name, part in partitions.items():
        lines.append(f"  {name}: {part.count} entries")
    return "\n".join(lines)
