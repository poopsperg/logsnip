from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from logsnip.parser import LogEntry

LEVEL_WEIGHTS = {
    "critical": 5,
    "error": 4,
    "warning": 3,
    "warn": 3,
    "info": 1,
    "debug": 0,
}


@dataclass
class ScoredEntry:
    entry: LogEntry
    score: int
    reasons: List[str] = field(default_factory=list)

    @property
    def timestamp(self):
        return self.entry.timestamp

    @property
    def level(self):
        return self.entry.level

    @property
    def message(self):
        return self.entry.message


@dataclass
class ScoreOptions:
    keywords: List[str] = field(default_factory=list)
    keyword_weight: int = 2
    level_weights: dict = field(default_factory=lambda: dict(LEVEL_WEIGHTS))


def score_entry(entry: LogEntry, options: ScoreOptions) -> ScoredEntry:
    reasons: List[str] = []
    total = 0

    level_key = (entry.level or "").lower()
    lw = options.level_weights.get(level_key, 0)
    if lw:
        total += lw
        reasons.append(f"level:{level_key}={lw}")

    msg_lower = (entry.message or "").lower()
    for kw in options.keywords:
        if kw.lower() in msg_lower:
            total += options.keyword_weight
            reasons.append(f"keyword:{kw}")

    return ScoredEntry(entry=entry, score=total, reasons=reasons)


def score_entries(
    entries: List[LogEntry], options: Optional[ScoreOptions] = None
) -> List[ScoredEntry]:
    if options is None:
        options = ScoreOptions()
    return [score_entry(e, options) for e in entries]


def top_entries(scored: List[ScoredEntry], n: int = 10) -> List[ScoredEntry]:
    return sorted(scored, key=lambda s: s.score, reverse=True)[:n]
