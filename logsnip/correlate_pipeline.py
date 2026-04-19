from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.filter import apply_filters
from logsnip.correlator import CorrelationGroup, correlate_entries


@dataclass
class CorrelatePipelineOptions:
    pattern: str
    level: Optional[str] = None
    filter_pattern: Optional[str] = None
    exclude: Optional[str] = None
    min_group_size: int = 1


def run_correlate_pipeline(
    entries: List[LogEntry], opts: CorrelatePipelineOptions
) -> List[CorrelationGroup]:
    filtered = apply_filters(
        entries,
        level=opts.level,
        pattern=opts.filter_pattern,
        exclude=opts.exclude,
    )
    groups = correlate_entries(filtered, opts.pattern)
    return [g for g in groups if g.count >= opts.min_group_size]


def correlate_summary(groups: List[CorrelationGroup]) -> str:
    total = sum(g.count for g in groups)
    return (
        f"{len(groups)} correlation group(s), {total} total matched entries"
    )
