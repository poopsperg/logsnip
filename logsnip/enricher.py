from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from logsnip.parser import LogEntry


@dataclass
class EnrichRule:
    field: str  # 'level', 'message', or 'extra_*'
    pattern: str
    extract_as: str  # key name to store extracted group
    group: int = 1

    def __post_init__(self) -> None:
        if not self.pattern:
            raise ValueError("pattern must not be empty")
        if not self.extract_as:
            raise ValueError("extract_as must not be empty")
        self._re = re.compile(self.pattern)

    def apply(self, entry: LogEntry) -> Optional[str]:
        text = entry.level if self.field == "level" else entry.message
        m = self._re.search(text)
        if m:
            try:
                return m.group(self.group)
            except IndexError:
                return None
        return None


@dataclass
class EnrichedEntry:
    entry: LogEntry
    extras: dict = field(default_factory=dict)

    @property
    def timestamp(self):
        return self.entry.timestamp

    @property
    def level(self):
        return self.entry.level

    @property
    def message(self):
        return self.entry.message


@dataclass
class EnrichOptions:
    rules: List[EnrichRule] = field(default_factory=list)
    skip_empty: bool = True


def enrich_entry(entry: LogEntry, rules: List[EnrichRule], skip_empty: bool = True) -> EnrichedEntry:
    extras: dict = {}
    for rule in rules:
        value = rule.apply(entry)
        if value is not None or not skip_empty:
            extras[rule.extract_as] = value
    return EnrichedEntry(entry=entry, extras=extras)


def enrich_entries(
    entries: Iterable[LogEntry],
    options: EnrichOptions,
) -> List[EnrichedEntry]:
    return [
        enrich_entry(e, options.rules, options.skip_empty)
        for e in entries
    ]


def enrich_summary(enriched: List[EnrichedEntry]) -> str:
    total = len(enriched)
    with_extras = sum(1 for e in enriched if e.extras)
    keys: set = set()
    for e in enriched:
        keys.update(e.extras.keys())
    return (
        f"Enriched {total} entries, "
        f"{with_extras} with extracted data, "
        f"fields: {sorted(keys) if keys else []}"
    )
