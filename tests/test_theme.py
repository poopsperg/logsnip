"""Tests for logsnip.theme module."""

import pytest
from logsnip.theme import get_theme, DEFAULT_THEME, NO_COLOR_THEME, Theme


def test_default_theme_enabled():
    assert DEFAULT_THEME.enabled is True


def test_no_color_theme_disabled():
    assert NO_COLOR_THEME.enabled is False


def test_get_theme_default():
    theme = get_theme(no_color=False)
    assert theme.enabled is True
    assert "ERROR" in theme.level_colors


def test_get_theme_no_color():
    theme = get_theme(no_color=True)
    assert theme.enabled is False
    assert theme.level_colors == {}


def test_theme_is_dataclass():
    t = Theme(level_colors={"INFO": "\033[32m"}, enabled=True)
    assert t.level_colors["INFO"] == "\033[32m"


def test_default_theme_has_all_levels():
    for level in ("ERROR", "WARN", "WARNING", "INFO", "DEBUG"):
        assert level in DEFAULT_THEME.level_colors
