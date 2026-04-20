from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from logsnip.parser import LogEntry


@dataclass
class ClassifyRule:
    label: str
    pattern: Optional[str] = None
    level: Optional[str] = None
    priority: int = 0

    def __post_init__(self) -> None:
        if not self.label:
            raise ValueError("label must not be empty")
        if not self.pattern and not self.level:
            raise ValueError("at least one of pattern or level must be set")

    def matches(self, entry: LogEntry) -> bool:
        level_match = (
            self.level is None
            or entry.level.upper() == self.level.upper()
        )
        pattern_match = (
            self.pattern is None
            or self.pattern.lower() in entry.message.lower()
        )
        return level_match and pattern_match


@dataclass
class ClassifiedEntry:
    entry: LogEntry
    labels: List[str] = field(default_factory=list)

    @property
    def timestamp(self):
        return self.entry.timestamp

    @property
    def level(self):
        return self.entry.level

    @property
    def message(self):
        return self.entry.message

    def has_label(self, label: str) -> bool:
        return label in self.labels


@dataclass
class ClassifyOptions:
    rules: List[ClassifyRule] = field(default_factory=list)
    default_label: Optional[str] = None


def classify_entries(
    entries: List[LogEntry],
    options: ClassifyOptions,
) -> List[ClassifiedEntry]:
    sorted_rules = sorted(options.rules, key=lambda r: -r.priority)
    result: List[ClassifiedEntry] = []
    for entry in entries:
        matched = [r.label for r in sorted_rules if r.matches(entry)]
        if not matched and options.default_label:
            matched = [options.default_label]
        result.append(ClassifiedEntry(entry=entry, labels=matched))
    return result


def group_by_label(
    classified: List[ClassifiedEntry],
) -> Dict[str, List[ClassifiedEntry]]:
    groups: Dict[str, List[ClassifiedEntry]] = {}
    for ce in classified:
        for label in ce.labels:
            groups.setdefault(label, []).append(ce)
        if not ce.labels:
            groups.setdefault("__unclassified__", []).append(ce)
    return groups
