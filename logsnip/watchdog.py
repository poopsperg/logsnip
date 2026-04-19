"""Watch a log file for new entries and emit them as they arrive."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator

from logsnip.parser import LogEntry, iter_entries
from logsnip.filter import apply_filters


@dataclass
class WatchOptions:
    level: list[str] = field(default_factory=list)
    pattern: str | None = None
    exclude: str | None = None
    poll_interval: float = 0.5
    max_idle: float | None = None  # seconds before giving up; None = forever


def _read_new_lines(path: Path, offset: int) -> tuple[list[str], int]:
    with path.open("r", errors="replace") as fh:
        fh.seek(offset)
        lines = fh.readlines()
        new_offset = fh.tell()
    return lines, new_offset


def watch_file(
    path: Path,
    options: WatchOptions | None = None,
    *,
    callback: Callable[[LogEntry], None] | None = None,
) -> Iterator[LogEntry]:
    """Yield new LogEntry objects as they are appended to *path*."""
    opts = options or WatchOptions()
    offset = path.stat().st_size if path.exists() else 0
    idle_elapsed = 0.0

    while True:
        lines, new_offset = _read_new_lines(path, offset)
        if lines:
            idle_elapsed = 0.0
            entries = list(iter_entries(lines))
            entries = apply_filters(
                entries,
                levels=opts.level,
                pattern=opts.pattern,
                exclude=opts.exclude,
            )
            for entry in entries:
                if callback:
                    callback(entry)
                yield entry
            offset = new_offset
        else:
            idle_elapsed += opts.poll_interval
            if opts.max_idle is not None and idle_elapsed >= opts.max_idle:
                return
        time.sleep(opts.poll_interval)


def watch_summary(entries: list[LogEntry]) -> dict:
    from collections import Counter
    levels = Counter(e.level for e in entries)
    return {
        "total": len(entries),
        "levels": dict(levels),
    }
