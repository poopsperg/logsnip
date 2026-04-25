"""Pipeline for running anomaly detection over filtered log entries."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.filter import apply_filters
from logsnip.detector import AnomalyOptions, Anomaly, detect_anomalies, anomaly_summary


@dataclass
class DetectPipelineOptions:
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None
    window_seconds: int = 60
    min_occurrences: int = 3
    top_n: Optional[int] = None


def run_detect_pipeline(
    entries: List[LogEntry],
    opts: DetectPipelineOptions,
) -> List[Anomaly]:
    filtered = apply_filters(
        entries,
        level=opts.level,
        pattern=opts.pattern,
        exclude=opts.exclude,
    )
    detect_opts = AnomalyOptions(
        window_seconds=opts.window_seconds,
        min_occurrences=opts.min_occurrences,
    )
    anomalies = detect_anomalies(filtered, detect_opts)
    if opts.top_n is not None:
        anomalies = anomalies[: opts.top_n]
    return anomalies


def detect_pipeline_summary(anomalies: List[Anomaly]) -> str:
    s = anomaly_summary(anomalies)
    levels = ", ".join(s["levels"]) if s["levels"] else "none"
    return (
        f"anomalies={s['total']} max_score={s['max_score']} levels=[{levels}]"
    )
