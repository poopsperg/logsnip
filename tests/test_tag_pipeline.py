import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.tagger import TagRule
from logsnip.tag_pipeline import TagPipelineOptions, run_tag_pipeline, tag_pipeline_summary


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="ERROR", message="disk full", line_number=1),
        LogEntry(timestamp=_ts(1), level="WARN", message="slow query", line_number=2),
        LogEntry(timestamp=_ts(2), level="INFO", message="ready", line_number=3),
    ]


def test_run_pipeline_no_filter(sample_entries):
    rules = [TagRule(tag="err", level="ERROR")]
    opts = TagPipelineOptions(rules=rules)
    result = run_tag_pipeline(sample_entries, opts)
    assert len(result) == 3


def test_run_pipeline_with_filter(sample_entries):
    rules = [TagRule(tag="err", level="ERROR")]
    opts = TagPipelineOptions(rules=rules, filter_tag="err")
    result = run_tag_pipeline(sample_entries, opts)
    assert len(result) == 1
    assert result[0].entry.level == "ERROR"


def test_run_pipeline_no_rules(sample_entries):
    opts = TagPipelineOptions()
    result = run_tag_pipeline(sample_entries, opts)
    assert all(t.tags == [] for t in result)


def test_summary_with_tags(sample_entries):
    rules = [TagRule(tag="err", level="ERROR"), TagRule(tag="warn", level="WARN")]
    opts = TagPipelineOptions(rules=rules)
    tagged = run_tag_pipeline(sample_entries, opts)
    summary = tag_pipeline_summary(tagged)
    assert "err" in summary
    assert "warn" in summary


def test_summary_empty():
    summary = tag_pipeline_summary([])
    assert summary == "no tags applied"
