from dataclasses import dataclass
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.comparer import CompareOptions, CompareResult, compare_entries, compare_summary


@dataclass
class ComparePipelineOptions:
    label_a: str = "A"
    label_b: str = "B"
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None


def run_compare_pipeline(
    entries_a: List[LogEntry],
    entries_b: List[LogEntry],
    opts: Optional[ComparePipelineOptions] = None,
) -> CompareResult:
    if opts is None:
        opts = ComparePipelineOptions()

    cmp_opts = CompareOptions(
        level=opts.level,
        pattern=opts.pattern,
        exclude=opts.exclude,
    )

    return compare_entries(
        entries_a,
        entries_b,
        label_a=opts.label_a,
        label_b=opts.label_b,
        opts=cmp_opts,
    )


def pipeline_summary(result: CompareResult) -> str:
    return compare_summary(result)
