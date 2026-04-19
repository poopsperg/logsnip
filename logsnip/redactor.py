"""Redact sensitive patterns from log entry messages."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
import re
from logsnip.parser import LogEntry


@dataclass
class RedactRule:
    pattern: str
    replacement: str = "[REDACTED]"
    _compiled: re.Pattern = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._compiled = re.compile(self.pattern)

    def apply(self, text: str) -> str:
        return self._compiled.sub(self.replacement, text)


@dataclass
class RedactOptions:
    rules: List[RedactRule] = field(default_factory=list)
    redact_ip: bool = False
    redact_email: bool = False


_IP_RULE = RedactRule(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[IP]")
_EMAIL_RULE = RedactRule(r"[\w.+-]+@[\w-]+\.[\w.]+", "[EMAIL]")


def redact_message(message: str, rules: List[RedactRule]) -> str:
    for rule in rules:
        message = rule.apply(message)
    return message


def redact_entry(entry: LogEntry, opts: RedactOptions) -> LogEntry:
    rules = list(opts.rules)
    if opts.redact_ip:
        rules.append(_IP_RULE)
    if opts.redact_email:
        rules.append(_EMAIL_RULE)
    new_msg = redact_message(entry.message, rules)
    return LogEntry(timestamp=entry.timestamp, level=entry.level,
                    message=new_msg, raw=entry.raw, line_number=entry.line_number)


def redact_entries(entries: List[LogEntry], opts: RedactOptions) -> List[LogEntry]:
    return [redact_entry(e, opts) for e in entries]
