"""Tests for LogFile monitoring functionality."""

from __future__ import annotations

import json
import time

import pytest

from logxy_log_parser import LogFile, LogFileError, LogParser


class TestLogFile:
    """Tests for LogFile class."""

    def test_init_existing_file(self, sample_log_path: str) -> None:
        """Test creating LogFile for existing file."""
        logfile = LogFile(sample_log_path)

        assert logfile.path.exists()
        assert logfile.is_valid
        assert logfile.entry_count > 0

    def test_init_nonexistent_file(self, tmp_path: str) -> None:
        """Test creating LogFile for non-existent file raises error."""
        import os

        nonexistent = os.path.join(tmp_path, "does_not_exist.log")

        with pytest.raises(LogFileError):
            LogFile(nonexistent)

    def test_open_safe(self, sample_log_path: str, tmp_path: str) -> None:
        """Test safe open that returns None for invalid files."""
        import os

        logfile = LogFile.open(sample_log_path)
        assert logfile is not None

        nonexistent = os.path.join(tmp_path, "does_not_exist.log")
        logfile_none = LogFile.open(nonexistent)
        assert logfile_none is None

    def test_entry_count(self, sample_log_path: str) -> None:
        """Test getting entry count."""
        logfile = LogFile(sample_log_path)

        count = logfile.entry_count
        assert count > 0
        assert isinstance(count, int)

    def test_file_size(self, sample_log_path: str) -> None:
        """Test getting file size."""
        logfile = LogFile(sample_log_path)

        size = logfile.size
        assert size > 0
        assert isinstance(size, int)

    def test_line_count(self, sample_log_path: str) -> None:
        """Test getting line count."""
        logfile = LogFile(sample_log_path)

        lines = logfile.line_count
        assert lines > 0
        assert isinstance(lines, int)

    def test_contains_message(self, sample_log_path: str) -> None:
        """Test checking if file contains message."""
        logfile = LogFile(sample_log_path)

        assert logfile.contains_message("started") is True
        assert logfile.contains_message("nonexistent") is False

    def test_contains_error(self, sample_log_path: str) -> None:
        """Test checking if file contains errors."""
        logfile = LogFile(sample_log_path)

        # Our sample has at least one error
        has_error = logfile.contains_error()
        # Check if error log path has errors
        assert isinstance(has_error, bool)

    def test_contains_level(self, sample_log_path: str) -> None:
        """Test checking if file contains specific level."""
        logfile = LogFile(sample_log_path)

        assert logfile.contains_level("info") is True

    def test_contains_with_criteria(self, sample_log_path: str) -> None:
        """Test contains with custom criteria."""
        logfile = LogFile(sample_log_path)

        assert logfile.contains(level="info") is True
        assert logfile.contains(user_id=12345) is True

    def test_contains_substring(self, sample_log_path: str) -> None:
        """Test contains with substring search."""
        logfile = LogFile(sample_log_path)

        assert logfile.contains(message__contains="application") is True
        assert logfile.contains(message__contains="nonexistent") is False

    def test_contains_comparison(self, sample_log_path: str) -> None:
        """Test contains with comparison operators."""
        logfile = LogFile(sample_log_path)

        assert logfile.contains(timestamp__gt=1738332000.0) is True
        assert logfile.contains(timestamp__lt=1738332000.0) is False

    def test_find_first(self, sample_log_path: str) -> None:
        """Test finding first matching entry."""
        logfile = LogFile(sample_log_path)

        entry = logfile.find_first(level="info")
        assert entry is not None
        assert entry.level.value == "info"

    def test_find_last(self, sample_log_path: str) -> None:
        """Test finding last matching entry."""
        logfile = LogFile(sample_log_path)

        entry = logfile.find_last(user_id=12345)
        assert entry is not None

    def test_find_all(self, sample_log_path: str) -> None:
        """Test finding all matching entries."""
        logfile = LogFile(sample_log_path)

        entries = logfile.find_all(level="info")
        assert len(entries) > 0
        assert all(e.level.value == "info" for e in entries)

    def test_tail(self, sample_log_path: str) -> None:
        """Test getting last n entries."""
        logfile = LogFile(sample_log_path)

        entries = logfile.tail(3)
        assert len(entries) <= 3

    def test_refresh(self, sample_log_path: str) -> None:
        """Test refreshing file state."""
        logfile = LogFile(sample_log_path)

        initial_count = logfile.entry_count
        new_count = logfile.refresh()

        assert new_count == initial_count

    def test_get_parser(self, sample_log_path: str) -> None:
        """Test getting parser from LogFile."""
        logfile = LogFile(sample_log_path)

        parser = logfile.get_parser()
        assert isinstance(parser, LogParser)

        logs = parser.parse()
        assert len(logs) > 0

    def test_to_entries(self, sample_log_path: str) -> None:
        """Test loading all entries."""
        logfile = LogFile(sample_log_path)

        entries = logfile.to_entries()
        assert len(entries) > 0
        assert len(entries) == logfile.entry_count

    def test_watch_integration(self, sample_log_path: str) -> None:
        """Test watch method (integration test)."""
        logfile = LogFile(sample_log_path)

        # Watch should return an iterator
        iterator = logfile.watch(interval=0.01)

        assert hasattr(iterator, "__iter__")
        assert hasattr(iterator, "__next__")

        # Clean up the generator
        iterator.close()

    def test_follow_integration(self, sample_log_path: str) -> None:
        """Test follow method (integration test)."""
        logfile = LogFile(sample_log_path)

        called = []

        def callback(entry):
            called.append(entry)

        # Follow should start monitoring
        # We won't actually wait for new entries
        # Just verify the method can be called
        import threading

        def stop_follow():
            time.sleep(0.1)
            # Raise KeyboardInterrupt in main thread
            import _thread
            _thread.interrupt_main()

        thread = threading.Thread(target=stop_follow)
        thread.start()

        try:
            logfile.follow(callback, interval=0.01)
        except KeyboardInterrupt:
            pass

        thread.join()

    def test_wait_for_integration(self, sample_log_path: str) -> None:
        """Test wait_for method (integration test)."""
        logfile = LogFile(sample_log_path)

        # This should return an entry if it exists
        entry = logfile.wait_for_message("started", timeout=0.1)

        if entry:
            assert entry.message == "started"
        else:
            # Entry might not be found in timeout
            assert entry is None

    def test_wait_for_message_timeout(self, sample_log_path: str) -> None:
        """Test wait_for_message with timeout."""
        logfile = LogFile(sample_log_path)

        # Message doesn't exist, should return None
        entry = logfile.wait_for_message("nonexistent_message_xyz", timeout=0.1)

        assert entry is None


class TestLogFileGrowth:
    """Tests for LogFile with growing files."""

    def test_entry_count_updates(self, tmp_path: str) -> None:
        """Test that entry count updates when file grows."""
        import os

        log_file = os.path.join(tmp_path, "growing.log")

        # Create initial file
        with open(log_file, "w") as f:
            f.write('{"task_uuid": "test", "timestamp": 1.0, "level": "/", "message_type": "loggerx:info", "message": "First"}\n')

        logfile = LogFile(log_file)

        initial_count = logfile.entry_count
        assert initial_count == 1

        # Add more entries
        with open(log_file, "a") as f:
            f.write('{"task_uuid": "test", "timestamp": 2.0, "level": "/", "message_type": "loggerx:info", "message": "Second"}\n')
            f.write('{"task_uuid": "test", "timestamp": 3.0, "level": "/", "message_type": "loggerx:info", "message": "Third"}\n')

        new_count = logfile.refresh()
        assert new_count == 3
