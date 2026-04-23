from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import re
from logsnip.parser import LogEntry


@dataclass
class AlertRule:
    name: str
    pattern: Optional[str] = None
    level: Optional[str] = None
    min_score: Optional[float] = None

    def __post_init__(self):
        if not any([self.pattern, self.level, self.min_score is not None]):
            raise ValueError("AlertRule requires at least one condition")
        self._regex = re.compile(self.pattern, re.IGNORECASE) if self.pattern else None

    def matches(self, entry: LogEntry) -> bool:
        if self.level and entry.level.upper() != self.level.upper():
            return False
        if self._regex and not self._regex.search(entry.message):
            return False
        if self.min_score is not None and (entry.score is None or entry.score < self.min_score):
            return False
        return True


@dataclass
class Alert:
    rule_name: str
    entry: LogEntry

    @property
    def timestamp(self):
        return self.entry.timestamp

    @property
    def message(self):
        return self.entry.message


@dataclass
class AlertOptions:
    rules: List[AlertRule] = field(default_factory=list)
    limit: Optional[int] = None


def evaluate_entry(entry: LogEntry, rules: List[AlertRule]) -> List[Alert]:
    return [Alert(rule_name=r.name, entry=entry) for r in rules if r.matches(entry)]


def run_alerts(entries: List[LogEntry], options: AlertOptions) -> List[Alert]:
    alerts: List[Alert] = []
    for entry in entries:
        alerts.extend(evaluate_entry(entry, options.rules))
    if options.limit is not None:
        alerts = alerts[: options.limit]
    return alerts


def alert_summary(alerts: List[Alert]) -> dict:
    by_rule: dict = {}
    for a in alerts:
        by_rule[a.rule_name] = by_rule.get(a.rule_name, 0) + 1
    return {"total": len(alerts), "by_rule": by_rule}
