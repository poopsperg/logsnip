"""Pipeline wrapper for masking sensitive data in log entries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from logsnip.parser import LogEntry
from logsnip.masker import MaskRule, MaskOptions, MaskedEntry, mask_entries, mask_summary


@dataclass
class MaskPipelineOptions:
    rules: List[MaskRule] = field(default_factory=list)
    level_filter: Optional[str] = None
    pattern_filter: Optional[str] = None
    only_masked: bool = False


def run_mask_pipeline(
    entries: List[LogEntry], options: MaskPipelineOptions
) -> List[MaskedEntry]:
    opts = MaskOptions(
        rules=options.rules,
        level_filter=options.level_filter,
        pattern_filter=options.pattern_filter,
    )
    results = mask_entries(entries, opts)
    if options.only_masked:
        results = [r for r in results if r.masked]
    return results


def pipeline_summary(results: List[MaskedEntry]) -> str:
    return mask_summary(results)
