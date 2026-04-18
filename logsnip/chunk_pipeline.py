"""High-level pipeline step: chunk filtered entries and format them."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import List, Optional

from logsnip.chunk_formatter import format_chunks
from logsnip.chunker import Chunk, chunk_by_size, chunk_by_time
from logsnip.parser import LogEntry


@dataclass
class ChunkOptions:
    mode: str = "size"          # "size" | "time"
    size: int = 100
    window_minutes: int = 10
    fmt: str = "text"           # "text" | "json" | "summary"
    max_chunks: Optional[int] = None


def build_chunks(entries: List[LogEntry], opts: ChunkOptions) -> List[Chunk]:
    """Produce chunks from entries according to ChunkOptions."""
    if opts.mode == "time":
        window = timedelta(minutes=opts.window_minutes)
        chunks = list(chunk_by_time(entries, window))
    else:
        chunks = list(chunk_by_size(entries, opts.size))

    if opts.max_chunks is not None:
        chunks = chunks[: opts.max_chunks]

    return chunks


def run_chunk_pipeline(entries: List[LogEntry], opts: ChunkOptions) -> str:
    """Build chunks and return formatted output string."""
    chunks = build_chunks(entries, opts)
    if not chunks:
        return "No chunks produced."
    return format_chunks(chunks, fmt=opts.fmt)


def chunk_stats(chunks: List[Chunk]) -> dict:
    """Return basic statistics about a list of chunks."""
    if not chunks:
        return {"total_chunks": 0, "total_entries": 0, "avg_chunk_size": 0.0}
    total = sum(c.size for c in chunks)
    return {
        "total_chunks": len(chunks),
        "total_entries": total,
        "avg_chunk_size": round(total / len(chunks), 2),
    }
