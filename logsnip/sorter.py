"""Sorting utilities for log entries."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Literal

from logsnip.parser import LogEntry

SortKey = Literal["timestamp", "level", "line_number"]
SortOrder = Literal["asc", "desc"]


@dataclass
class SortOptions:
    key: SortKey = "timestamp"
    order: SortOrder = "asc"
    stable: bool = True


_LEVEL_PRIORITY = {
    "debug": 0,
    "info": 1,
    "warning": 2,
    "warn": 2,
    "error": 3,
    "critical": 4,
    "fatal": 4,
}


def _level_key(entry: LogEntry) -> int:
    return _LEVEL_PRIORITY.get((entry.level or "").lower(), -1)


def sort_entries(
    entries: Iterable[LogEntry],
    options: SortOptions | None = None,
) -> List[LogEntry]:
    """Return a sorted list of entries according to *options*."""
    if options is None:
        options = SortOptions()

    items = list(entries)

    if options.key == "timestamp":
        key_fn = lambda e: (e.timestamp is None, e.timestamp)  # noqa: E731
    elif options.key == "level":
        key_fn = _level_key  # type: ignore[assignment]
    else:
        key_fn = lambda e: e.line_number  # noqa: E731

    reverse = options.order == "desc"
    return sorted(items, key=key_fn, reverse=reverse)


def sort_by_timestamp(entries: Iterable[LogEntry], desc: bool = False) -> List[LogEntry]:
    """Convenience wrapper — sort by timestamp."""
    return sort_entries(entries, SortOptions(key="timestamp", order="desc" if desc else "asc"))


def sort_by_level(entries: Iterable[LogEntry], desc: bool = False) -> List[LogEntry]:
    """Convenience wrapper — sort by severity level."""
    return sort_entries(entries, SortOptions(key="level", order="desc" if desc else "asc"))
