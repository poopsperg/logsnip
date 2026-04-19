import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.splitter import Segment, SplitOptions, split_entries, split_summary


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="INFO", message="startup complete", line_number=1),
        LogEntry(timestamp=_ts(1), level="INFO", message="processing batch", line_number=2),
        LogEntry(timestamp=_ts(2), level="ERROR", message="--- MARKER ---", line_number=3),
        LogEntry(timestamp=_ts(3), level="INFO", message="recovery started", line_number=4),
        LogEntry(timestamp=_ts(4), level="WARN", message="slow query", line_number=5),
        LogEntry(timestamp=_ts(5), level="ERROR", message="--- MARKER ---", line_number=6),
        LogEntry(timestamp=_ts(6), level="INFO", message="done", line_number=7),
    ]


def test_split_creates_segments(sample_entries):
    opts = SplitOptions(markers=[r"--- MARKER ---"])
    segments = split_entries(sample_entries, opts)
    assert len(segments) == 3


def test_split_first_segment_entries(sample_entries):
    opts = SplitOptions(markers=[r"--- MARKER ---"])
    segments = split_entries(sample_entries, opts)
    assert segments[0].size == 2


def test_split_marker_line_included(sample_entries):
    opts = SplitOptions(markers=[r"--- MARKER ---"], include_marker_line=True)
    segments = split_entries(sample_entries, opts)
    assert any(e.message == "--- MARKER ---" for e in segments[1].entries)


def test_split_marker_line_excluded(sample_entries):
    opts = SplitOptions(markers=[r"--- MARKER ---"], include_marker_line=False)
    segments = split_entries(sample_entries, opts)
    for seg in segments:
        assert all("MARKER" not in e.message for e in seg.entries)


def test_split_no_markers(sample_entries):
    opts = SplitOptions(markers=[])
    segments = split_entries(sample_entries, opts)
    assert len(segments) == 1
    assert segments[0].size == len(sample_entries)


def test_split_segment_names(sample_entries):
    opts = SplitOptions(markers=[r"--- MARKER ---"])
    segments = split_entries(sample_entries, opts)
    assert segments[0].name == "default"
    assert segments[1].name == "segment_2"


def test_split_summary_keys(sample_entries):
    opts = SplitOptions(markers=[r"--- MARKER ---"])
    segments = split_entries(sample_entries, opts)
    summary = split_summary(segments)
    assert "total_segments" in summary
    assert "total_entries" in summary
    assert summary["total_segments"] == 3
    assert summary["total_entries"] == len(sample_entries)
