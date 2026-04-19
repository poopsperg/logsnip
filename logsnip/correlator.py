from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from logsnip.parser import LogEntry


@dataclass
class CorrelationGroup:
    key: str
    entries: List[LogEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)

    @property
    def levels(self) -> List[str]:
        return [e.level for e in self.entries]

    @property
    def start(self) -> Optional[object]:
        return self.entries[0].timestamp if self.entries else None

    @property
    def end(self) -> Optional[object]:
        return self.entries[-1].timestamp if self.entries else None


@dataclass
class CorrelateOptions:
    pattern: str
    context_lines: int = 2
    max_gap_seconds: Optional[float] = None


def correlate_entries(
    entries: List[LogEntry], pattern: str
) -> List[CorrelationGroup]:
    """Group entries that share a common pattern match into correlation groups."""
    import re
    groups: Dict[str, CorrelationGroup] = {}
    for entry in entries:
        m = re.search(pattern, entry.message)
        if m:
            key = m.group(0)
            if key not in groups:
                groups[key] = CorrelationGroup(key=key)
            groups[key].entries.append(entry)
    return list(groups.values())


def correlate_by_field(
    entries: List[LogEntry], field_pattern: str
) -> List[CorrelationGroup]:
    """Correlate entries by extracted field value (e.g. request IDs)."""
    return correlate_entries(entries, field_pattern)


def format_correlation(groups: List[CorrelationGroup]) -> str:
    lines = []
    for g in groups:
        lines.append(f"[{g.key}] {g.count} entries  {g.start} -> {g.end}")
        for e in g.entries:
            lines.append(f"  {e.level:8s} {e.message}")
    return "\n".join(lines)
