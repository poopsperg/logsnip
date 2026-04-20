from dataclasses import dataclass, field
from typing import List, Optional
from logsnip.parser import LogEntry
from logsnip.filter import apply_filters


@dataclass
class CompareOptions:
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None


@dataclass
class CompareResult:
    label_a: str
    label_b: str
    entries_a: List[LogEntry]
    entries_b: List[LogEntry]
    only_in_a: List[LogEntry] = field(default_factory=list)
    only_in_b: List[LogEntry] = field(default_factory=list)
    common_messages: List[str] = field(default_factory=list)

    @property
    def total_a(self) -> int:
        return len(self.entries_a)

    @property
    def total_b(self) -> int:
        return len(self.entries_b)

    @property
    def overlap_count(self) -> int:
        return len(self.common_messages)


def _message_set(entries: List[LogEntry]) -> set:
    return {e.message.strip() for e in entries}


def compare_entries(
    entries_a: List[LogEntry],
    entries_b: List[LogEntry],
    label_a: str = "A",
    label_b: str = "B",
    opts: Optional[CompareOptions] = None,
) -> CompareResult:
    if opts is not None:
        entries_a = apply_filters(
            entries_a,
            level=opts.level,
            pattern=opts.pattern,
            exclude=opts.exclude,
        )
        entries_b = apply_filters(
            entries_b,
            level=opts.level,
            pattern=opts.pattern,
            exclude=opts.exclude,
        )

    msgs_a = _message_set(entries_a)
    msgs_b = _message_set(entries_b)

    common = sorted(msgs_a & msgs_b)
    only_a = [e for e in entries_a if e.message.strip() not in msgs_b]
    only_b = [e for e in entries_b if e.message.strip() not in msgs_a]

    return CompareResult(
        label_a=label_a,
        label_b=label_b,
        entries_a=list(entries_a),
        entries_b=list(entries_b),
        only_in_a=only_a,
        only_in_b=only_b,
        common_messages=common,
    )


def compare_summary(result: CompareResult) -> str:
    lines = [
        f"Compare: {result.label_a} vs {result.label_b}",
        f"  {result.label_a}: {result.total_a} entries",
        f"  {result.label_b}: {result.total_b} entries",
        f"  Only in {result.label_a}: {len(result.only_in_a)}",
        f"  Only in {result.label_b}: {len(result.only_in_b)}",
        f"  Common messages: {result.overlap_count}",
    ]
    return "\n".join(lines)
