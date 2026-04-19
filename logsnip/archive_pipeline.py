from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from logsnip.parser import LogEntry
from logsnip.filter import apply_filters
from logsnip.archiver import Archive, ArchiveOptions, create_archive, serialize_archive


@dataclass
class ArchivePipelineOptions:
    compress: bool = True
    label: str = ""
    level: Optional[str] = None
    pattern: Optional[str] = None
    exclude: Optional[str] = None


def run_archive_pipeline(
    entries: List[LogEntry],
    options: ArchivePipelineOptions,
) -> Archive:
    filtered = apply_filters(
        entries,
        level=options.level,
        pattern=options.pattern,
        exclude=options.exclude,
    )
    opts = ArchiveOptions(
        compress=options.compress,
        label=options.label,
    )
    return create_archive(filtered, opts)


def archive_to_bytes(archive: Archive) -> bytes:
    return serialize_archive(archive)
