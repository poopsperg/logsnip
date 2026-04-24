from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from logsnip.parser import LogEntry


@dataclass
class ValidationIssue:
    line_number: int
    message: str
    entry: Optional[LogEntry] = None


@dataclass
class ValidationReport:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.issues) == 0

    @property
    def issue_count(self) -> int:
        return len(self.issues)


@dataclass
class ValidateOptions:
    require_level: bool = True
    require_message: bool = True
    allowed_levels: Optional[List[str]] = None
    max_message_length: Optional[int] = None


def validate_entry(entry: LogEntry, opts: ValidateOptions) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if opts.require_level and not entry.level:
        issues.append(ValidationIssue(
            line_number=entry.line_number,
            message="Missing log level",
            entry=entry,
        ))

    if opts.require_message and not entry.message.strip():
        issues.append(ValidationIssue(
            line_number=entry.line_number,
            message="Empty message",
            entry=entry,
        ))

    if opts.allowed_levels and entry.level:
        normalized = entry.level.upper()
        allowed = [lvl.upper() for lvl in opts.allowed_levels]
        if normalized not in allowed:
            issues.append(ValidationIssue(
                line_number=entry.line_number,
                message=f"Unexpected level '{entry.level}'; allowed: {opts.allowed_levels}",
                entry=entry,
            ))

    if opts.max_message_length and len(entry.message) > opts.max_message_length:
        issues.append(ValidationIssue(
            line_number=entry.line_number,
            message=f"Message exceeds max length {opts.max_message_length}",
            entry=entry,
        ))

    return issues


def validate_entries(
    entries: List[LogEntry],
    opts: Optional[ValidateOptions] = None,
) -> ValidationReport:
    if opts is None:
        opts = ValidateOptions()
    report = ValidationReport()
    for entry in entries:
        report.issues.extend(validate_entry(entry, opts))
    return report


def format_validation_report(report: ValidationReport) -> str:
    if report.valid:
        return "Validation passed: no issues found."
    lines = [f"Validation failed: {report.issue_count} issue(s) found."]
    for issue in report.issues:
        lines.append(f"  line {issue.line_number}: {issue.message}")
    return "\n".join(lines)
