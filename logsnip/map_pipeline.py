from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from logsnip.mapper import MapOptions, MapRule, map_entries, map_summary
from logsnip.filter import filter_by_level, filter_by_pattern
from logsnip.parser import LogEntry


@dataclass
class MapPipelineOptions:
    rules: List[MapRule] = field(default_factory=list)
    level_filter: Optional[str] = None
    pattern_filter: Optional[str] = None


def run_map_pipeline(
    entries: List[LogEntry],
    options: MapPipelineOptions,
) -> List[LogEntry]:
    working = list(entries)
    if options.level_filter:
        scoped = filter_by_level(working, [options.level_filter])
    else:
        scoped = working

    if options.pattern_filter:
        scoped = filter_by_pattern(scoped, options.pattern_filter)

    mapped_set = {id(e): map_entries([e], options.rules)[0] for e in scoped}

    return [mapped_set.get(id(e), e) for e in working]


def pipeline_summary(original: List[LogEntry], result: List[LogEntry]) -> str:
    return map_summary(original, result)
