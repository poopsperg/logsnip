"""Anomaly detection for log entries based on frequency and pattern deviation."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from collections import Counter
from logsnip.parser import LogEntry


@dataclass
class AnomalyOptions:
    window_seconds: int = 60
    min_occurrences: int = 3
    level_filter: Optional[str] = None
    pattern: Optional[str] = None


@dataclass
class Anomaly:
    entry: LogEntry
    reason: str
    score: float

    @property
    def timestamp(self) -> datetime:
        return self.entry.timestamp

    @property
    def level(self) -> str:
        return self.entry.level

    @property
    def message(self) -> str:
        return self.entry.message


def _bucket_key(entry: LogEntry, window_seconds: int) -> int:
    ts = entry.timestamp
    epoch = int(ts.timestamp())
    return epoch // window_seconds


def detect_anomalies(entries: List[LogEntry], opts: AnomalyOptions) -> List[Anomaly]:
    """Detect entries that appear suspiciously often within a time window."""
    bucket_counts: Counter = Counter()
    bucket_entries: dict = {}

    for entry in entries:
        key = (_bucket_key(entry, opts.window_seconds), entry.level, entry.message)
        bucket_counts[key] += 1
        bucket_entries.setdefault(key, entry)

    anomalies: List[Anomaly] = []
    for key, count in bucket_counts.items():
        if count >= opts.min_occurrences:
            entry = bucket_entries[key]
            score = round(count / opts.min_occurrences, 2)
            anomalies.append(Anomaly(
                entry=entry,
                reason=f"appeared {count}x in {opts.window_seconds}s window",
                score=score,
            ))

    return sorted(anomalies, key=lambda a: a.score, reverse=True)


def anomaly_summary(anomalies: List[Anomaly]) -> dict:
    return {
        "total": len(anomalies),
        "max_score": max((a.score for a in anomalies), default=0.0),
        "levels": list({a.level for a in anomalies}),
    }
