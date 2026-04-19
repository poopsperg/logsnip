from dataclasses import dataclass, field
from typing import Callable, List, Optional
from logsnip.parser import LogEntry


@dataclass
class TransformOptions:
    uppercase_level: bool = False
    truncate_message: Optional[int] = None
    add_prefix: Optional[str] = None
    strip_fields: List[str] = field(default_factory=list)
    custom: Optional[Callable[[LogEntry], LogEntry]] = None


def transform_entry(entry: LogEntry, opts: TransformOptions) -> LogEntry:
    level = entry.level
    message = entry.message
    extra = dict(entry.extra) if entry.extra else {}

    if opts.uppercase_level and level:
        level = level.upper()

    if opts.truncate_message and len(message) > opts.truncate_message:
        message = message[: opts.truncate_message] + "..."

    if opts.add_prefix:
        message = f"{opts.add_prefix}{message}"

    for key in opts.strip_fields:
        extra.pop(key, None)

    result = LogEntry(
        timestamp=entry.timestamp,
        level=level,
        message=message,
        raw=entry.raw,
        line_number=entry.line_number,
        extra=extra,
    )

    if opts.custom:
        result = opts.custom(result)

    return result


def transform_entries(
    entries: List[LogEntry], opts: TransformOptions
) -> List[LogEntry]:
    return [transform_entry(e, opts) for e in entries]
