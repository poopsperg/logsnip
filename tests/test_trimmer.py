import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.trimmer import TrimOptions, trim_head, trim_tail, trim_entries, trim_summary


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 0, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(line_number=i, timestamp=_ts(i), level="INFO", message=f"msg {i}")
        for i in range(6)
    ]


def test_trim_head_basic(sample_entries):
    result = trim_head(sample_entries, 3)
    assert len(result) == 3
    assert result[0].message == "msg 0"


def test_trim_head_zero(sample_entries):
    assert trim_head(sample_entries, 0) == []


def test_trim_head_invalid(sample_entries):
    with pytest.raises(ValueError):
        trim_head(sample_entries, -1)


def test_trim_tail_basic(sample_entries):
    result = trim_tail(sample_entries, 2)
    assert len(result) == 2
    assert result[-1].message == "msg 5"


def test_trim_tail_zero(sample_entries):
    assert trim_tail(sample_entries, 0) == []


def test_trim_tail_invalid(sample_entries):
    with pytest.raises(ValueError):
        trim_tail(sample_entries, -1)


def test_trim_entries_head_only(sample_entries):
    result = trim_entries(sample_entries, TrimOptions(head=4))
    assert len(result) == 4


def test_trim_entries_tail_only(sample_entries):
    result = trim_entries(sample_entries, TrimOptions(tail=2))
    assert len(result) == 2
    assert result[0].message == "msg 4"


def test_trim_entries_drop_duplicates():
    entries = [
        LogEntry(line_number=1, timestamp=_ts(0), level="INFO", message="dup"),
        LogEntry(line_number=2, timestamp=_ts(1), level="INFO", message="dup"),
        LogEntry(line_number=3, timestamp=_ts(2), level="ERROR", message="unique"),
    ]
    result = trim_entries(entries, TrimOptions(drop_duplicates=True))
    assert len(result) == 2
    assert result[0].message == "dup"
    assert result[1].message == "unique"


def test_trim_summary(sample_entries):
    trimmed = sample_entries[:3]
    summary = trim_summary(sample_entries, trimmed)
    assert summary["original_count"] == 6
    assert summary["trimmed_count"] == 3
    assert summary["removed"] == 3
