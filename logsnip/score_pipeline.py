from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.scorer import ScoreOptions, ScoredEntry, score_entries, top_entries
from logsnip.filter import apply_filters


@dataclass
class ScorePipelineOptions:
    keywords: List[str] = field(default_factory=list)
    keyword_weight: int = 2
    level: Optional[str] = None
    pattern: Optional[str] = None
    top_n: Optional[int] = None
    min_score: int = 0


def run_score_pipeline(
    entries: List[LogEntry], options: ScorePipelineOptions
) -> List[ScoredEntry]:
    filtered = apply_filters(
        entries,
        level=options.level,
        pattern=options.pattern,
    )
    score_opts = ScoreOptions(
        keywords=options.keywords,
        keyword_weight=options.keyword_weight,
    )
    scored = score_entries(filtered, score_opts)
    scored = [s for s in scored if s.score >= options.min_score]
    if options.top_n is not None:
        scored = top_entries(scored, options.top_n)
    return scored


def score_summary(scored: List[ScoredEntry]) -> dict:
    if not scored:
        return {"total": 0, "max_score": 0, "avg_score": 0.0}
    scores = [s.score for s in scored]
    return {
        "total": len(scored),
        "max_score": max(scores),
        "avg_score": round(sum(scores) / len(scores), 2),
    }
