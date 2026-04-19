from dataclasses import dataclass, field
from typing import List, Optional, Callable
from logsnip.parser import LogEntry
from logsnip.transformer import TransformOptions, transform_entries


@dataclass
class TransformPipelineOptions:
    uppercase_level: bool = False
    truncate_message: Optional[int] = None
    add_prefix: Optional[str] = None
    strip_fields: List[str] = field(default_factory=list)
    custom: Optional[Callable[[LogEntry], LogEntry]] = None


def run_transform_pipeline(
    entries: List[LogEntry], opts: TransformPipelineOptions
) -> List[LogEntry]:
    transform_opts = TransformOptions(
        uppercase_level=opts.uppercase_level,
        truncate_message=opts.truncate_message,
        add_prefix=opts.add_prefix,
        strip_fields=opts.strip_fields,
        custom=opts.custom,
    )
    return transform_entries(entries, transform_opts)


def transform_summary(original: List[LogEntry], transformed: List[LogEntry]) -> dict:
    return {
        "total_input": len(original),
        "total_output": len(transformed),
        "changed": sum(
            1
            for a, b in zip(original, transformed)
            if a.message != b.message or a.level != b.level
        ),
    }
