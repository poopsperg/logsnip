from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from logsnip.parser import LogEntry
from logsnip.filter import apply_filters
from logsnip.indexer import LogIndex, build_index, index_summary


@dataclass
class IndexPipelineOptions:
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None


def run_index_pipeline(
    entries: List[LogEntry],
    options: Optional[IndexPipelineOptions] = None,
) -> LogIndex:
    if options is None:
        options = IndexPipelineOptions()
    filtered = apply_filters(
        entries,
        level=options.level,
        pattern=options.pattern,
        exclude=options.exclude,
    )
    return build_index(filtered)


def index_pipeline_summary(index: LogIndex) -> str:
    return index_summary(index)
