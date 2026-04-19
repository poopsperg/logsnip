from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import re
from logsnip.parser import LogEntry


@dataclass
class LabelRule:
    label: str
    pattern: Optional[str] = None
    level: Optional[str] = None

    def __post_init__(self):
        if not self.label:
            raise ValueError("label must not be empty")
        if self.pattern is None and self.level is None:
            raise ValueError("at least one of pattern or level must be set")

    def matches(self, entry: LogEntry) -> bool:
        if self.level and entry.level.upper() != self.level.upper():
            return False
        if self.pattern and not re.search(self.pattern, entry.message):
            return False
        return True


@dataclass
class LabeledEntry:
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


def label_entries(
    entries: List[LogEntry], rules: List[LabelRule]
) -> List[LabeledEntry]:
    result = []
    for entry in entries:
        labels = [r.label for r in rules if r.matches(entry)]
        result.append(LabeledEntry(entry=entry, labels=labels))
    return result


def filter_by_label(
    labeled: List[LabeledEntry], label: str
) -> List[LabeledEntry]:
    return [e for e in labeled if e.has_label(label)]
