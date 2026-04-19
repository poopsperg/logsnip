from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.filter import apply_filters
from logsnip.router import RouterOptions, RouteRule, RoutedEntry, route_entries, group_by_route


@dataclass
class RoutePipelineOptions:
    rules: List[RouteRule] = field(default_factory=list)
    default_route: str = "default"
    level: Optional[str] = None
    pattern: Optional[str] = None


def run_route_pipeline(
    entries: List[LogEntry],
    options: RoutePipelineOptions,
) -> dict[str, List[RoutedEntry]]:
    filtered = apply_filters(entries, level=options.level, pattern=options.pattern)
    opts = RouterOptions(rules=options.rules, default_route=options.default_route)
    routed = route_entries(filtered, opts)
    return group_by_route(routed)


def route_summary(grouped: dict[str, List[RoutedEntry]]) -> dict:
    return {
        "routes": {name: len(entries) for name, entries in grouped.items()},
        "total": sum(len(v) for v in grouped.values()),
    }
