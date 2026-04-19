import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.transformer import TransformOptions, transform_entry, transform_entries


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(_ts(0), "info", "hello world", "raw", 1, {"req_id": "abc"}),
        LogEntry(_ts(1), "warn", "something happened", "raw", 2, {"user": "bob"}),
        LogEntry(_ts(2), "error", "a" * 80, "raw", 3, {}),
    ]


def test_uppercase_level(sample_entries):
    opts = TransformOptions(uppercase_level=True)
    result = transform_entries(sample_entries, opts)
    assert result[0].level == "INFO"
    assert result[1].level == "WARN"


def test_truncate_message(sample_entries):
    opts = TransformOptions(truncate_message=10)
    result = transform_entries(sample_entries, opts)
    assert result[0].message == "hello worl..."
    assert len(result[2].message) == 13  # 10 + "..."


def test_add_prefix(sample_entries):
    opts = TransformOptions(add_prefix="[APP] ")
    result = transform_entries(sample_entries, opts)
    assert result[0].message.startswith("[APP] ")


def test_strip_fields(sample_entries):
    opts = TransformOptions(strip_fields=["req_id"])
    result = transform_entries(sample_entries, opts)
    assert "req_id" not in result[0].extra
    assert "user" in result[1].extra


def test_custom_transform(sample_entries):
    def shout(entry):
        return LogEntry(
            entry.timestamp, entry.level,
            entry.message.upper(), entry.raw, entry.line_number, entry.extra
        )
    opts = TransformOptions(custom=shout)
    result = transform_entries(sample_entries, opts)
    assert result[0].message == "HELLO WORLD"


def test_no_transform_preserves_entry(sample_entries):
    opts = TransformOptions()
    result = transform_entries(sample_entries, opts)
    assert result[0].message == sample_entries[0].message
    assert result[0].level == sample_entries[0].level


def test_transform_entries_count(sample_entries):
    opts = TransformOptions(uppercase_level=True)
    result = transform_entries(sample_entries, opts)
    assert len(result) == len(sample_entries)
