"""Deduplication utilities for log entries."""
from __future__ import annotations

import hashlib
from typing import Iterable, Iterator, List, Optional

from logsnip.parser import LogEntry


def _entry_key(entry: LogEntry, fields: Optional[List[str]] = None) -> str:
    """Build a hash key for a log entry based on selected fields."""
    if fields is None:
        fields = ["message", "level"]
    parts = []
    for field in fields:
        value = getattr(entry, field, None)
        parts.append(str(value) if value is not None else "")
    raw = "|".join(parts)
    return hashlib.md5(raw.encode()).hexdigest()


def dedup_entries(
    entries: Iterable[LogEntry],
    fields: Optional[List[str]] = None,
) -> Iterator[LogEntry]:
    """Yield entries with duplicate messages removed (first occurrence kept)."""
    seen: set[str] = set()
    for entry in entries:
        key = _entry_key(entry, fields)
        if key not in seen:
            seen.add(key)
            yield entry


def dedup_consecutive(
    entries: Iterable[LogEntry],
    fields: Optional[List[str]] = None,
) -> Iterator[LogEntry]:
    """Yield entries, suppressing consecutive duplicates only."""
    last_key: Optional[str] = None
    for entry in entries:
        key = _entry_key(entry, fields)
        if key != last_key:
            last_key = key
            yield entry


def count_duplicates(
    entries: Iterable[LogEntry],
    fields: Optional[List[str]] = None,
) -> int:
    """Return number of duplicate entries that would be removed by dedup_entries."""
    seen: set[str] = set()
    duplicates = 0
    for entry in entries:
        key = _entry_key(entry, fields)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
    return duplicates
