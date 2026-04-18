"""Pipeline integration for entry annotation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from logsnip.parser import LogEntry
from logsnip.annotator import AnnotationRule, AnnotatedEntry, annotate_entries, filter_by_tag


@dataclass
class AnnotatePipelineOptions:
    rules: List[AnnotationRule] = field(default_factory=list)
    filter_tag: Optional[str] = None


def run_annotate_pipeline(
    entries: List[LogEntry],
    options: AnnotatePipelineOptions,
) -> List[AnnotatedEntry]:
    annotated = annotate_entries(entries, options.rules)
    if options.filter_tag:
        annotated = filter_by_tag(annotated, options.filter_tag)
    return annotated


def annotate_summary(annotated: List[AnnotatedEntry]) -> dict:
    tag_counts: dict = {}
    untagged = 0
    for a in annotated:
        if not a.tags:
            untagged += 1
        for tag in a.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    return {
        "total": len(annotated),
        "untagged": untagged,
        "by_tag": tag_counts,
    }
