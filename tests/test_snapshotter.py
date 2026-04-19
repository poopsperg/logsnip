from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.snapshotter import (
    Snapshot,
    SnapshotOptions,
    take_snapshot,
    compare_snapshots,
    format_snapshot,
)


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


sample_entries = [
    LogEntry(timestamp=_ts(0), level="INFO", message="service started", line=1),
    LogEntry(timestamp=_ts(1), level="WARN", message="high memory", line=2),
    LogEntry(timestamp=_ts(2), level="ERROR", message="disk full", line=3),
    LogEntry(timestamp=_ts(3), level="INFO", message="service stopped", line=4),
]


def test_take_snapshot_count():
    snap = take_snapshot(sample_entries, SnapshotOptions(label="all"))
    assert snap.count == 4


def test_take_snapshot_label():
    snap = take_snapshot(sample_entries, SnapshotOptions(label="test"))
    assert snap.label == "test"


def test_take_snapshot_filter_level():
    snap = take_snapshot(sample_entries, SnapshotOptions(label="info", level="INFO"))
    assert snap.count == 2
    assert all(e.level == "INFO" for e in snap.entries)


def test_take_snapshot_filter_pattern():
    snap = take_snapshot(sample_entries, SnapshotOptions(label="disk", pattern="disk"))
    assert snap.count == 1
    assert "disk" in snap.entries[0].message


def test_take_snapshot_exclude():
    snap = take_snapshot(sample_entries, SnapshotOptions(label="no-info", exclude="INFO"))
    assert all(e.level != "INFO" for e in snap.entries)


def test_snapshot_start_end():
    snap = take_snapshot(sample_entries, SnapshotOptions())
    assert snap.start == _ts(0)
    assert snap.end == _ts(3)


def test_snapshot_empty():
    snap = take_snapshot([], SnapshotOptions(label="empty"))
    assert snap.count == 0
    assert snap.start is None
    assert snap.end is None


def test_compare_snapshots_common():
    a = take_snapshot(sample_entries, SnapshotOptions(label="a"))
    b = take_snapshot(sample_entries[:2], SnapshotOptions(label="b"))
    diff = compare_snapshots(a, b)
    assert diff["common"] == 2
    assert diff["only_in_a"] == 2
    assert diff["only_in_b"] == 0


def test_format_snapshot_contains_label():
    snap = take_snapshot(sample_entries, SnapshotOptions(label="mylabel"))
    text = format_snapshot(snap)
    assert "mylabel" in text
    assert "Entries" in text
