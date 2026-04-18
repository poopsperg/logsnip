"""Theme configuration for terminal highlighting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Theme:
    level_colors: Dict[str, str] = field(default_factory=dict)
    pattern_color: str = "\033[35m"
    reset: str = "\033[0m"
    enabled: bool = True


DEFAULT_THEME = Theme(
    level_colors={
        "ERROR":   "\033[31m",
        "WARN":    "\033[33m",
        "WARNING": "\033[33m",
        "INFO":    "\033[32m",
        "DEBUG":   "\033[36m",
    },
    pattern_color="\033[35m",
    enabled=True,
)

NO_COLOR_THEME = Theme(
    level_colors={},
    pattern_color="",
    enabled=False,
)


def get_theme(no_color: bool = False) -> Theme:
    """Return the appropriate theme based on user preference."""
    return NO_COLOR_THEME if no_color else DEFAULT_THEME
