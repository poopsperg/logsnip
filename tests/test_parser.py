"""Tests for logsnip.parser."""

import tempfile
import os
from datetime import datetime

import pytest

from logsnip.parser import iter_entries, filter_by_range, LogEntry


SAMPLE_LINES = [
    "2024-01-10 08:00:00 INFO  server started\n",
    "2024-01-10 09:15:30 DEBUG request received\n",
    "2024-01-10 10:45:00 ERROR something broke\n",
    "no timestamp here, just noise\n",
    "2024-01-10T11:00:00 WARN  disk usage high\n",
]


@pytest.fixture()
def sample_log(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text("".join(SAMPLE_LINES))
    return str(log_file)


def test_iter_entries_count(sample_log):
    entries = list(iter_entries(sample_log))
    assert len(entries) == 4  # 4 lines have timestamps


def test_iter_entries_line_numbers(sample_log):
    entries = list(iter_entries(sample_log))
    assert entries[0].line_number == 1
    assert entries[3].line_number == 5


def test_iter_entries_timestamps(sample_log):
    entries = list(iter_entries(sample_log))
    assert entries[0].timestamp == datetime(2024, 1, 10, 8, 0, 0)
    assert entries[2].timestamp == datetime(2024, 1, 10, 10, 45, 0)


def test_filter_by_range_start_only(sample_log):
    entries = iter_entries(sample_log)
    start = datetime(2024, 1, 10, 9, 0, 0)
    result = list(filter_by_range(entries, start=start, end=None))
    assert len(result) == 3
    assert all(e.timestamp >= start for e in result)


def test_filter_by_range_both_bounds(sample_log):
    entries = iter_entries(sample_log)
    start = datetime(2024, 1, 10, 9, 0, 0)
    end = datetime(2024, 1, 10, 10, 59, 59)
    result = list(filter_by_range(entries, start=start, end=end))
    assert len(result) == 2


def test_filter_by_range_no_bounds(sample_log):
    entries = list(iter_entries(sample_log))
    result = list(filter_by_range(iter(entries), start=None, end=None))
    assert len(result) == 4
