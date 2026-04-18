"""Pattern and level filtering for log entries."""
from __future__ import annotations

import re
from typing import Iterable, Iterator, List, Optional

from logsnip.parser import LogEntry


def filter_by_level(
    entries: Iterable[LogEntry],
    levels: List[str],
) -> Iterator[LogEntry]:
    """Yield entries whose level matches one of the given levels (case-insensitive)."""
    normalized = {lvl.upper() for lvl in levels}
    for entry in entries:
        if entry.level.upper() in normalized:
            yield entry


def filter_by_pattern(
    entries: Iterable[LogEntry],
    pattern: str,
    ignore_case: bool = False,
) -> Iterator[LogEntry]:
    """Yield entries whose message matches the given regex pattern."""
    flags = re.IGNORECASE if ignore_case else 0
    compiled = re.compile(pattern, flags)
    for entry in entries:
        if compiled.search(entry.message):
            yield entry


def filter_by_exclude(
    entries: Iterable[LogEntry],
    pattern: str,
    ignore_case: bool = False,
) -> Iterator[LogEntry]:
    """Yield entries whose message does NOT match the given regex pattern."""
    flags = re.IGNORECASE if ignore_case else 0
    compiled = re.compile(pattern, flags)
    for entry in entries:
        if not compiled.search(entry.message):
            yield entry


def apply_filters(
    entries: Iterable[LogEntry],
    levels: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    exclude: Optional[str] = None,
    ignore_case: bool = False,
) -> Iterator[LogEntry]:
    """Apply all active filters in sequence."""
    result: Iterable[LogEntry] = entries
    if levels:
        result = filter_by_level(result, levels)
    if pattern:
        result = filter_by_pattern(result, pattern, ignore_case=ignore_case)
    if exclude:
        result = filter_by_exclude(result, exclude, ignore_case=ignore_case)
    yield from result
