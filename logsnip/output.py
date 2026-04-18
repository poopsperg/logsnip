"""Handles writing formatted output to stdout or a file."""

import sys
from pathlib import Path
from typing import Iterable

from logsnip.parser import LogEntry
from logsnip.formatter import format_entries, SUPPORTED_FORMATS


def write_output(
    entries: Iterable[LogEntry],
    fmt: str = "text",
    output_path: str | None = None,
) -> None:
    """Format entries and write to file or stdout.

    Args:
        entries: Iterable of LogEntry objects to output.
        fmt: Output format — one of SUPPORTED_FORMATS.
        output_path: If given, write to this file path; otherwise use stdout.

    Raises:
        ValueError: If fmt is not a supported format.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    content = format_entries(entries, fmt)

    if not content:
        return

    if output_path:
        dest = Path(output_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content + "\n", encoding="utf-8")
    else:
        sys.stdout.write(content + "\n")


def count_and_write(
    entries: Iterable[LogEntry],
    fmt: str = "text",
    output_path: str | None = None,
) -> int:
    """Write entries and return how many were written."""
    entries = list(entries)
    write_output(entries, fmt=fmt, output_path=output_path)
    return len(entries)
