"""Render log entries to terminal with optional highlighting."""

from __future__ import annotations

import sys
from typing import Iterable, Optional, TextIO

from logsnip.parser import LogEntry
from logsnip.highlighter import highlight_line, strip_ansi
from logsnip.theme import Theme, get_theme


def render_entry(
    entry: LogEntry,
    theme: Theme,
    pattern: Optional[str] = None,
    show_line_numbers: bool = False,
) -> str:
    """Render a single LogEntry as a (possibly colored) string."""
    parts = []
    if show_line_numbers:
        parts.append(f"[{entry.line_number}] ")

    line = entry.raw.rstrip("\n")

    if theme.enabled:
        line = highlight_line(line, level=entry.level, pattern=pattern)
    elif pattern:
        # no color but still want to keep raw text intact
        pass

    parts.append(line)
    return "".join(parts)


def render_entries(
    entries: Iterable[LogEntry],
    *,
    no_color: bool = False,
    pattern: Optional[str] = None,
    show_line_numbers: bool = False,
    file: TextIO = sys.stdout,
) -> int:
    """Render multiple entries to *file*. Returns count of entries written."""
    theme = get_theme(no_color=no_color)
    count = 0
    for entry in entries:
        line = render_entry(
            entry,
            theme=theme,
            pattern=pattern,
            show_line_numbers=show_line_numbers,
        )
        print(line, file=file)
        count += 1
    return count
