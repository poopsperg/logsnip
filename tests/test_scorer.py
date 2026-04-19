import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.scorer import (
    ScoreOptions,
    score_entry,
    score_entries,
    top_entries,
)


def _ts(minute: int = 0):
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="ERROR", message="disk failure detected", line=1),
        LogEntry(timestamp=_ts(1), level="INFO", message="service started", line=2),
        LogEntry(timestamp=_ts(2), level="WARNING", message="high memory usage", line=3),
        LogEntry(timestamp=_ts(3), level="DEBUG", message="debug trace", line=4),
        LogEntry(timestamp=_ts(4), level="CRITICAL", message="system crash failure", line=5),
    ]


def test_score_entry_level_weight(sample_entries):
    opts = ScoreOptions()
    scored = score_entry(sample_entries[0], opts)  # ERROR
    assert scored.score == 4


def test_score_entry_keyword_adds_weight(sample_entries):
    opts = ScoreOptions(keywords=["failure"], keyword_weight=3)
    scored = score_entry(sample_entries[0], opts)  # ERROR + "failure"
    assert scored.score == 4 + 3


def test_score_entry_multiple_keywords(sample_entries):
    opts = ScoreOptions(keywords=["failure", "disk"], keyword_weight=2)
    scored = score_entry(sample_entries[0], opts)
    assert scored.score == 4 + 2 + 2


def test_score_entry_reasons_populated(sample_entries):
    opts = ScoreOptions(keywords=["failure"])
    scored = score_entry(sample_entries[0], opts)
    assert any("level" in r for r in scored.reasons)
    assert any("keyword" in r for r in scored.reasons)


def test_score_entries_count(sample_entries):
    result = score_entries(sample_entries)
    assert len(result) == len(sample_entries)


def test_score_entries_debug_zero(sample_entries):
    result = score_entries(sample_entries)
    debug_scored = next(s for s in result if s.level == "DEBUG")
    assert debug_scored.score == 0


def test_top_entries_limits(sample_entries):
    scored = score_entries(sample_entries)
    top = top_entries(scored, n=2)
    assert len(top) == 2


def test_top_entries_ordered(sample_entries):
    scored = score_entries(sample_entries)
    top = top_entries(scored, n=3)
    assert top[0].score >= top[1].score >= top[2].score
