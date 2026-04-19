from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.filter import apply_filters
from logsnip.profiler import ProfileReport, profile_entries, format_profile


@dataclass
class ProfilePipelineOptions:
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None


def run_profile_pipeline(
    entries: List[LogEntry],
    options: ProfilePipelineOptions,
) -> ProfileReport:
    filtered = apply_filters(
        entries,
        level=options.level,
        pattern=options.pattern,
        exclude=options.exclude,
    )
    return profile_entries(filtered)


def profile_summary(report: ProfileReport) -> str:
    return format_profile(report)
