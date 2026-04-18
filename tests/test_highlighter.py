"""Tests for logsnip.highlighter module."""

import pytest
from logsnip.highlighter import (
    colorize_level,
    highlight_pattern,
    highlight_line,
    strip_ansi,
    LEVEL_COLORS,
    ANSI_RESET,
)


def test_colorize_level_known():
    result = colorize_level("ERROR", "something bad")
    assert "something bad" in result
    assert LEVEL_COLORS["ERROR"] in result
    assert ANSI_RESET in result


def test_colorize_level_unknown():
    result = colorize_level("TRACE", "some message")
    assert result == "some message"


def test_colorize_level_case_insensitive():
    result = colorize_level("error", "msg")
    assert LEVEL_COLORS["ERROR"] in result


def test_highlight_pattern_found():
    result = highlight_pattern("hello world", "world")
    assert "world" in result
    assert "\033[" in result


def test_highlight_pattern_not_found():
    result = highlight_pattern("hello world", "missing")
    assert result == "hello world"


def test_highlight_pattern_empty():
    result = highlight_pattern("hello", "")
    assert result == "hello"


def test_highlight_line_both():
    result = highlight_line("ERROR: disk full", level="ERROR", pattern="disk")
    clean = strip_ansi(result)
    assert "ERROR: disk full" in clean


def test_highlight_line_no_args():
    result = highlight_line("plain line")
    assert result == "plain line"


def test_strip_ansi():
    colored = "\033[31mred text\033[0m"
    assert strip_ansi(colored) == "red text"


def test_strip_ansi_no_codes():
    assert strip_ansi("plain") == "plain"
