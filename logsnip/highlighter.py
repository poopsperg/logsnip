"""Terminal color highlighting for log output."""

from __future__ import annotations

import re
from typing import Optional

ANSI_RESET = "\033[0m"

LEVEL_COLORS = {
    "ERROR": "\033[31m",    # red
    "WARN":  "\033[33m",    # yellow
    "WARNING": "\033[33m",
    "INFO":  "\033[32m",    # green
    "DEBUG": "\033[36m",   # cyan
}

PATTERN_COLOR = "\033[35m"  # magenta for matched patterns


def colorize_level(level: str, text: str) -> str:
    """Wrap text with ANSI color for the given log level."""
    color = LEVEL_COLORS.get(level.upper(), "")
    if not color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def highlight_pattern(text: str, pattern: str) -> str:
    """Highlight all occurrences of pattern in text."""
    if not pattern:
        return text
    try:
        highlighted = re.sub(
            f"({re.escape(pattern)})",
            f"{PATTERN_COLOR}\\1{ANSI_RESET}",
            text,
        )
        return highlighted
    except re.error:
        return text


def highlight_line(line: str, level: Optional[str] = None, pattern: Optional[str] = None) -> str:
    """Apply level coloring and optional pattern highlighting to a log line."""
    if level:
        line = colorize_level(level, line)
    if pattern:
        line = highlight_pattern(line, pattern)
    return line


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    ansi_escape = re.compile(r"\033\[[0-9;]*m")
    return ansi_escape.sub("", text)
