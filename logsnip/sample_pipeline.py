"""Pipeline integration for entry sampling."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from logsnip.parser import LogEntry
from logsnip.pipeline import PipelineOptions, collect_pipeline
from logsnip.sampler import SampleOptions, apply_sampling


@dataclass
class SampledPipelineOptions:
    pipeline: PipelineOptions
    sample: SampleOptions = field(default_factory=SampleOptions)


def run_sampled_pipeline(
    lines: List[str],
    opts: SampledPipelineOptions,
) -> List[LogEntry]:
    """Run the standard pipeline then apply sampling."""
    entries = collect_pipeline(lines, opts.pipeline)
    return apply_sampling(entries, opts.sample)


def sampled_pipeline_summary(entries: List[LogEntry], original_count: int) -> dict:
    """Return a small summary dict for sampled results."""
    return {
        "original": original_count,
        "sampled": len(entries),
        "ratio": round(len(entries) / original_count, 4) if original_count else 0.0,
        "first_ts": entries[0].timestamp.isoformat() if entries else None,
        "last_ts": entries[-1].timestamp.isoformat() if entries else None,
    }
