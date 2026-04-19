import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.transform_pipeline import (
    TransformPipelineOptions,
    run_transform_pipeline,
    transform_summary,
)


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(_ts(0), "info", "msg one", "raw", 1, {}),
        LogEntry(_ts(1), "debug", "msg two", "raw", 2, {}),
        LogEntry(_ts(2), "error", "msg three", "raw", 3, {}),
    ]


def test_run_pipeline_returns_same_count(sample_entries):
    opts = TransformPipelineOptions()
    result = run_transform_pipeline(sample_entries, opts)
    assert len(result) == 3


def test_run_pipeline_uppercase(sample_entries):
    opts = TransformPipelineOptions(uppercase_level=True)
    result = run_transform_pipeline(sample_entries, opts)
    assert all(e.level == e.level.upper() for e in result)


def test_run_pipeline_prefix(sample_entries):
    opts = TransformPipelineOptions(add_prefix=">> ")
    result = run_transform_pipeline(sample_entries, opts)
    assert result[0].message.startswith(">> ")


def test_summary_total(sample_entries):
    opts = TransformPipelineOptions(uppercase_level=True)
    transformed = run_transform_pipeline(sample_entries, opts)
    summary = transform_summary(sample_entries, transformed)
    assert summary["total_input"] == 3
    assert summary["total_output"] == 3


def test_summary_changed_count(sample_entries):
    opts = TransformPipelineOptions(add_prefix="X")
    transformed = run_transform_pipeline(sample_entries, opts)
    summary = transform_summary(sample_entries, transformed)
    assert summary["changed"] == 3
