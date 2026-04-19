from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from logsnip.parser import LogEntry


@dataclass
class GroupOptions:
    key: str = "level"  # "level" | "minute" | "source"
    min_size: int = 1


@dataclass
class EntryGroup:
    label: str
    entries: List[LogEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)

    @property
    def start(self) -> Optional[str]:
        return self.entries[0].timestamp if self.entries else None

    @property
    def end(self) -> Optional[str]:
        return self.entries[-1].timestamp if self.entries else None


def _group_key(entry: LogEntry, key: str) -> str:
    if key == "level":
        return (entry.level or "UNKNOWN").upper()
    if key == "minute":
        ts = entry.timestamp or ""
        return ts[:16] if len(ts) >= 16 else ts
    if key == "source":
        return entry.source or "unknown"
    return "default"


def group_entries(
    entries: List[LogEntry],
    options: Optional[GroupOptions] = None,
) -> Dict[str, EntryGroup]:
    opts = options or GroupOptions()
    groups: Dict[str, EntryGroup] = {}
    for entry in entries:
        label = _group_key(entry, opts.key)
        if label not in groups:
            groups[label] = EntryGroup(label=label)
        groups[label].entries.append(entry)
    if opts.min_size > 1:
        groups = {k: v for k, v in groups.items() if v.count >= opts.min_size}
    return groups


def group_summary(groups: Dict[str, EntryGroup]) -> str:
    lines = [f"Groups: {len(groups)}"]
    for label, g in sorted(groups.items()):
        lines.append(f"  {label}: {g.count} entries")
    return "\n".join(lines)
