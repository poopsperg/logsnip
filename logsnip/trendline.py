from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Sequence

from logsnip.parser import LogEntry


@dataclass
class TrendBucket:
    minute: datetime
    count: int
    levels: Dict[str, int]

    @property
    def top_level(self) -> str:
        if not self.levels:
            return "UNKNOWN"
        return max(self.levels, key=lambda k: self.levels[k])


@dataclass
class TrendOptions:
    window_minutes: int = 1
    level_filter: str | None = None
    pattern: str | None = None


def _bucket_key(entry: LogEntry, window_minutes: int) -> datetime:
    ts = entry.timestamp
    floored = ts.replace(second=0, microsecond=0)
    slot = (floored.minute // window_minutes) * window_minutes
    return floored.replace(minute=slot)


def compute_trend(
    entries: Sequence[LogEntry],
    options: TrendOptions | None = None,
) -> List[TrendBucket]:
    opts = options or TrendOptions()
    buckets: Dict[datetime, Dict[str, int]] = {}

    for entry in entries:
        if opts.level_filter and entry.level.upper() != opts.level_filter.upper():
            continue
        if opts.pattern and opts.pattern.lower() not in entry.message.lower():
            continue

        key = _bucket_key(entry, opts.window_minutes)
        if key not in buckets:
            buckets[key] = {}
        level = entry.level.upper()
        buckets[key][level] = buckets[key].get(level, 0) + 1

    return [
        TrendBucket(minute=k, count=sum(v.values()), levels=v)
        for k, v in sorted(buckets.items())
    ]


def format_trend(buckets: List[TrendBucket], bar_width: int = 20) -> str:
    if not buckets:
        return "No trend data."

    max_count = max(b.count for b in buckets) or 1
    lines = []
    for bucket in buckets:
        bar_len = int((bucket.count / max_count) * bar_width)
        bar = "#" * bar_len
        ts = bucket.minute.strftime("%Y-%m-%d %H:%M")
        lines.append(f"{ts} | {bar:<{bar_width}} | {bucket.count:>4} [{bucket.top_level}]")
    return "\n".join(lines)
