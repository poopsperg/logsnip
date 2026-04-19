from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from logsnip.parser import LogEntry


@dataclass
class TrimOptions:
    head: Optional[int] = None
    tail: Optional[int] = None
    drop_duplicates: bool = False


def trim_head(entries: List[LogEntry], n: int) -> List[LogEntry]:
    if n < 0:
        raise ValueError("head must be >= 0")
    return entries[:n]


def trim_tail(entries: List[LogEntry], n: int) -> List[LogEntry]:
    if n < 0:
        raise ValueError("tail must be >= 0")
    return entries[-n:] if n > 0 else []


def trim_entries(entries: List[LogEntry], options: TrimOptions) -> List[LogEntry]:
    result = list(entries)

    if options.drop_duplicates:
        seen: set = set()
        deduped = []
        for e in result:
            key = (e.level, e.message)
            if key not in seen:
                seen.add(key)
                deduped.append(e)
        result = deduped

    if options.head is not None and options.tail is not None:
        result = trim_head(result, options.head + options.tail)
        head_part = result[:options.head]
        tail_part = result[options.head:]
        tail_part = trim_tail(tail_part, options.tail)
        result = head_part + tail_part
    elif options.head is not None:
        result = trim_head(result, options.head)
    elif options.tail is not None:
        result = trim_tail(result, options.tail)

    return result


def trim_summary(original: List[LogEntry], trimmed: List[LogEntry]) -> dict:
    return {
        "original_count": len(original),
        "trimmed_count": len(trimmed),
        "removed": len(original) - len(trimmed),
    }
