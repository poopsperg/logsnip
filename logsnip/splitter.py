"""Split log entries into named segments based on marker patterns."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import re
from logsnip.parser import LogEntry


@dataclass
class Segment:
    name: str
    entries: List[LogEntry] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.entries)

    @property
    def start(self) -> Optional[LogEntry]:
        return self.entries[0] if self.entries else None

    @property
    def end(self) -> Optional[LogEntry]:
        return self.entries[-1] if self.entries else None


@dataclass
class SplitOptions:
    markers: List[str]
    default_segment: str = "default"
    include_marker_line: bool = True


def split_entries(entries: List[LogEntry], options: SplitOptions) -> List[Segment]:
    """Split entries into segments whenever a marker pattern is matched."""
    patterns = [re.compile(m) for m in options.markers]
    segments: List[Segment] = []
    current = Segment(name=options.default_segment)

    for entry in entries:
        matched = False
        for i, pat in enumerate(patterns):
            if pat.search(entry.message):
                if current.entries:
                    segments.append(current)
                seg_name = f"segment_{len(segments) + 1}"
                current = Segment(name=seg_name)
                if options.include_marker_line:
                    current.entries.append(entry)
                matched = True
                break
        if not matched:
            current.entries.append(entry)

    if current.entries:
        segments.append(current)

    return segments


def split_summary(segments: List[Segment]) -> dict:
    return {
        "total_segments": len(segments),
        "total_entries": sum(s.size for s in segments),
        "segments": [{"name": s.name, "size": s.size} for s in segments],
    }
