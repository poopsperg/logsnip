"""Mask sensitive fields in log entries using regex rules."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from logsnip.parser import LogEntry


@dataclass
class MaskRule:
    pattern: str
    replacement: str = "***"
    field: str = "message"  # 'message' or 'level'
    _compiled: re.Pattern = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.pattern:
            raise ValueError("MaskRule pattern must not be empty")
        if self.field not in ("message", "level"):
            raise ValueError("MaskRule field must be 'message' or 'level'")
        self._compiled = re.compile(self.pattern)

    def apply(self, text: str) -> str:
        return self._compiled.sub(self.replacement, text)


@dataclass
class MaskedEntry:
    timestamp: object
    level: str
    message: str
    original_message: str
    masked: bool


@dataclass
class MaskOptions:
    rules: List[MaskRule] = field(default_factory=list)
    level_filter: Optional[str] = None
    pattern_filter: Optional[str] = None


def mask_entry(entry: LogEntry, rules: List[MaskRule]) -> MaskedEntry:
    message = entry.message
    level = entry.level
    original = entry.message
    changed = False
    for rule in rules:
        if rule.field == "message":
            new_msg = rule.apply(message)
            if new_msg != message:
                changed = True
            message = new_msg
        elif rule.field == "level":
            new_level = rule.apply(level)
            if new_level != level:
                changed = True
            level = new_level
    return MaskedEntry(
        timestamp=entry.timestamp,
        level=level,
        message=message,
        original_message=original,
        masked=changed,
    )


def mask_entries(
    entries: List[LogEntry], options: MaskOptions
) -> List[MaskedEntry]:
    filtered = list(entries)
    if options.level_filter:
        lvl = options.level_filter.upper()
        filtered = [e for e in filtered if e.level.upper() == lvl]
    if options.pattern_filter:
        pat = re.compile(options.pattern_filter)
        filtered = [e for e in filtered if pat.search(e.message)]
    return [mask_entry(e, options.rules) for e in filtered]


def mask_summary(results: List[MaskedEntry]) -> str:
    total = len(results)
    masked = sum(1 for r in results if r.masked)
    return f"total={total} masked={masked} unchanged={total - masked}"
