from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from logsnip.parser import LogEntry
from logsnip.trendline import TrendBucket, TrendOptions, compute_trend, format_trend


@dataclass
class TrendPipelineOptions:
    window_minutes: int = 1
    level_filter: str | None = None
    pattern: str | None = None
    bar_width: int = 20


def run_trend_pipeline(
    entries: Sequence[LogEntry],
    options: TrendPipelineOptions | None = None,
) -> List[TrendBucket]:
    opts = options or TrendPipelineOptions()
    trend_opts = TrendOptions(
        window_minutes=opts.window_minutes,
        level_filter=opts.level_filter,
        pattern=opts.pattern,
    )
    return compute_trend(entries, trend_opts)


def trend_summary(buckets: List[TrendBucket], bar_width: int = 20) -> str:
    if not buckets:
        return "trend: no data"
    total = sum(b.count for b in buckets)
    peak = max(buckets, key=lambda b: b.count)
    formatted = format_trend(buckets, bar_width=bar_width)
    header = (
        f"trend: {len(buckets)} bucket(s), "
        f"{total} entries total, "
        f"peak at {peak.minute.strftime('%H:%M')} ({peak.count})"
    )
    return f"{header}\n{formatted}"
