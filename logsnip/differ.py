"""Diff two streams of log entries by message content."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Sequence
from logsnip.parser import LogEntry


@dataclass
class DiffResult:
    only_in_a: List[LogEntry]
    only_in_b: List[LogEntry]
    common: List[LogEntry]

    @property
    def total_a(self) -> int:
        return len(self.only_in_a) + len(self.common)

    @property
    def total_b(self) -> int:
        return len(self.only_in_b) + len(self.common)


def _message_keys(entries: Sequence[LogEntry]) -> dict:
    seen = {}
    for e in entries:
        key = e.message.strip()
        if key not in seen:
            seen[key] = e
    return seen


def diff_entries(a: Sequence[LogEntry], b: Sequence[LogEntry]) -> DiffResult:
    """Compare two entry sequences by message. Returns sets: only_a, only_b, common."""
    keys_a = _message_keys(a)
    keys_b = _message_keys(b)

    common_keys = keys_a.keys() & keys_b.keys()
    only_a = [e for k, e in keys_a.items() if k not in common_keys]
    only_b = [e for k, e in keys_b.items() if k not in common_keys]
    common = [keys_a[k] for k in common_keys]

    return DiffResult(only_in_a=only_a, only_in_b=only_b, common=common)


def format_diff(result: DiffResult) -> str:
    """Return a human-readable diff summary."""
    lines = [
        f"Common entries   : {len(result.common)}",
        f"Only in A        : {len(result.only_in_a)}",
        f"Only in B        : {len(result.only_in_b)}",
    ]
    if result.only_in_a:
        lines.append("\n< Only in A:")
        for e in result.only_in_a:
            lines.append(f"  - [{e.level}] {e.message}")
    if result.only_in_b:
        lines.append("\n> Only in B:")
        for e in result.only_in_b:
            lines.append(f"  + [{e.level}] {e.message}")
    return "\n".join(lines)
