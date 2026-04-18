"""Split log entries into time-based or size-based chunks."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterator, List

from logsnip.parser import LogEntry


@dataclass
class Chunk:
    index: int
    entries: List[LogEntry]

    @property
    def start(self) -> datetime | None:
        return self.entries[0].timestamp if self.entries else None

    @property
    def end(self) -> datetime | None:
        return self.entries[-1].timestamp if self.entries else None

    @property
    def size(self) -> int:
        return len(self.entries)


def chunk_by_size(entries: List[LogEntry], size: int) -> Iterator[Chunk]:
    """Yield chunks of at most `size` entries."""
    if size <= 0:
        raise ValueError("size must be a positive integer")
    for i in range(0, len(entries), size):
        yield Chunk(index=i // size, entries=entries[i : i + size])


def chunk_by_time(entries: List[LogEntry], window: timedelta) -> Iterator[Chunk]:
    """Yield chunks grouped by a fixed time window."""
    if window.total_seconds() <= 0:
        raise ValueError("window must be a positive timedelta")
    if not entries:
        return

    chunk_entries: List[LogEntry] = []
    chunk_index = 0
    window_start: datetime | None = None

    for entry in entries:
        ts = entry.timestamp
        if ts is None:
            chunk_entries.append(entry)
            continue
        if window_start is None:
            window_start = ts
        if ts - window_start >= window:
            if chunk_entries:
                yield Chunk(index=chunk_index, entries=chunk_entries)
                chunk_index += 1
            chunk_entries = [entry]
            window_start = ts
        else:
            chunk_entries.append(entry)

    if chunk_entries:
        yield Chunk(index=chunk_index, entries=chunk_entries)
