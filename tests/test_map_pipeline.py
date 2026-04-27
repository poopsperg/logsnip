import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.mapper import MapRule
from logsnip.map_pipeline import MapPipelineOptions, run_map_pipeline, pipeline_summary


def _ts(minute: int = 0) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(_ts(0), "INFO", "app booted", "INFO app booted", 1),
        LogEntry(_ts(1), "WARN", "memory pressure", "WARN memory pressure", 2),
        LogEntry(_ts(2), "ERROR", "null pointer", "ERROR null pointer", 3),
        LogEntry(_ts(3), "INFO", "request received", "INFO request received", 4),
    ]


def test_run_pipeline_returns_same_count(sample_entries):
    opts = MapPipelineOptions(rules=[])
    result = run_map_pipeline(sample_entries, opts)
    assert len(result) == len(sample_entries)


def test_run_pipeline_applies_rule(sample_entries):
    rule = MapRule(field="message", pattern=r"null pointer", replacement="NPE")
    opts = MapPipelineOptions(rules=[rule])
    result = run_map_pipeline(sample_entries, opts)
    assert result[2].message == "NPE"


def test_run_pipeline_filter_level(sample_entries):
    rule = MapRule(field="message", pattern=r".*", replacement="suppressed")
    opts = MapPipelineOptions(rules=[rule], level_filter="WARN")
    result = run_map_pipeline(sample_entries, opts)
    assert result[1].message == "suppressed"
    assert result[0].message == "app booted"  # not WARN, untouched
    assert result[2].message == "null pointer"  # not WARN, untouched


def test_run_pipeline_filter_pattern(sample_entries):
    rule = MapRule(field="message", pattern=r"received", replacement="handled")
    opts = MapPipelineOptions(rules=[rule], pattern_filter=r"request")
    result = run_map_pipeline(sample_entries, opts)
    assert result[3].message == "handled"
    assert result[0].message == "app booted"


def test_pipeline_summary_output(sample_entries):
    rule = MapRule(field="message", pattern=r"booted", replacement="started")
    opts = MapPipelineOptions(rules=[rule])
    result = run_map_pipeline(sample_entries, opts)
    summary = pipeline_summary(sample_entries, result)
    assert "modified" in summary
    assert "4" in summary
