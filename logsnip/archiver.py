from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import json
import gzip
import io

from logsnip.parser import LogEntry


@dataclass
class ArchiveOptions:
    compress: bool = True
    label: str = ""
    include_meta: bool = True


@dataclass
class Archive:
    label: str
    created_at: datetime
    entries: List[LogEntry]
    compressed: bool

    @property
    def count(self) -> int:
        return len(self.entries)

    @property
    def start(self) -> Optional[datetime]:
        return self.entries[0].timestamp if self.entries else None

    @property
    def end(self) -> Optional[datetime]:
        return self.entries[-1].timestamp if self.entries else None


def create_archive(entries: List[LogEntry], options: ArchiveOptions) -> Archive:
    return Archive(
        label=options.label or "archive",
        created_at=datetime.utcnow(),
        entries=list(entries),
        compressed=options.compress,
    )


def serialize_archive(archive: Archive) -> bytes:
    rows = [
        {"timestamp": e.timestamp.isoformat(), "level": e.level, "message": e.message, "line": e.line_number}
        for e in archive.entries
    ]
    meta = {
        "label": archive.label,
        "created_at": archive.created_at.isoformat(),
        "count": archive.count,
        "entries": rows,
    }
    raw = json.dumps(meta, indent=2).encode()
    if archive.compressed:
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            gz.write(raw)
        return buf.getvalue()
    return raw


def deserialize_archive(data: bytes, compressed: bool = True) -> Archive:
    if compressed:
        try:
            buf = io.BytesIO(data)
            with gzip.GzipFile(fileobj=buf, mode="rb") as gz:
                raw = gz.read()
        except (OSError, EOFError) as e:
            raise ValueError(f"Failed to decompress archive data: {e}") from e
    else:
        raw = data
    try:
        meta = json.loads(raw.decode())
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"Failed to parse archive JSON: {e}") from e
    entries = [
        LogEntry(timestamp=datetime.fromisoformat(r["timestamp"]), level=r["level"], message=r["message"], line_number=r["line"])
        for r in meta["entries"]
    ]
    return Archive(
        label=meta["label"],
        created_at=datetime.fromisoformat(meta["created_at"]),
        entries=entries,
        compressed=compressed,
    )


def archive_summary(archive: Archive) -> str:
    return (
        f"Archive '{archive.label}': {archive.count} entries"
        f" | {archive.start} -> {archive.end}"
        f" | compressed={archive.compressed}"
    )
