import pytest
from datetime import datetime
from logsnip.parser import LogEntry
from logsnip.summarizer import SummaryOptions, summarize_entries, format_summary


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(line_number=1, timestamp=_ts(0), level="INFO", message="started"),
        LogEntry(line_number=2, timestamp=_ts(1), level="INFO", message="running"),
        LogEntry(line_number=3, timestamp=_ts(2), level="ERROR", message="failed badly"),
        LogEntry(line_number=4, timestamp=_ts(3), level="WARN", message="slow response"),
        LogEntry(line_number=5, timestamp=_ts(4), level="ERROR", message="failed badly"),
        LogEntry(line_number=6, timestamp=_ts(5), level="INFO", message="started"),
    ]


def test_summary_total(sample_entries):
    report = summarize_entries(sample_entries)
    assert report.total == 6


def test_summary_level_counts(sample_entries):
    report = summarize_entries(sample_entries)
    assert report.level_counts["INFO"] == 3
    assert report.level_counts["ERROR"] == 2
    assert report.level_counts["WARN"] == 1


def test_summary_unique_messages(sample_entries):
    report = summarize_entries(sample_entries)
    assert report.unique_messages == 4


def test_summary_top_messages(sample_entries):
    report = summarize_entries(sample_entries)
    top_msgs = [m for m, _ in report.top_messages]
    assert "failed badly" in top_msgs
    assert "started" in top_msgs


def test_summary_timestamps(sample_entries):
    report = summarize_entries(sample_entries)
    assert report.first_ts is not None
    assert report.last_ts is not None
    assert report.first_ts <= report.last_ts


def test_summary_filter_level(sample_entries):
    opts = SummaryOptions(level_filter="ERROR")
    report = summarize_entries(sample_entries, opts)
    assert report.total == 2
    assert set(report.level_counts.keys()) == {"ERROR"}


def test_summary_filter_pattern(sample_entries):
    opts = SummaryOptions(pattern="fail")
    report = summarize_entries(sample_entries, opts)
    assert report.total == 2


def test_summary_empty_result(sample_entries):
    opts = SummaryOptions(pattern="nonexistent_xyz")
    report = summarize_entries(sample_entries, opts)
    assert report.total == 0
    assert report.first_ts is None


def test_format_summary_contains_total(sample_entries):
    report = summarize_entries(sample_entries)
    text = format_summary(report)
    assert "6" in text
    assert "Total" in text


def test_format_summary_contains_levels(sample_entries):
    report = summarize_entries(sample_entries)
    text = format_summary(report)
    assert "ERROR" in text
    assert "INFO" in text
