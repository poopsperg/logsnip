from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, Optional
from logsnip.parser import LogEntry


@dataclass
class RouteRule:
    name: str
    level: Optional[str] = None
    pattern: Optional[str] = None

    def __post_init__(self):
        if not self.level and not self.pattern:
            raise ValueError("RouteRule requires level or pattern")

    def matches(self, entry: LogEntry) -> bool:
        if self.level and entry.level.upper() != self.level.upper():
            return False
        if self.pattern and self.pattern.lower() not in entry.message.lower():
            return False
        return True


@dataclass
class RoutedEntry:
    entry: LogEntry
    route: str

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
class RouterOptions:
    rules: List[RouteRule] = field(default_factory=list)
    default_route: str = "default"


def route_entry(entry: LogEntry, options: RouterOptions) -> RoutedEntry:
    for rule in options.rules:
        if rule.matches(entry):
            return RoutedEntry(entry=entry, route=rule.name)
    return RoutedEntry(entry=entry, route=options.default_route)


def route_entries(entries: List[LogEntry], options: RouterOptions) -> List[RoutedEntry]:
    return [route_entry(e, options) for e in entries]


def group_by_route(routed: List[RoutedEntry]) -> dict[str, List[RoutedEntry]]:
    result: dict[str, List[RoutedEntry]] = {}
    for r in routed:
        result.setdefault(r.route, []).append(r)
    return result
