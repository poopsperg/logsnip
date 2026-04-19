from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.labeler import LabelRule, LabeledEntry, label_entries, filter_by_label
from logsnip.filter import filter_by_level, filter_by_pattern


@dataclass
class LabelPipelineOptions:
    rules: List[LabelRule] = field(default_factory=list)
    filter_label: Optional[str] = None
    level: Optional[str] = None
    pattern: Optional[str] = None


def run_label_pipeline(
    entries: List[LogEntry], options: LabelPipelineOptions
) -> List[LabeledEntry]:
    filtered = list(entries)
    if options.level:
        filtered = filter_by_level(filtered, [options.level])
    if options.pattern:
        filtered = filter_by_pattern(filtered, options.pattern)
    labeled = label_entries(filtered, options.rules)
    if options.filter_label:
        labeled = filter_by_label(labeled, options.filter_label)
    return labeled


def label_pipeline_summary(labeled: List[LabeledEntry]) -> dict:
    label_counts: dict = {}
    for e in labeled:
        for lbl in e.labels:
            label_counts[lbl] = label_counts.get(lbl, 0) + 1
    return {"total": len(labeled), "label_counts": label_counts}
