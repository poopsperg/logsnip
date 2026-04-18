"""Entry sampling utilities for logsnip."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from logsnip.parser import LogEntry


@dataclass
class SampleOptions:
    rate: float = 1.0        # fraction 0.0-1.0
    max_entries: Optional[int] = None
    every_nth: Optional[int] = None


def sample_by_rate(entries: List[LogEntry], rate: float) -> List[LogEntry]:
    """Keep approximately `rate` fraction of entries."""
    if not 0.0 < rate <= 1.0:
        raise ValueError(f"rate must be in (0.0, 1.0], got {rate}")
    if rate == 1.0:
        return list(entries)
    step = 1.0 / rate
    result = []
    acc = 0.0
    for entry in entries:
        acc += 1.0
        if acc >= step:
            result.append(entry)
            acc -= step
    return result


def sample_every_nth(entries: List[LogEntry], n: int) -> List[LogEntry]:
    """Keep every nth entry (1-based)."""
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    return [e for i, e in enumerate(entries) if i % n == 0]


def sample_head(entries: List[LogEntry], max_entries: int) -> List[LogEntry]:
    """Keep at most max_entries from the start."""
    if max_entries < 0:
        raise ValueError(f"max_entries must be >= 0, got {max_entries}")
    return entries[:max_entries]


def apply_sampling(entries: List[LogEntry], opts: SampleOptions) -> List[LogEntry]:
    """Apply sampling options in order: every_nth -> rate -> max_entries."""
    result = list(entries)
    if opts.every_nth is not None:
        result = sample_every_nth(result, opts.every_nth)
    if opts.rate != 1.0:
        result = sample_by_rate(result, opts.rate)
    if opts.max_entries is not None:
        result = sample_head(result, opts.max_entries)
    return result
