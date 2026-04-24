from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from logsnip.parser import LogEntry
from logsnip.filter import apply_filters
from logsnip.tracer import TraceOptions, TraceSpan, trace_entries, trace_summary


@dataclass
class TracePipelineOptions:
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None
    trace_options: TraceOptions = field(default_factory=TraceOptions)


def run_trace_pipeline(
    entries: List[LogEntry],
    options: Optional[TracePipelineOptions] = None,
) -> Dict[str, TraceSpan]:
    opts = options or TracePipelineOptions()
    filtered = apply_filters(
        entries,
        level=opts.level,
        pattern=opts.pattern,
        exclude=opts.exclude,
    )
    return trace_entries(filtered, opts.trace_options)


def pipeline_summary(spans: Dict[str, TraceSpan]) -> str:
    return trace_summary(spans)
