"""Dispatch log entries to multiple named handlers based on rules."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from logsnip.parser import LogEntry
from logsnip.filter import filter_by_level, filter_by_pattern


Handler = Callable[[LogEntry], None]


@dataclass
class DispatchRule:
    name: str
    handler: Handler
    level: Optional[str] = None
    pattern: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("DispatchRule name must not be empty")
        if self.level is None and self.pattern is None:
            raise ValueError("DispatchRule requires at least one of: level, pattern")

    def matches(self, entry: LogEntry) -> bool:
        if self.level and entry.level.upper() != self.level.upper():
            return False
        if self.pattern:
            import re
            if not re.search(self.pattern, entry.message, re.IGNORECASE):
                return False
        return True


@dataclass
class DispatchOptions:
    rules: List[DispatchRule] = field(default_factory=list)
    catch_all: Optional[Handler] = None


@dataclass
class DispatchResult:
    total: int = 0
    dispatched: int = 0
    unmatched: int = 0
    counts: Dict[str, int] = field(default_factory=dict)


def dispatch_entries(
    entries: List[LogEntry],
    options: DispatchOptions,
) -> DispatchResult:
    """Dispatch each entry to the first matching rule's handler."""
    result = DispatchResult()
    for rule in options.rules:
        result.counts[rule.name] = 0

    for entry in entries:
        result.total += 1
        matched = False
        for rule in options.rules:
            if rule.matches(entry):
                rule.handler(entry)
                result.counts[rule.name] = result.counts.get(rule.name, 0) + 1
                result.dispatched += 1
                matched = True
                break
        if not matched:
            result.unmatched += 1
            if options.catch_all:
                options.catch_all(entry)

    return result


def dispatch_summary(result: DispatchResult) -> str:
    lines = [
        f"Total entries : {result.total}",
        f"Dispatched    : {result.dispatched}",
        f"Unmatched     : {result.unmatched}",
    ]
    for name, count in result.counts.items():
        lines.append(f"  [{name}]: {count}")
    return "\n".join(lines)
