"""High-level pipeline combining parsing, filtering, and rendering."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator, List, Optional, TextIO

from logsnip.parser import LogEntry, iter_entries, filter_by_range
from logsnip.filter import apply_filters
from logsnip.render import render_entries
from logsnip.theme import Theme, get_theme


@dataclass
class PipelineOptions:
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    levels: List[str] = field(default_factory=list)
    pattern: Optional[str] = None
    exclude: Optional[str] = None
    ignore_case: bool = False
    highlight: Optional[str] = None
    no_color: bool = False


def run_pipeline(
    source: TextIO,
    opts: PipelineOptions,
) -> Iterator[str]:
    """Parse, filter, and render log entries from *source*, yielding formatted lines."""
    entries = iter_entries(source)

    if opts.start or opts.end:
        entries = filter_by_range(entries, start=opts.start, end=opts.end)

    entries = apply_filters(
        entries,
        levels=opts.levels or None,
        pattern=opts.pattern,
        exclude=opts.exclude,
        ignore_case=opts.ignore_case,
    )

    theme: Theme = get_theme(no_color=opts.no_color)

    yield from render_entries(entries, theme=theme, highlight=opts.highlight)


def collect_pipeline(
    source: TextIO,
    opts: PipelineOptions,
) -> List[LogEntry]:
    """Run the parse + filter stages and return a list of matching LogEntry objects."""
    entries = iter_entries(source)

    if opts.start or opts.end:
        entries = filter_by_range(entries, start=opts.start, end=opts.end)

    return list(
        apply_filters(
            entries,
            levels=opts.levels or None,
            pattern=opts.pattern,
            exclude=opts.exclude,
            ignore_case=opts.ignore_case,
        )
    )
