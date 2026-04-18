"""Format Chunk objects for output."""
from __future__ import annotations

import json
from typing import List

from logsnip.chunker import Chunk
from logsnip.formatter import _entries_to_dicts, format_text


def format_chunk_summary(chunk: Chunk) -> str:
    """One-line summary of a chunk."""
    start = chunk.start.isoformat() if chunk.start else "?"
    end = chunk.end.isoformat() if chunk.end else "?"
    return f"[Chunk {chunk.index}] {chunk.size} entries | {start} -> {end}"


def format_chunk_text(chunk: Chunk, show_header: bool = True) -> str:
    """Render a chunk as plain text with an optional header."""
    parts: List[str] = []
    if show_header:
        parts.append(format_chunk_summary(chunk))
        parts.append("-" * 60)
    parts.append(format_text(chunk.entries))
    return "\n".join(parts)


def format_chunk_json(chunk: Chunk) -> str:
    """Render a chunk as a JSON object with metadata."""
    data = {
        "chunk_index": chunk.index,
        "size": chunk.size,
        "start": chunk.start.isoformat() if chunk.start else None,
        "end": chunk.end.isoformat() if chunk.end else None,
        "entries": _entries_to_dicts(chunk.entries),
    }
    return json.dumps(data, indent=2)


def format_chunks(chunks: List[Chunk], fmt: str = "text") -> str:
    """Format a list of chunks."""
    if fmt == "json":
        return json.dumps(
            [json.loads(format_chunk_json(c)) for c in chunks], indent=2
        )
    if fmt == "summary":
        return "\n".join(format_chunk_summary(c) for c in chunks)
    # default: text
    return "\n\n".join(format_chunk_text(c) for c in chunks)
