from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.filter import apply_filters


@dataclass
class Snapshot:
    taken_at: datetime
    label: str
    entries: List[LogEntry]

    @property
    def count(self) -> int:
        return len(self.entries)

    @property
    def start(self) -> Optional[datetime]:
        return self.entries[0].timestamp if self.entries else None

    @property
    def end(self) -> Optional[datetime]:
        return self.entries[-1].timestamp if self.entries else None


@dataclass
class SnapshotOptions:
    label: str = "snapshot"
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None


def take_snapshot(entries: List[LogEntry], options: SnapshotOptions) -> Snapshot:
    filtered = apply_filters(
        entries,
        level=options.level,
        pattern=options.pattern,
        exclude=options.exclude,
    )
    return Snapshot(
        taken_at=datetime.utcnow(),
        label=options.label,
        entries=list(filtered),
    )


def compare_snapshots(a: Snapshot, b: Snapshot) -> dict:
    keys_a = {e.message for e in a.entries}
    keys_b = {e.message for e in b.entries}
    return {
        "label_a": a.label,
        "label_b": b.label,
        "count_a": a.count,
        "count_b": b.count,
        "only_in_a": len(keys_a - keys_b),
        "only_in_b": len(keys_b - keys_a),
        "common": len(keys_a & keys_b),
    }


def format_snapshot(snapshot: Snapshot) -> str:
    lines = [
        f"Snapshot : {snapshot.label}",
        f"Taken at : {snapshot.taken_at.isoformat()}",
        f"Entries  : {snapshot.count}",
        f"From     : {snapshot.start}",
        f"To       : {snapshot.end}",
    ]
    return "\n".join(lines)
