"""Log chunk parser — extracts structured log entries from a file."""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator

# Matches common log timestamp formats like: 2024-01-15 12:34:56 or 2024-01-15T12:34:56
TIMESTAMP_RE = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})"
)

TS_FORMATS = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]


@dataclass
class LogEntry:
    timestamp: datetime
    raw: str
    line_number: int


def parse_timestamp(ts_str: str) -> datetime | None:
    for fmt in TS_FORMATS:
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            continue
    return None


def iter_entries(file_path: str) -> Iterator[LogEntry]:
    """Yield LogEntry objects for every line that contains a parseable timestamp."""
    with open(file_path, "r", errors="replace") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.rstrip("\n")
            match = TIMESTAMP_RE.search(line)
            if match:
                ts = parse_timestamp(match.group("ts"))
                if ts:
                    yield LogEntry(timestamp=ts, raw=line, line_number=lineno)


def filter_by_range(
    entries: Iterator[LogEntry],
    start: datetime | None,
    end: datetime | None,
) -> Iterator[LogEntry]:
    """Filter entries to those whose timestamp falls within [start, end]."""
    for entry in entries:
        if start and entry.timestamp < start:
            continue
        if end and entry.timestamp > end:
            continue
        yield entry
