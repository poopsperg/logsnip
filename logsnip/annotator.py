"""Annotate log entries with tags or notes based on patterns."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import re

from logsnip.parser import LogEntry


@dataclass
class AnnotationRule:
    tag: str
    pattern: str
    note: Optional[str] = None
    _compiled: re.Pattern = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._compiled = re.compile(self.pattern, re.IGNORECASE)

    def matches(self, entry: LogEntry) -> bool:
        return bool(self._compiled.search(entry.message))


@dataclass
class AnnotatedEntry:
    entry: LogEntry
    tags: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


def annotate_entries(
    entries: List[LogEntry],
    rules: List[AnnotationRule],
) -> List[AnnotatedEntry]:
    result = []
    for entry in entries:
        tags = []
        notes = []
        for rule in rules:
            if rule.matches(entry):
                tags.append(rule.tag)
                if rule.note:
                    notes.append(rule.note)
        result.append(AnnotatedEntry(entry=entry, tags=tags, notes=notes))
    return result


def filter_by_tag(
    annotated: List[AnnotatedEntry],
    tag: str,
) -> List[AnnotatedEntry]:
    return [a for a in annotated if a.has_tag(tag)]


def format_annotated(annotated: List[AnnotatedEntry]) -> str:
    lines = []
    for a in annotated:
        tag_str = ",".join(a.tags) if a.tags else "-"
        note_str = "; ".join(a.notes) if a.notes else ""
        line = f"[{tag_str}] {a.entry.timestamp} {a.entry.level} {a.entry.message}"
        if note_str:
            line += f"  # {note_str}"
        lines.append(line)
    return "\n".join(lines)
