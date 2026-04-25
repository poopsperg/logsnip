"""Pipeline wrapper for the compactor module."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from logsnip.compactor import CompactOptions, CompactedEntry, compact_entries, compact_summary
from logsnip.filter import apply_filters
from logsnip.parser import LogEntry


@dataclass
class CompactPipelineOptions:
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None
    ignore_level: bool = False
    min_repeats: int = 1


def run_compact_pipeline(
    entries: List[LogEntry],
    options: Optional[CompactPipelineOptions] = None,
) -> List[CompactedEntry]:
    opts = options or CompactPipelineOptions()

    filtered = apply_filters(
        entries,
        level=opts.level,
        pattern=opts.pattern,
        exclude=opts.exclude,
    )

    compact_opts = CompactOptions(
        ignore_level=opts.ignore_level,
        min_repeats=opts.min_repeats,
    )

    return list(compact_entries(filtered, compact_opts))


def pipeline_summary(compacted: List[CompactedEntry]) -> str:
    stats = compact_summary(compacted)
    return (
        f"original={stats['total_original']} "
        f"compacted={stats['total_compacted']} "
        f"repeated_groups={stats['repeated_groups']} "
        f"max_repeats={stats['max_repeats']}"
    )
