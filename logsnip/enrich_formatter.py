from __future__ import annotations

import json
from typing import List

from logsnip.enricher import EnrichedEntry


def _ts_str(entry: EnrichedEntry) -> str:
    ts = entry.timestamp
    return ts.isoformat() if ts else "n/a"


def format_enrich_text(enriched: List[EnrichedEntry]) -> str:
    lines = []
    for e in enriched:
        extras_str = ", ".join(f"{k}={v}" for k, v in e.extras.items())
        base = f"[{_ts_str(e)}] {e.level}: {e.message}"
        if extras_str:
            base += f" | {extras_str}"
        lines.append(base)
    return "\n".join(lines)


def format_enrich_json(enriched: List[EnrichedEntry]) -> str:
    records = [
        {
            "timestamp": _ts_str(e),
            "level": e.level,
            "message": e.message,
            "extras": e.extras,
        }
        for e in enriched
    ]
    return json.dumps(records, indent=2)


def format_enrich_jsonl(enriched: List[EnrichedEntry]) -> str:
    lines = []
    for e in enriched:
        record = {
            "timestamp": _ts_str(e),
            "level": e.level,
            "message": e.message,
            "extras": e.extras,
        }
        lines.append(json.dumps(record))
    return "\n".join(lines)


SUPPORTED_FORMATS = ("text", "json", "jsonl")


def format_enrich_entries(enriched: List[EnrichedEntry], fmt: str = "text") -> str:
    if fmt == "json":
        return format_enrich_json(enriched)
    if fmt == "jsonl":
        return format_enrich_jsonl(enriched)
    return format_enrich_text(enriched)
