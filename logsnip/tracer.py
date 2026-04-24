from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from logsnip.parser import LogEntry


@dataclass
class TraceSpan:
    trace_id: str
    entries: List[LogEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)

    @property
    def start(self) -> Optional[float]:
        return self.entries[0].timestamp if self.entries else None

    @property
    def end(self) -> Optional[float]:
        return self.entries[-1].timestamp if self.entries else None

    @property
    def duration(self) -> Optional[float]:
        if self.start is not None and self.end is not None:
            return self.end - self.start
        return None

    @property
    def levels(self) -> List[str]:
        return [e.level for e in self.entries]


@dataclass
class TraceOptions:
    id_pattern: str = r"trace[_-]?id[=:]\s*([\w-]+)"
    min_span_size: int = 1


def extract_trace_id(message: str, pattern: str) -> Optional[str]:
    import re
    m = re.search(pattern, message, re.IGNORECASE)
    return m.group(1) if m else None


def trace_entries(
    entries: List[LogEntry],
    options: Optional[TraceOptions] = None,
) -> Dict[str, TraceSpan]:
    opts = options or TraceOptions()
    spans: Dict[str, TraceSpan] = {}
    for entry in entries:
        tid = extract_trace_id(entry.message, opts.id_pattern)
        if tid is None:
            continue
        if tid not in spans:
            spans[tid] = TraceSpan(trace_id=tid)
        spans[tid].entries.append(entry)
    if opts.min_span_size > 1:
        spans = {k: v for k, v in spans.items() if v.count >= opts.min_span_size}
    return spans


def trace_summary(spans: Dict[str, TraceSpan]) -> str:
    if not spans:
        return "No trace spans found."
    lines = [f"Trace spans: {len(spans)}"]
    for tid, span in spans.items():
        dur = f"{span.duration:.3f}s" if span.duration is not None else "n/a"
        lines.append(f"  [{tid}] entries={span.count} duration={dur}")
    return "\n".join(lines)
