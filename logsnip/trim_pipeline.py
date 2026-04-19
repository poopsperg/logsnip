from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.filter import apply_filters
from logsnip.trimmer import TrimOptions, trim_entries, trim_summary


@dataclass
class TrimPipelineOptions:
    head: Optional[int] = None
    tail: Optional[int] = None
    drop_duplicates: bool = False
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None


def run_trim_pipeline(
    entries: List[LogEntry],
    options: TrimPipelineOptions,
) -> List[LogEntry]:
    filtered = apply_filters(
        entries,
        level=options.level,
        pattern=options.pattern,
        exclude=options.exclude,
    )
    trim_opts = TrimOptions(
        head=options.head,
        tail=options.tail,
        drop_duplicates=options.drop_duplicates,
    )
    return trim_entries(filtered, trim_opts)


def pipeline_summary(
    original: List[LogEntry],
    result: List[LogEntry],
) -> dict:
    return trim_summary(original, result)
