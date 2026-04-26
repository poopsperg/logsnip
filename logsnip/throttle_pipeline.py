"""Pipeline wrapper around the throttler module."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from logsnip.parser import LogEntry
from logsnip.filter import apply_filters
from logsnip.throttler import ThrottleOptions, throttle_entries, throttle_summary


@dataclass
class ThrottlePipelineOptions:
    max_per_window: int = 10
    window_seconds: int = 60
    # pre-filter before throttling
    level: str | None = None
    pattern: str | None = None
    exclude: str | None = None
    # throttle-specific level / pattern scope
    throttle_level: str | None = None
    throttle_pattern: str | None = None


def run_throttle_pipeline(
    entries: List[LogEntry],
    options: ThrottlePipelineOptions,
) -> List[LogEntry]:
    filtered = apply_filters(
        entries,
        level=options.level,
        pattern=options.pattern,
        exclude=options.exclude,
    )
    throttle_opts = ThrottleOptions(
        max_per_window=options.max_per_window,
        window_seconds=options.window_seconds,
        level=options.throttle_level,
        pattern=options.throttle_pattern,
    )
    return list(throttle_entries(filtered, throttle_opts))


def pipeline_summary(
    original: List[LogEntry],
    result: List[LogEntry],
    options: ThrottlePipelineOptions,
) -> str:
    return (
        throttle_summary(original, result)
        + f" (window={options.window_seconds}s, max={options.max_per_window})"
    )
