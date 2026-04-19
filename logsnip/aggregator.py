"""Aggregate log entries by time window or level."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from logsnip.parser import LogEntry


@dataclass
class AggregateOptions:
    window_seconds: int = 60
    group_by_level: bool = False


@dataclass
class AggregatedBucket:
    key: str
    entries: List[LogEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)

    @property
    def start(self) -> Optional[datetime]:
        return self.entries[0].timestamp if self.entries else None

    @property
    def end(self) -> Optional[datetime]:
        return self.entries[-1].timestamp if self.entries else None


def aggregate_by_window(
    entries: List[LogEntry], window_seconds: int
) -> List[AggregatedBucket]:
    if not entries:
        return []
    buckets: List[AggregatedBucket] = []
    window = timedelta(seconds=window_seconds)
    current_start = entries[0].timestamp
    bucket = AggregatedBucket(key=str(current_start))
    for entry in entries:
        if entry.timestamp and entry.timestamp - current_start > window:
            buckets.append(bucket)
            current_start = entry.timestamp
            bucket = AggregatedBucket(key=str(current_start))
        bucket.entries.append(entry)
    if bucket.entries:
        buckets.append(bucket)
    return buckets


def aggregate_by_level(entries: List[LogEntry]) -> List[AggregatedBucket]:
    groups: Dict[str, AggregatedBucket] = {}
    for entry in entries:
        key = (entry.level or "UNKNOWN").upper()
        if key not in groups:
            groups[key] = AggregatedBucket(key=key)
        groups[key].entries.append(entry)
    return list(groups.values())


def aggregate(entries: List[LogEntry], opts: AggregateOptions) -> List[AggregatedBucket]:
    if opts.group_by_level:
        return aggregate_by_level(entries)
    return aggregate_by_window(entries, opts.window_seconds)
