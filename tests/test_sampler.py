"""Tests for logsnip.sampler."""
from datetime import datetime, timezone
import pytest

from logsnip.parser import LogEntry
from logsnip.sampler import (
    SampleOptions,
    apply_sampling,
    sample_by_rate,
    sample_every_nth,
    sample_head,
)


def _ts(h: int, m: int = 0) -> datetime:
    return datetime(2024, 1, 1, h, m, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries() -> list:
    levels = ["INFO", "DEBUG", "WARNING", "ERROR", "INFO", "DEBUG"]
    return [
        LogEntry(timestamp=_ts(i), level=levels[i], message=f"msg {i}", line_number=i + 1)
        for i in range(6)
    ]


def test_sample_every_nth_basic(sample_entries):
    result = sample_every_nth(sample_entries, 2)
    assert len(result) == 3
    assert result[0].message == "msg 0"
    assert result[1].message == "msg 2"


def test_sample_every_nth_one(sample_entries):
    result = sample_every_nth(sample_entries, 1)
    assert result == sample_entries


def test_sample_every_nth_invalid(sample_entries):
    with pytest.raises(ValueError):
        sample_every_nth(sample_entries, 0)


def test_sample_head_basic(sample_entries):
    result = sample_head(sample_entries, 3)
    assert len(result) == 3
    assert result[-1].message == "msg 2"


def test_sample_head_zero(sample_entries):
    assert sample_head(sample_entries, 0) == []


def test_sample_head_negative(sample_entries):
    with pytest.raises(ValueError):
        sample_head(sample_entries, -1)


def test_sample_by_rate_full(sample_entries):
    result = sample_by_rate(sample_entries, 1.0)
    assert result == sample_entries


def test_sample_by_rate_half(sample_entries):
    result = sample_by_rate(sample_entries, 0.5)
    assert 2 <= len(result) <= 4


def test_sample_by_rate_invalid(sample_entries):
    with pytest.raises(ValueError):
        sample_by_rate(sample_entries, 0.0)
    with pytest.raises(ValueError):
        sample_by_rate(sample_entries, 1.5)


def test_apply_sampling_max_entries(sample_entries):
    opts = SampleOptions(max_entries=2)
    result = apply_sampling(sample_entries, opts)
    assert len(result) == 2


def test_apply_sampling_every_nth_then_max(sample_entries):
    opts = SampleOptions(every_nth=2, max_entries=1)
    result = apply_sampling(sample_entries, opts)
    assert len(result) == 1
    assert result[0].message == "msg 0"


def test_apply_sampling_defaults(sample_entries):
    opts = SampleOptions()
    result = apply_sampling(sample_entries, opts)
    assert result == sample_entries
