"""Entry-level deduplication with windowed time-based grouping."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterator, List, Optional

from logsnip.parser import LogEntry


@dataclass
class DeduplicateOptions:
    window_seconds: int = 60
    max_repeats: int = 1  # keep at most this many copies per window
    level: Optional[str] = None
    pattern: Optional[str] = None


@dataclass
class DeduplicateReport:
    total_in: int = 0
    total_out: int = 0
    dropped: int = 0
    windows_seen: int = 0

    @property
    def reduction_pct(self) -> float:
        if self.total_in == 0:
            return 0.0
        return round(100.0 * self.dropped / self.total_in, 2)


def _window_key(ts: datetime, window_seconds: int) -> int:
    """Return an integer bucket id for the given timestamp."""
    epoch = datetime(1970, 1, 1)
    total_seconds = int((ts - epoch).total_seconds())
    return total_seconds // window_seconds


def deduplicate_entries(
    entries: List[LogEntry],
    opts: DeduplicateOptions,
) -> Iterator[LogEntry]:
    """Yield entries, dropping duplicates within each time window."""
    import re

    seen: dict[tuple, int] = {}
    windows: set[int] = set()

    for entry in entries:
        if opts.level and entry.level.upper() != opts.level.upper():
            yield entry
            continue
        if opts.pattern and not re.search(opts.pattern, entry.message):
            yield entry
            continue

        wk = _window_key(entry.timestamp, opts.window_seconds)
        windows.add(wk)
        key = (wk, entry.level.upper(), entry.message.strip())
        count = seen.get(key, 0)
        if count < opts.max_repeats:
            seen[key] = count + 1
            yield entry


def deduplicate_summary(entries: List[LogEntry], opts: DeduplicateOptions) -> DeduplicateReport:
    """Run deduplication and return a summary report."""
    import re

    total_in = len(entries)
    result = list(deduplicate_entries(entries, opts))
    total_out = len(result)

    windows: set = set()
    for e in entries:
        windows.add(_window_key(e.timestamp, opts.window_seconds))

    return DeduplicateReport(
        total_in=total_in,
        total_out=total_out,
        dropped=total_in - total_out,
        windows_seen=len(windows),
    )
