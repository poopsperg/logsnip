"""Command-line interface for logsnip."""

import sys
import argparse
from datetime import datetime
from pathlib import Path

from logsnip.parser import iter_entries, filter_by_range


DATETIME_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M",
    "%Y-%_arg(value: str) -> datetime:
    " parsing a datetime string using several common formats."""
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(
        f"Cannot parse datetime: '{value}'. "
        "Expected formats like '2024-01-15T13:00:00' or '2024-01-15 13:00'."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logsnip",
        description="Extract and filter structured log chunks from large files.",
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Path to the log file to read.",
    )
    parser.add_argument(
        "--start",
        metavar="DATETIME",
        type=parse_datetime_arg,
        default=None,
        help="Include entries at or after this timestamp.",
    )
    parser.add_argument(
        "--end",
        metavar="DATETIME",
        type=parse_datetime_arg,
        default=None,
        help="Include entries before or at this timestamp.",
    )
    parser.add_argument(
        "--pattern",
        metavar="REGEX",
        default=None,
        help="Only include entries whose message matches this regex pattern.",
    )
    parser.add_argument(
        "--show-line-numbers",
        action="store_true",
        help="Prefix each entry with its line number in the source file.",
    )
    return parser


def run(argv=None):
    """Main entry point for the CLI."""
    import re

    args = build_parser().parse_args(argv)

    if not args.file.exists():
        print(f"logsnip: error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    compiled_pattern = None
    if args.pattern:
        try:
            compiled_pattern = re.compile(args.pattern)
        except re.error as exc:
            print(f"logsnip: error: invalid pattern: {exc}", file=sys.stderr)
            sys.exit(1)

    try:
        with args.file.open("r", encoding="utf-8", errors="replace") as fh:
            entries = iter_entries(fh)
            entries = filter_by_range(entries, start=args.start, end=args.end)

            count = 0
            for entry in entries:
                if compiled_pattern and not compiled_pattern.search(entry.message):
                    continue
                if args.show_line_numbers:
                    print(f"[line {entry.line_number}] {entry.raw}", end="")
                else:
                    print(entry.raw, end="")
                count += 1

    except OSError as exc:
        print(f"logsnip: error: {exc}", file=sys.stderr)
        sys.exit(1)

    if count == 0:
        print("logsnip: no matching entries found.", file=sys.stderr)


if __name__ == "__main__":
    run()
