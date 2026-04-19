import pytest
from datetime import datetime
from logsnip.parser import LogEntry
from logsnip.archive_pipeline import ArchivePipelineOptions, run_archive_pipeline, archive_to_bytes


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="INFO", message="boot complete", line_number=1),
        LogEntry(timestamp=_ts(1), level="DEBUG", message="checking config", line_number=2),
        LogEntry(timestamp=_ts(2), level="ERROR", message="disk full", line_number=3),
        LogEntry(timestamp=_ts(3), level="INFO", message="retry ok", line_number=4),
    ]


def test_run_pipeline_returns_all(sample_entries):
    opts = ArchivePipelineOptions()
    arch = run_archive_pipeline(sample_entries, opts)
    assert arch.count == 4


def test_run_pipeline_filter_level(sample_entries):
    opts = ArchivePipelineOptions(level="INFO")
    arch = run_archive_pipeline(sample_entries, opts)
    assert arch.count == 2
    assert all(e.level == "INFO" for e in arch.entries)


def test_run_pipeline_filter_pattern(sample_entries):
    opts = ArchivePipelineOptions(pattern="disk")
    arch = run_archive_pipeline(sample_entries, opts)
    assert arch.count == 1
    assert arch.entries[0].message == "disk full"


def test_run_pipeline_exclude(sample_entries):
    opts = ArchivePipelineOptions(exclude="retry")
    arch = run_archive_pipeline(sample_entries, opts)
    assert all("retry" not in e.message for e in arch.entries)


def test_run_pipeline_label(sample_entries):
    opts = ArchivePipelineOptions(label="prod-2024")
    arch = run_archive_pipeline(sample_entries, opts)
    assert arch.label == "prod-2024"


def test_archive_to_bytes_compressed(sample_entries):
    opts = ArchivePipelineOptions(compress=True)
    arch = run_archive_pipeline(sample_entries, opts)
    data = archive_to_bytes(arch)
    assert isinstance(data, bytes)
    assert len(data) > 0
