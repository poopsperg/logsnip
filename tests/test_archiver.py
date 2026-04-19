import pytest
from datetime import datetime
from logsnip.parser import LogEntry
from logsnip.archiver import (
    ArchiveOptions,
    create_archive,
    serialize_archive,
    deserialize_archive,
    archive_summary,
)


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="INFO", message="start", line_number=1),
        LogEntry(timestamp=_ts(1), level="WARN", message="slow query", line_number=2),
        LogEntry(timestamp=_ts(2), level="ERROR", message="failed", line_number=3),
    ]


def test_create_archive_count(sample_entries):
    opts = ArchiveOptions(label="test")
    arch = create_archive(sample_entries, opts)
    assert arch.count == 3


def test_create_archive_label(sample_entries):
    opts = ArchiveOptions(label="my-archive")
    arch = create_archive(sample_entries, opts)
    assert arch.label == "my-archive"


def test_create_archive_default_label(sample_entries):
    opts = ArchiveOptions()
    arch = create_archive(sample_entries, opts)
    assert arch.label == "archive"


def test_archive_start_end(sample_entries):
    opts = ArchiveOptions()
    arch = create_archive(sample_entries, opts)
    assert arch.start == _ts(0)
    assert arch.end == _ts(2)


def test_serialize_deserialize_compressed(sample_entries):
    opts = ArchiveOptions(compress=True, label="roundtrip")
    arch = create_archive(sample_entries, opts)
    data = serialize_archive(arch)
    assert isinstance(data, bytes)
    restored = deserialize_archive(data, compressed=True)
    assert restored.count == 3
    assert restored.label == "roundtrip"
    assert restored.entries[1].level == "WARN"


def test_serialize_deserialize_uncompressed(sample_entries):
    opts = ArchiveOptions(compress=False, label="plain")
    arch = create_archive(sample_entries, opts)
    data = serialize_archive(arch)
    restored = deserialize_archive(data, compressed=False)
    assert restored.count == 3
    assert restored.entries[2].message == "failed"


def test_archive_summary_contains_label(sample_entries):
    opts = ArchiveOptions(label="summary-test")
    arch = create_archive(sample_entries, opts)
    s = archive_summary(arch)
    assert "summary-test" in s
    assert "3" in s


def test_empty_archive_start_end():
    opts = ArchiveOptions()
    arch = create_archive([], opts)
    assert arch.start is None
    assert arch.end is None
