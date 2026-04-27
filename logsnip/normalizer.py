"""Normalize log entries: standardize levels, strip whitespace, unify timestamp precision."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Iterator, List, Optional

from logsnip.parser import LogEntry

_LEVEL_ALIASES: dict[str, str] = {
    "warn": "WARNING",
    "warning": "WARNING",
    "err": "ERROR",
    "error": "ERROR",
    "info": "INFO",
    "information": "INFO",
    "dbg": "DEBUG",
    "debug": "DEBUG",
    "crit": "CRITICAL",
    "critical": "CRITICAL",
    "fatal": "CRITICAL",
}


@dataclass
class NormalizeOptions:
    strip_message: bool = True
    canonical_level: bool = True
    utc_timestamps: bool = True
    max_message_length: Optional[int] = None


def normalize_level(level: str) -> str:
    """Return a canonical level string."""
    return _LEVEL_ALIASES.get(level.lower(), level.upper())


def normalize_entry(entry: LogEntry, opts: NormalizeOptions) -> LogEntry:
    """Return a new LogEntry with normalized fields."""
    message = entry.message
    if opts.strip_message:
        message = message.strip()
    if opts.max_message_length and len(message) > opts.max_message_length:
        message = message[: opts.max_message_length]

    level = entry.level
    if opts.canonical_level:
        level = normalize_level(level)

    ts = entry.timestamp
    if opts.utc_timestamps and ts is not None and ts.tzinfo is not None:
        ts = ts.astimezone(timezone.utc)

    return LogEntry(timestamp=ts, level=level, message=message, raw=entry.raw, line=entry.line)


def normalize_entries(
    entries: Iterable[LogEntry], opts: Optional[NormalizeOptions] = None
) -> Iterator[LogEntry]:
    """Yield normalized log entries."""
    if opts is None:
        opts = NormalizeOptions()
    for entry in entries:
        yield normalize_entry(entry, opts)


def normalize_summary(original: List[LogEntry], normalized: List[LogEntry]) -> str:
    levels_before = {e.level for e in original}
    levels_after = {e.level for e in normalized}
    return (
        f"Normalized {len(normalized)} entries. "
        f"Levels before: {sorted(levels_before)} -> after: {sorted(levels_after)}"
    )
