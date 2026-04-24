from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from logsnip.parser import LogEntry
from logsnip.filter import apply_filters
from logsnip.validator import ValidateOptions, ValidationReport, validate_entries


@dataclass
class ValidatePipelineOptions:
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None
    require_level: bool = True
    require_message: bool = True
    allowed_levels: Optional[List[str]] = None
    max_message_length: Optional[int] = None


def run_validate_pipeline(
    entries: List[LogEntry],
    opts: Optional[ValidatePipelineOptions] = None,
) -> ValidationReport:
    if opts is None:
        opts = ValidatePipelineOptions()

    filtered = apply_filters(
        entries,
        level=opts.level,
        pattern=opts.pattern,
        exclude=opts.exclude,
    )

    validate_opts = ValidateOptions(
        require_level=opts.require_level,
        require_message=opts.require_message,
        allowed_levels=opts.allowed_levels,
        max_message_length=opts.max_message_length,
    )

    return validate_entries(filtered, validate_opts)


def validate_summary(report: ValidationReport) -> str:
    status = "PASS" if report.valid else "FAIL"
    return f"[{status}] {report.issue_count} issue(s) detected."
