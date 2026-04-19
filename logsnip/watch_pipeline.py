"""High-level pipeline for the watch feature."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from logsnip.parser import LogEntry
from logsnip.watchdog import WatchOptions, watch_file


@dataclass
class WatchPipelineOptions:
    path: Path
    level: list[str] = field(default_factory=list)
    pattern: str | None = None
    exclude: str | None = None
    poll_interval: float = 0.5
    max_idle: float | None = None
    limit: int | None = None


def run_watch_pipeline(
    options: WatchPipelineOptions,
    callback: Callable[[LogEntry], None] | None = None,
) -> list[LogEntry]:
    watch_opts = WatchOptions(
        level=options.level,
        pattern=options.pattern,
        exclude=options.exclude,
        poll_interval=options.poll_interval,
        max_idle=options.max_idle,
    )
    collected: list[LogEntry] = []
    for entry in watch_file(options.path, watch_opts, callback=callback):
        collected.append(entry)
        if options.limit is not None and len(collected) >= options.limit:
            break
    return collected


def watch_pipeline_summary(entries: list[LogEntry]) -> str:
    from logsnip.watchdog import watch_summary
    s = watch_summary(entries)
    level_str = ", ".join(f"{k}={v}" for k, v in s["levels"].items())
    return f"watched {s['total']} entries [{level_str}]"
