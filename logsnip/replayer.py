"""Replay log entries with simulated timing delays."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Iterable, Iterator

from logsnip.parser import LogEntry


@dataclass
class ReplayOptions:
    speed: float = 1.0        # multiplier; 2.0 = twice as fast
    max_delay: float = 5.0    # cap delay between entries (seconds)
    real_time: bool = True    # if False, yield instantly (dry run)


@dataclass
class ReplayEvent:
    entry: LogEntry
    delay: float              # seconds waited before this entry
    elapsed: float            # total elapsed time so far


def _compute_delay(prev: LogEntry, curr: LogEntry, opts: ReplayOptions) -> float:
    if prev is None:
        return 0.0
    delta = (curr.timestamp - prev.timestamp).total_seconds()
    delay = delta / max(opts.speed, 1e-6)
    return min(delay, opts.max_delay)


def replay_entries(
    entries: Iterable[LogEntry],
    opts: ReplayOptions | None = None,
    on_event: Callable[[ReplayEvent], None] | None = None,
) -> Iterator[ReplayEvent]:
    """Yield ReplayEvent for each entry, sleeping according to log timestamps."""
    if opts is None:
        opts = ReplayOptions()

    prev: LogEntry | None = None
    elapsed = 0.0

    for entry in entries:
        delay = _compute_delay(prev, entry, opts)
        if opts.real_time and delay > 0:
            time.sleep(delay)
        elapsed += delay
        event = ReplayEvent(entry=entry, delay=delay, elapsed=elapsed)
        if on_event:
            on_event(event)
        yield event
        prev = entry


def replay_summary(events: list[ReplayEvent]) -> dict:
    if not events:
        return {"total": 0, "elapsed": 0.0, "avg_delay": 0.0}
    total_elapsed = events[-1].elapsed
    delays = [e.delay for e in events]
    return {
        "total": len(events),
        "elapsed": round(total_elapsed, 4),
        "avg_delay": round(sum(delays) / len(delays), 4),
        "max_delay": round(max(delays), 4),
    }
