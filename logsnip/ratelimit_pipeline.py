"""Pipeline wrapper for rate-limiting log entries."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from logsnip.parser import LogEntry
from logsnip.filter import filter_by_level, filter_by_pattern
from logsnip.ratelimiter import RateLimitOptions, RateLimitReport, ratelimit_entries, ratelimit_summary


@dataclass
class RateLimitPipelineOptions:
    max_per_window: int = 10
    window_seconds: int = 60
    level_filter: Optional[str] = None
    pattern: Optional[str] = None
    pre_filter_level: Optional[str] = None
    pre_filter_pattern: Optional[str] = None


def run_ratelimit_pipeline(
    entries: List[LogEntry], opts: RateLimitPipelineOptions
) -> tuple[List[LogEntry], RateLimitReport]:
    """Apply optional pre-filters then rate-limit, returning results and report."""
    filtered = list(entries)

    if opts.pre_filter_level:
        filtered = list(filter_by_level(filtered, [opts.pre_filter_level]))
    if opts.pre_filter_pattern:
        filtered = list(filter_by_pattern(filtered, opts.pre_filter_pattern))

    rl_opts = RateLimitOptions(
        max_per_window=opts.max_per_window,
        window_seconds=opts.window_seconds,
        level_filter=opts.level_filter,
        pattern=opts.pattern,
    )

    result = list(ratelimit_entries(filtered, rl_opts))
    report = ratelimit_summary(filtered, result)
    return result, report


def pipeline_summary(report: RateLimitReport) -> str:
    return (
        f"rate-limit: {report.total_in} in, "
        f"{report.total_out} out, "
        f"{report.dropped} dropped ({report.drop_pct}%)"
    )
