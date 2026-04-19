"""Pipeline helpers for diffing two log sources."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.filter import apply_filters
from logsnip.differ import DiffResult, diff_entries, format_diff


@dataclass
class DiffPipelineOptions:
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None


def run_diff_pipeline(
    stream_a: List[LogEntry],
    stream_b: List[LogEntry],
    opts: DiffPipelineOptions | None = None,
) -> DiffResult:
    if opts is None:
        opts = DiffPipelineOptions()

    def _filter(entries):
        return list(apply_filters(
            entries,
            level=opts.level,
            pattern=opts.pattern,
            exclude=opts.exclude,
        ))

    return diff_entries(_filter(stream_a), _filter(stream_b))


def diff_summary(result: DiffResult) -> dict:
    return {
        "common": len(result.common),
        "only_in_a": len(result.only_in_a),
        "only_in_b": len(result.only_in_b),
        "total_a": result.total_a,
        "total_b": result.total_b,
    }
