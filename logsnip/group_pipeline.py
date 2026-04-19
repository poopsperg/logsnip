from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from logsnip.parser import LogEntry
from logsnip.filter import apply_filters
from logsnip.grouper import EntryGroup, GroupOptions, group_entries, group_summary


@dataclass
class GroupPipelineOptions:
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None
    group_key: str = "level"
    min_size: int = 1


def run_group_pipeline(
    entries: List[LogEntry],
    options: Optional[GroupPipelineOptions] = None,
) -> Dict[str, EntryGroup]:
    opts = options or GroupPipelineOptions()
    filtered = apply_filters(
        entries,
        level=opts.level,
        pattern=opts.pattern,
        exclude=opts.exclude,
    )
    gopts = GroupOptions(key=opts.group_key, min_size=opts.min_size)
    return group_entries(filtered, gopts)


def pipeline_summary(groups: Dict[str, EntryGroup]) -> str:
    return group_summary(groups)
