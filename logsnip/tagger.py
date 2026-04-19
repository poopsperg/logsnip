from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from logsnip.parser import LogEntry


@dataclass
class TagRule:
    tag: str
    level: Optional[str] = None
    pattern: Optional[str] = None

    def __post_init__(self):
        if not self.tag:
            raise ValueError("tag must not be empty")
        if self.level:
            self.level = self.level.upper()

    def matches(self, entry: LogEntry) -> bool:
        if self.level and entry.level.upper() != self.level:
            return False
        if self.pattern and self.pattern.lower() not in entry.message.lower():
            return False
        return True


@dataclass
class TaggedEntry:
    entry: LogEntry
    tags: List[str] = field(default_factory=list)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


def tag_entries(
    entries: List[LogEntry], rules: List[TagRule]
) -> List[TaggedEntry]:
    result = []
    for entry in entries:
        tags = [r.tag for r in rules if r.matches(entry)]
        result.append(TaggedEntry(entry=entry, tags=tags))
    return result


def filter_by_tag(
    tagged: List[TaggedEntry], tag: str
) -> List[TaggedEntry]:
    return [t for t in tagged if t.has_tag(tag)]


def tag_summary(tagged: List[TaggedEntry]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for t in tagged:
        for tag in t.tags:
            counts[tag] = counts.get(tag, 0) + 1
    return counts
