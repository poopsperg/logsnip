"""Tests for logsnip.masker and logsnip.mask_pipeline."""
from datetime import datetime, timezone
import pytest

from logsnip.parser import LogEntry
from logsnip.masker import (
    MaskRule,
    MaskOptions,
    mask_entry,
    mask_entries,
    mask_summary,
)
from logsnip.mask_pipeline import MaskPipelineOptions, run_mask_pipeline


def _ts(h: int, m: int = 0) -> datetime:
    return datetime(2024, 1, 1, h, m, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(10), level="INFO", message="user=alice logged in"),
        LogEntry(timestamp=_ts(10, 1), level="ERROR", message="token=abc123 expired"),
        LogEntry(timestamp=_ts(10, 2), level="DEBUG", message="no sensitive data here"),
        LogEntry(timestamp=_ts(10, 3), level="WARN", message="ip=192.168.1.1 blocked"),
    ]


def test_mask_rule_invalid_empty_pattern():
    with pytest.raises(ValueError):
        MaskRule(pattern="")


def test_mask_rule_invalid_field():
    with pytest.raises(ValueError):
        MaskRule(pattern=r"x", field="body")


def test_mask_rule_applies_replacement():
    rule = MaskRule(pattern=r"user=\w+", replacement="user=***")
    assert rule.apply("user=alice logged in") == "user=*** logged in"


def test_mask_entry_masks_message(sample_entries):
    rule = MaskRule(pattern=r"user=\w+")
    result = mask_entry(sample_entries[0], [rule])
    assert "***" in result.message
    assert result.masked is True
    assert result.original_message == "user=alice logged in"


def test_mask_entry_no_match_not_masked(sample_entries):
    rule = MaskRule(pattern=r"token=\w+")
    result = mask_entry(sample_entries[0], [rule])
    assert result.masked is False
    assert result.message == sample_entries[0].message


def test_mask_entries_count(sample_entries):
    opts = MaskOptions(rules=[MaskRule(pattern=r"\d+")])
    results = mask_entries(sample_entries, opts)
    assert len(results) == 4


def test_mask_entries_level_filter(sample_entries):
    opts = MaskOptions(
        rules=[MaskRule(pattern=r"\w+")],
        level_filter="ERROR",
    )
    results = mask_entries(sample_entries, opts)
    assert len(results) == 1
    assert results[0].level == "ERROR"


def test_mask_entries_pattern_filter(sample_entries):
    opts = MaskOptions(
        rules=[MaskRule(pattern=r"ip=\S+")],
        pattern_filter=r"ip=",
    )
    results = mask_entries(sample_entries, opts)
    assert len(results) == 1
    assert results[0].masked is True


def test_mask_summary(sample_entries):
    opts = MaskOptions(rules=[MaskRule(pattern=r"\d+")])
    results = mask_entries(sample_entries, opts)
    summary = mask_summary(results)
    assert "total=4" in summary
    assert "masked=" in summary


def test_run_pipeline_only_masked(sample_entries):
    opts = MaskPipelineOptions(
        rules=[MaskRule(pattern=r"token=\w+")],
        only_masked=True,
    )
    results = run_mask_pipeline(sample_entries, opts)
    assert all(r.masked for r in results)
    assert len(results) == 1


def test_run_pipeline_returns_all_when_not_filtered(sample_entries):
    opts = MaskPipelineOptions(rules=[MaskRule(pattern=r"\d+")])
    results = run_mask_pipeline(sample_entries, opts)
    assert len(results) == 4
