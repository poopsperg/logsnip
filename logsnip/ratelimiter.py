"""Rate limit log entries: keep at most N entries per time window per level."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterator, List, Optional

from logsnip.parser import LogEntry


@dataclass
class RateLimitOptions:
    max_per_window: int = 10
    window_seconds: int = 60
    level_filter: Optional[str] = None
    pattern: Optional[str] = None


@dataclass
class RateLimitReport:
    total_in: int
    total_out: int
    dropped: int

    @property
    def drop_pct(self) -> float:
        if self.total_in == 0:
            return 0.0
        return round(self.dropped / self.total_in * 100, 2)


def ratelimit_entries(
    entries: List[LogEntry], opts: RateLimitOptions
) -> Iterator[LogEntry]:
    """Yield entries, dropping those that exceed max_per_window per (level, window)."""
    if opts.max_per_window <= 0:
        raise ValueError("max_per_window must be positive")
    if opts.window_seconds <= 0:
        raise ValueError("window_seconds must be positive")

    window_delta = timedelta(seconds=opts.window_seconds)
    # bucket -> (window_start, count)
    buckets: dict[str, tuple[datetime, int]] = {}

    for entry in entries:
        if opts.level_filter and entry.level.upper() != opts.level_filter.upper():
            yield entry
            continue
        if opts.pattern:
            import re
            if not re.search(opts.pattern, entry.message):
                yield entry
                continue

        key = entry.level.upper()
        ts = entry.timestamp

        if key not in buckets:
            buckets[key] = (ts, 1)
            yield entry
        else:
            win_start, count = buckets[key]
            if ts - win_start >= window_delta:
                buckets[key] = (ts, 1)
                yield entry
            elif count < opts.max_per_window:
                buckets[key] = (win_start, count + 1)
                yield entry
            # else: drop


def ratelimit_summary(entries_in: List[LogEntry], entries_out: List[LogEntry]) -> RateLimitReport:
    total_in = len(entries_in)
    total_out = len(entries_out)
    return RateLimitReport(
        total_in=total_in,
        total_out=total_out,
        dropped=total_in - total_out,
    )
