from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.filter import apply_filters
from logsnip.alerter import AlertOptions, AlertRule, Alert, run_alerts, alert_summary


@dataclass
class AlertPipelineOptions:
    rules: List[AlertRule] = field(default_factory=list)
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None
    limit: Optional[int] = None


def run_alert_pipeline(entries: List[LogEntry], options: AlertPipelineOptions) -> List[Alert]:
    filtered = apply_filters(
        entries,
        level=options.level,
        pattern=options.pattern,
        exclude=options.exclude,
    )
    opts = AlertOptions(rules=options.rules, limit=options.limit)
    return run_alerts(filtered, opts)


def pipeline_summary(alerts: List[Alert]) -> dict:
    return alert_summary(alerts)
