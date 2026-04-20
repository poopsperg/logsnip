from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from logsnip.parser import LogEntry
from logsnip.filter import apply_filters
from logsnip.classifier import (
    ClassifyOptions,
    ClassifyRule,
    ClassifiedEntry,
    classify_entries,
    group_by_label,
)


@dataclass
class ClassifyPipelineOptions:
    rules: List[ClassifyRule] = field(default_factory=list)
    default_label: Optional[str] = None
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None


def run_classify_pipeline(
    entries: List[LogEntry],
    options: ClassifyPipelineOptions,
) -> List[ClassifiedEntry]:
    filtered = apply_filters(
        entries,
        level=options.level,
        pattern=options.pattern,
        exclude=options.exclude,
    )
    opts = ClassifyOptions(
        rules=options.rules,
        default_label=options.default_label,
    )
    return classify_entries(filtered, opts)


def classify_summary(
    classified: List[ClassifiedEntry],
) -> Dict[str, int]:
    groups = group_by_label(classified)
    return {label: len(items) for label, items in sorted(groups.items())}
