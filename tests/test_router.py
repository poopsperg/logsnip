import pytest
from datetime import datetime, timezone
from logsnip.parser import LogEntry
from logsnip.router import RouteRule, RouterOptions, route_entry, route_entries, group_by_route
from logsnip.route_pipeline import RoutePipelineOptions, run_route_pipeline, route_summary


def _ts(minute: int) -> datetime:
    return datetime(2024, 1, 1, 12, minute, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_entries():
    return [
        LogEntry(timestamp=_ts(0), level="ERROR", message="disk full", line_number=1),
        LogEntry(timestamp=_ts(1), level="WARN", message="high memory", line_number=2),
        LogEntry(timestamp=_ts(2), level="INFO", message="started", line_number=3),
        LogEntry(timestamp=_ts(3), level="ERROR", message="timeout error", line_number=4),
        LogEntry(timestamp=_ts(4), level="DEBUG", message="trace info", line_number=5),
    ]


@pytest.fixture
def rules():
    return [
        RouteRule(name="errors", level="ERROR"),
        RouteRule(name="warnings", level="WARN"),
        RouteRule(name="memory", pattern="memory"),
    ]


def test_route_rule_invalid():
    with pytest.raises(ValueError):
        RouteRule(name="bad")


def test_route_entry_matches_level(sample_entries, rules):
    opts = RouterOptions(rules=rules)
    result = route_entry(sample_entries[0], opts)
    assert result.route == "errors"


def test_route_entry_default(sample_entries, rules):
    opts = RouterOptions(rules=rules, default_route="misc")
    result = route_entry(sample_entries[2], opts)  # INFO
    assert result.route == "misc"


def test_route_entries_count(sample_entries, rules):
    opts = RouterOptions(rules=rules)
    result = route_entries(sample_entries, opts)
    assert len(result) == len(sample_entries)


def test_group_by_route_keys(sample_entries, rules):
    opts = RouterOptions(rules=rules)
    routed = route_entries(sample_entries, opts)
    grouped = group_by_route(routed)
    assert "errors" in grouped
    assert "warnings" in grouped


def test_group_by_route_error_count(sample_entries, rules):
    opts = RouterOptions(rules=rules)
    routed = route_entries(sample_entries, opts)
    grouped = group_by_route(routed)
    assert len(grouped["errors"]) == 2


def test_run_route_pipeline_total(sample_entries, rules):
    opts = RoutePipelineOptions(rules=rules)
    grouped = run_route_pipeline(sample_entries, opts)
    total = sum(len(v) for v in grouped.values())
    assert total == len(sample_entries)


def test_run_route_pipeline_with_level_filter(sample_entries, rules):
    opts = RoutePipelineOptions(rules=rules, level="ERROR")
    grouped = run_route_pipeline(sample_entries, opts)
    total = sum(len(v) for v in grouped.values())
    assert total == 2


def test_route_summary_structure(sample_entries, rules):
    opts = RoutePipelineOptions(rules=rules)
    grouped = run_route_pipeline(sample_entries, opts)
    summary = route_summary(grouped)
    assert "total" in summary
    assert "routes" in summary
    assert summary["total"] == len(sample_entries)
