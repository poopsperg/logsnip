from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from logsnip.enricher import EnrichOptions, EnrichRule, EnrichedEntry, enrich_entries, enrich_summary
from logsnip.filter import apply_filters
from logsnip.parser import LogEntry


@dataclass
class EnrichPipelineOptions:
    rules: List[EnrichRule] = field(default_factory=list)
    level_filter: Optional[str] = None
    pattern_filter: Optional[str] = None
    skip_empty: bool = True


def run_enrich_pipeline(
    entries: Iterable[LogEntry],
    options: EnrichPipelineOptions,
) -> List[EnrichedEntry]:
    filtered = apply_filters(
        list(entries),
        level=options.level_filter,
        pattern=options.pattern_filter,
    )
    enrich_opts = EnrichOptions(
        rules=options.rules,
        skip_empty=options.skip_empty,
    )
    return enrich_entries(filtered, enrich_opts)


def pipeline_summary(enriched: List[EnrichedEntry]) -> str:
    return enrich_summary(enriched)
