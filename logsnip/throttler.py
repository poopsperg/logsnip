"""Rate-based throttling: keep at most N entries per time window."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterator, List

from logsnip.parser import LogEntry


@dataclass
class ThrottleOptions:
    max_per_window: int = 10
    window_seconds: int = 60
    level: str | None = None
    pattern: str | None = None


def throttle_entries(
    entries: List[LogEntry],
    options: ThrottleOptions,
) -> Iterator[LogEntry]:
    """Yield at most *max_per_window* entries per rolling time window."""
    if options.max_per_window <= 0:
        raise ValueError("max_per_window must be a positive integer")
    if options.window_seconds <= 0:
        raise ValueError("window_seconds must be a positive integer")

    window = timedelta(seconds=options.window_seconds)
    bucket: List[datetime] = []

    for entry in entries:
        if options.level and entry.level.upper() != options.level.upper():
            continue
        if options.pattern and options.pattern not in entry.message:
            continue

        cutoff = entry.timestamp - window
        bucket = [t for t in bucket if t > cutoff]

        if len(bucket) < options.max_per_window:
            bucket.append(entry.timestamp)
            yield entry


def throttle_summary(original: List[LogEntry], throttled: List[LogEntry]) -> str:
    dropped = len(original) - len(throttled)
    return (
        f"Throttle summary: {len(original)} input entries, "
        f"{len(throttled)} kept, {dropped} dropped."
    )
