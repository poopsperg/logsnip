from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional
from collections import Counter
from logsnip.parser import LogEntry


@dataclass
class SummaryReport:
    total: int
    level_counts: Dict[str, int]
    top_messages: List[tuple]
    first_ts: Optional[str]
    last_ts: Optional[str]
    unique_messages: int


@dataclass
class SummaryOptions:
    top_n: int = 5
    level_filter: Optional[str] = None
    pattern: Optional[str] = None


def summarize_entries(entries: List[LogEntry], options: Optional[SummaryOptions] = None) -> SummaryReport:
    if options is None:
        options = SummaryOptions()

    filtered = entries
    if options.level_filter:
        filtered = [e for e in filtered if e.level.upper() == options.level_filter.upper()]
    if options.pattern:
        import re
        rx = re.compile(options.pattern, re.IGNORECASE)
        filtered = [e for e in filtered if rx.search(e.message)]

    if not filtered:
        return SummaryReport(
            total=0,
            level_counts={},
            top_messages=[],
            first_ts=None,
            last_ts=None,
            unique_messages=0,
        )

    level_counts = dict(Counter(e.level.upper() for e in filtered))
    msg_counts = Counter(e.message for e in filtered)
    top_messages = msg_counts.most_common(options.top_n)
    timestamps = [e.timestamp for e in filtered if e.timestamp]
    first_ts = str(min(timestamps)) if timestamps else None
    last_ts = str(max(timestamps)) if timestamps else None

    return SummaryReport(
        total=len(filtered),
        level_counts=level_counts,
        top_messages=top_messages,
        first_ts=first_ts,
        last_ts=last_ts,
        unique_messages=len(msg_counts),
    )


def format_summary(report: SummaryReport) -> str:
    lines = [
        f"Total entries : {report.total}",
        f"Unique messages: {report.unique_messages}",
        f"First timestamp: {report.first_ts or 'N/A'}",
        f"Last timestamp : {report.last_ts or 'N/A'}",
        "Levels:",
    ]
    for lvl, cnt in sorted(report.level_counts.items()):
        lines.append(f"  {lvl}: {cnt}")
    lines.append("Top messages:")
    for msg, cnt in report.top_messages:
        short = msg[:60] + "..." if len(msg) > 60 else msg
        lines.append(f"  [{cnt}] {short}")
    return "\n".join(lines)
