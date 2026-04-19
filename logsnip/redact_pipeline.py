"""Pipeline helpers for redaction."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from logsnip.parser import LogEntry
from logsnip.redactor import RedactOptions, RedactRule, redact_entries


@dataclass
class RedactPipelineOptions:
    redact_ip: bool = False
    redact_email: bool = False
    patterns: List[str] = field(default_factory=list)
    replacement: str = "[REDACTED]"


def run_redact_pipeline(
    entries: List[LogEntry], opts: RedactPipelineOptions
) -> List[LogEntry]:
    rules = [RedactRule(p, opts.replacement) for p in opts.patterns]
    redact_opts = RedactOptions(
        rules=rules,
        redact_ip=opts.redact_ip,
        redact_email=opts.redact_email,
    )
    return redact_entries(entries, redact_opts)


def redact_summary(original: List[LogEntry], redacted: List[LogEntry]) -> dict:
    changed = sum(
        1 for a, b in zip(original, redacted) if a.message != b.message
    )
    return {"total": len(redacted), "changed": changed}
