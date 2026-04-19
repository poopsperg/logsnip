from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.tagger import TagRule, TaggedEntry, tag_entries, filter_by_tag, tag_summary


@dataclass
class TagPipelineOptions:
    rules: List[TagRule] = field(default_factory=list)
    filter_tag: Optional[str] = None


def run_tag_pipeline(
    entries: List[LogEntry], options: TagPipelineOptions
) -> List[TaggedEntry]:
    tagged = tag_entries(entries, options.rules)
    if options.filter_tag:
        tagged = filter_by_tag(tagged, options.filter_tag)
    return tagged


def tag_pipeline_summary(tagged: List[TaggedEntry]) -> str:
    counts = tag_summary(tagged)
    if not counts:
        return "no tags applied"
    parts = [f"{tag}: {count}" for tag, count in sorted(counts.items())]
    return "tag counts — " + ", ".join(parts)
