"""Merge multiple sorted log entry streams into one."""
from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Iterable, Iterator, List

from logsnip.parser import LogEntry


@dataclass
class MergeOptions:
    deduplicate: bool = False
    stable: bool = True  # preserve original order on timestamp ties


def merge_entries(
    streams: List[Iterable[LogEntry]],
    options: MergeOptions | None = None,
) -> Iterator[LogEntry]:
    """Merge multiple iterables of LogEntry sorted by timestamp."""
    if options is None:
        options = MergeOptions()

    # heapq needs comparable items; use (timestamp, stream_index, entry)
    heap: list = []
    iters = [iter(s) for s in streams]

    for idx, it in enumerate(iters):
        entry = next(it, None)
        if entry is not None:
            heapq.heappush(heap, (entry.timestamp, idx, entry, it))

    seen: set = set()
    prev: LogEntry | None = None

    while heap:
        ts, idx, entry, it = heapq.heappop(heap)

        if options.deduplicate:
            key = (entry.timestamp, entry.level, entry.message)
            if key in seen:
                _advance(heap, idx, it)
                continue
            seen.add(key)

        yield entry
        prev = entry
        _advance(heap, idx, it)


def _advance(heap: list, idx: int, it) -> None:
    entry = next(it, None)
    if entry is not None:
        heapq.heappush(heap, (entry.timestamp, idx, entry, it))


def merge_files_entries(
    entry_lists: List[List[LogEntry]],
    options: MergeOptions | None = None,
) -> List[LogEntry]:
    """Convenience wrapper returning a list."""
    return list(merge_entries(entry_lists, options))
