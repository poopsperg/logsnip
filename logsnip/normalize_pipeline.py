"""Pipeline wrapper for entry normalization."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from logsnip.filter import apply_filters
from logsnip.normalizer import NormalizeOptions, normalize_entries, normalize_summary
from logsnip.parser import LogEntry


@dataclass
class NormalizePipelineOptions:
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None
    normalize: NormalizeOptions = field(default_factory=NormalizeOptions)


def run_normalize_pipeline(
    entries: List[LogEntry], opts: NormalizePipelineOptions
) -> List[LogEntry]:
    """Filter then normalize entries."""
    filtered = apply_filters(
        entries,
        level=opts.level,
        pattern=opts.pattern,
        exclude=opts.exclude,
    )
    return list(normalize_entries(filtered, opts.normalize))


def pipeline_summary(original: List[LogEntry], result: List[LogEntry]) -> str:
    return normalize_summary(original, result)
