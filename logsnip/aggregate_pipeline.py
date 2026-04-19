"""Pipeline integration for aggregation."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.aggregator import AggregateOptions, AggregatedBucket, aggregate


@dataclass
class AggregatePipelineOptions:
    window_seconds: int = 60
    group_by_level: bool = False
    min_bucket_size: int = 1


def run_aggregate_pipeline(
    entries: List[LogEntry], opts: AggregatePipelineOptions
) -> List[AggregatedBucket]:
    agg_opts = AggregateOptions(
        window_seconds=opts.window_seconds,
        group_by_level=opts.group_by_level,
    )
    buckets = aggregate(entries, agg_opts)
    return [b for b in buckets if b.count >= opts.min_bucket_size]


def aggregate_summary(buckets: List[AggregatedBucket]) -> dict:
    total_entries = sum(b.count for b in buckets)
    return {
        "buckets": len(buckets),
        "total_entries": total_entries,
        "avg_bucket_size": round(total_entries / len(buckets), 2) if buckets else 0,
        "keys": [b.key for b in buckets],
    }
