"""Tests for logsnip.detector."""
from datetime import datetime, timezone
import pytest
from logsnip.parser import LogEntry
from logsnip.detector import AnomalyOptions, detect_anomalies, anomaly_summary


def _ts(second: int) -> datetime:
    return datetime(2024, 1, 1, 12, 0, second, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    repeated = [
        LogEntry(timestamp=_ts(i), level="ERROR", message="disk full", line=i)
        for i in range(5)
    ]
    unique = [
        LogEntry(timestamp=_ts(10 + i), level="INFO", message=f"msg {i}", line=10 + i)
        for i in range(3)
    ]
    return repeated + unique


def test_detect_anomalies_finds_repeated(sample_entries):
    opts = AnomalyOptions(window_seconds=60, min_occurrences=3)
    result = detect_anomalies(sample_entries, opts)
    assert len(result) == 1
    assert result[0].message == "disk full"


def test_detect_anomalies_empty():
    opts = AnomalyOptions(window_seconds=60, min_occurrences=2)
    result = detect_anomalies([], opts)
    assert result == []


def test_detect_anomalies_no_anomalies(sample_entries):
    opts = AnomalyOptions(window_seconds=60, min_occurrences=10)
    result = detect_anomalies(sample_entries, opts)
    assert result == []


def test_detect_anomaly_score(sample_entries):
    opts = AnomalyOptions(window_seconds=60, min_occurrences=5)
    result = detect_anomalies(sample_entries, opts)
    assert len(result) == 1
    assert result[0].score == pytest.approx(1.0)


def test_detect_anomaly_reason_contains_count(sample_entries):
    opts = AnomalyOptions(window_seconds=60, min_occurrences=3)
    result = detect_anomalies(sample_entries, opts)
    assert "5x" in result[0].reason


def test_detect_sorted_by_score_desc():
    entries = (
        [LogEntry(timestamp=_ts(i), level="ERROR", message="alpha", line=i) for i in range(6)]
        + [LogEntry(timestamp=_ts(i + 20), level="WARN", message="beta", line=i + 20) for i in range(3)]
    )
    opts = AnomalyOptions(window_seconds=60, min_occurrences=3)
    result = detect_anomalies(entries, opts)
    assert result[0].score >= result[-1].score


def test_anomaly_summary_keys(sample_entries):
    opts = AnomalyOptions(window_seconds=60, min_occurrences=3)
    anomalies = detect_anomalies(sample_entries, opts)
    s = anomaly_summary(anomalies)
    assert "total" in s
    assert "max_score" in s
    assert "levels" in s


def test_anomaly_summary_empty():
    s = anomaly_summary([])
    assert s["total"] == 0
    assert s["max_score"] == 0.0
