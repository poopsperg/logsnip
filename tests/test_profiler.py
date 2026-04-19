import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.profiler import profile_entries, format_profile, ProfileReport


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(line_number=1, timestamp=_ts(0), level="INFO", message="app started"),
        LogEntry(line_number=2, timestamp=_ts(1), level="DEBUG", message="app debug msg"),
        LogEntry(line_number=3, timestamp=_ts(2), level="ERROR", message="app crashed"),
        LogEntry(line_number=4, timestamp=_ts(3), level="INFO", message="app recovered"),
        LogEntry(line_number=5, timestamp=_ts(4), level="WARN", message="app slow"),
    ]


def test_profile_total(sample_entries):
    report = profile_entries(sample_entries)
    assert report.total == 5


def test_profile_level_counts(sample_entries):
    report = profile_entries(sample_entries)
    assert report.level_counts["INFO"] == 2
    assert report.level_counts["ERROR"] == 1
    assert report.level_counts["DEBUG"] == 1


def test_profile_timestamps(sample_entries):
    report = profile_entries(sample_entries)
    assert report.first_ts == _ts(0)
    assert report.last_ts == _ts(4)


def test_profile_duration(sample_entries):
    report = profile_entries(sample_entries)
    assert report.duration_seconds == 240.0


def test_profile_empty():
    report = profile_entries([])
    assert report.total == 0
    assert report.first_ts is None
    assert report.messages_per_minute == 0.0


def test_profile_mpm(sample_entries):
    report = profile_entries(sample_entries)
    assert report.messages_per_minute > 0


def test_format_profile_contains_total(sample_entries):
    report = profile_entries(sample_entries)
    text = format_profile(report)
    assert "5" in text


def test_format_profile_contains_levels(sample_entries):
    report = profile_entries(sample_entries)
    text = format_profile(report)
    assert "INFO" in text
    assert "ERROR" in text
