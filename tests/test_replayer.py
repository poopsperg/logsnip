"""Tests for logsnip.replayer."""
import pytest
from datetime import datetime, timezone, timedelta

from logsnip.parser import LogEntry
from logsnip.replayer import ReplayOptions, ReplayEvent, replay_entries, replay_summary


def _ts(offset_seconds: int) -> datetime:
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    return base + timedelta(seconds=offset_seconds)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0),  level="INFO",  message="start",   line_number=1),
        LogEntry(timestamp=_ts(2),  level="DEBUG", message="working",  line_number=2),
        LogEntry(timestamp=_ts(5),  level="WARN",  message="slow",     line_number=3),
        LogEntry(timestamp=_ts(6),  level="ERROR", message="oops",     line_number=4),
    ]


def test_replay_yields_all_entries(sample_entries):
    opts = ReplayOptions(real_time=False)
    events = list(replay_entries(sample_entries, opts))
    assert len(events) == 4


def test_replay_first_delay_is_zero(sample_entries):
    opts = ReplayOptions(real_time=False)
    events = list(replay_entries(sample_entries, opts))
    assert events[0].delay == 0.0


def test_replay_delays_match_timestamps(sample_entries):
    opts = ReplayOptions(speed=1.0, real_time=False)
    events = list(replay_entries(sample_entries, opts))
    assert events[1].delay == pytest.approx(2.0)
    assert events[2].delay == pytest.approx(3.0)
    assert events[3].delay == pytest.approx(1.0)


def test_replay_speed_multiplier(sample_entries):
    opts = ReplayOptions(speed=2.0, real_time=False)
    events = list(replay_entries(sample_entries, opts))
    assert events[1].delay == pytest.approx(1.0)
    assert events[2].delay == pytest.approx(1.5)


def test_replay_max_delay_capped(sample_entries):
    opts = ReplayOptions(speed=1.0, max_delay=2.0, real_time=False)
    events = list(replay_entries(sample_entries, opts))
    assert all(e.delay <= 2.0 for e in events)


def test_replay_elapsed_accumulates(sample_entries):
    opts = ReplayOptions(speed=1.0, max_delay=100.0, real_time=False)
    events = list(replay_entries(sample_entries, opts))
    assert events[-1].elapsed == pytest.approx(6.0)


def test_replay_on_event_callback(sample_entries):
    opts = ReplayOptions(real_time=False)
    seen = []
    list(replay_entries(sample_entries, opts, on_event=seen.append))
    assert len(seen) == 4
    assert all(isinstance(e, ReplayEvent) for e in seen)


def test_replay_summary_empty():
    result = replay_summary([])
    assert result["total"] == 0
    assert result["elapsed"] == 0.0


def test_replay_summary_fields(sample_entries):
    opts = ReplayOptions(speed=1.0, real_time=False)
    events = list(replay_entries(sample_entries, opts))
    summary = replay_summary(events)
    assert summary["total"] == 4
    assert summary["elapsed"] == pytest.approx(6.0)
    assert "avg_delay" in summary
    assert "max_delay" in summary
