"""Format aggregated buckets for display."""
from __future__ import annotations
import json
from typing import List
from logsnip.aggregator import AggregatedBucket


def format_bucket_summary(bucket: AggregatedBucket, index: int) -> str:
    ts_range = ""
    if bucket.start and bucket.end:
        ts_range = f" [{bucket.start} — {bucket.end}]"
    return f"Bucket {index}{ts_range} | key={bucket.key} | count={bucket.count}"


def format_bucket_text(bucket: AggregatedBucket, index: int) -> str:
    lines = [format_bucket_summary(bucket, index)]
    for e in bucket.entries:
        lines.append(f"  {e.timestamp} [{e.level}] {e.message}")
    return "\n".join(lines)


def format_bucket_json(bucket: AggregatedBucket, index: int) -> str:
    return json.dumps({
        "index": index,
        "key": bucket.key,
        "count": bucket.count,
        "entries": [
            {"timestamp": str(e.timestamp), "level": e.level, "message": e.message}
            for e in bucket.entries
        ],
    }, indent=2)


def format_buckets(buckets: List[AggregatedBucket], fmt: str = "text") -> str:
    parts = []
    for i, bucket in enumerate(buckets):
        if fmt == "json":
            parts.append(format_bucket_json(bucket, i))
        else:
            parts.append(format_bucket_text(bucket, i))
    sep = "\n" if fmt == "json" else "\n\n"
    return sep.join(parts)
