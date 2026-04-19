from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.snapshotter import Snapshot, SnapshotOptions, take_snapshot, compare_snapshots


@dataclass
class SnapshotPipelineOptions:
    label: str = "snapshot"
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None


def run_snapshot_pipeline(
    entries: List[LogEntry],
    options: SnapshotPipelineOptions,
) -> Snapshot:
    opts = SnapshotOptions(
        label=options.label,
        level=options.level,
        pattern=options.pattern,
        exclude=options.exclude,
    )
    return take_snapshot(entries, opts)


def snapshot_diff_summary(a: Snapshot, b: Snapshot) -> str:
    diff = compare_snapshots(a, b)
    lines = [
        f"Comparing '{diff['label_a']}' vs '{diff['label_b']}'",
        f"  Count     : {diff['count_a']} vs {diff['count_b']}",
        f"  Only in A : {diff['only_in_a']}",
        f"  Only in B : {diff['only_in_b']}",
        f"  Common    : {diff['common']}",
    ]
    return "\n".join(lines)
