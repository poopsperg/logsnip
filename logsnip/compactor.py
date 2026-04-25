"""Compactor: merge consecutive duplicate log entries into a single entry with a repeat count."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional

from logsnip.parser import LogEntry


@dataclass
class CompactedEntry:
    entry: LogEntry
    repeat_count: int = 1

    @property
    def timestamp(self):
        return self.entry.timestamp

    @property
    def level(self):
        return self.entry.level

    @property
    def message(self):
        return self.entry.message

    @property
    def is_repeated(self) -> bool:
        return self.repeat_count > 1


@dataclass
class CompactOptions:
    ignore_level: bool = False  # treat entries with same message but different level as duplicates
    min_repeats: int = 1        # only keep compacted entries with at least this many repeats


def _entry_key(entry: LogEntry, ignore_level: bool) -> tuple:
    if ignore_level:
        return (entry.message,)
    return (entry.level, entry.message)


def compact_entries(
    entries: Iterable[LogEntry],
    options: Optional[CompactOptions] = None,
) -> Iterator[CompactedEntry]:
    """Yield CompactedEntry objects, collapsing consecutive duplicates."""
    opts = options or CompactOptions()
    current: Optional[CompactedEntry] = None

    for entry in entries:
        key = _entry_key(entry, opts.ignore_level)
        if current is None:
            current = CompactedEntry(entry=entry, repeat_count=1)
            current_key = key
        elif key == current_key:
            current.repeat_count += 1
        else:
            if current.repeat_count >= opts.min_repeats:
                yield current
            current = CompactedEntry(entry=entry, repeat_count=1)
            current_key = key

    if current is not None and current.repeat_count >= opts.min_repeats:
        yield current


def compact_summary(compacted: List[CompactedEntry]) -> dict:
    total_original = sum(c.repeat_count for c in compacted)
    total_compacted = len(compacted)
    repeated = [c for c in compacted if c.is_repeated]
    return {
        "total_original": total_original,
        "total_compacted": total_compacted,
        "repeated_groups": len(repeated),
        "max_repeats": max((c.repeat_count for c in compacted), default=0),
    }
