"""Formatters for anomaly detection output."""
from __future__ import annotations
import json
from typing import List
from logsnip.detector import Anomaly


def _ts_str(anomaly: Anomaly) -> str:
    return anomaly.timestamp.strftime("%Y-%m-%dT%H:%M:%S")


def format_anomaly_summary(anomaly: Anomaly, index: int) -> str:
    return f"[{index}] {_ts_str(anomaly)} {anomaly.level} score={anomaly.score} — {anomaly.reason}"


def format_anomaly_text(anomalies: List[Anomaly]) -> str:
    if not anomalies:
        return "No anomalies detected."
    lines = []
    for i, a in enumerate(anomalies, 1):
        lines.append(format_anomaly_summary(a, i))
        lines.append(f"  {a.message}")
    return "\n".join(lines)


def format_anomaly_json(anomalies: List[Anomaly]) -> str:
    records = [
        {
            "timestamp": _ts_str(a),
            "level": a.level,
            "message": a.message,
            "reason": a.reason,
            "score": a.score,
        }
        for a in anomalies
    ]
    return json.dumps(records, indent=2)


def format_anomaly_jsonl(anomalies: List[Anomaly]) -> str:
    lines = [
        json.dumps({
            "timestamp": _ts_str(a),
            "level": a.level,
            "message": a.message,
            "reason": a.reason,
            "score": a.score,
        })
        for a in anomalies
    ]
    return "\n".join(lines)


def format_anomalies(anomalies: List[Anomaly], fmt: str = "text") -> str:
    if fmt == "json":
        return format_anomaly_json(anomalies)
    if fmt == "jsonl":
        return format_anomaly_jsonl(anomalies)
    return format_anomaly_text(anomalies)
