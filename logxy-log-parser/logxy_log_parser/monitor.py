"""
Monitor functionality for logxy-log-parser.

Contains LogFile for handling and monitoring log files with real-time updates.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

from .core import LogEntry, LogParser


class LogFileError(Exception):
    """Exception raised for invalid log files."""


class LogFile:
    """Handle and monitor a log file with real-time updates."""

    def __init__(self, path: str | Path):
        """Open and validate a log file.

        Args:
            path: Path to the log file.

        Raises:
            LogFileError: If file doesn't exist or is invalid.
        """
        self._path = Path(path)
        self._size: int = 0
        self._line_count: int = 0
        self._entry_count: int = 0
        self._last_position: int = 0

        if not self._path.exists():
            raise LogFileError(f"File not found: {path}")

        self._refresh_file_state()
        self._validate()

    @classmethod
    def open(cls, path: str | Path) -> LogFile | None:
        """Open a log file, return None if file doesn't exist or is invalid.

        Args:
            path: Path to the log file.

        Returns:
            LogFile | None: LogFile instance or None if invalid.
        """
        try:
            return cls(path)
        except LogFileError:
            return None

    def _refresh_file_state(self) -> None:
        """Refresh internal file state."""
        self._size = self._path.stat().st_size

        # Count lines
        with open(self._path, encoding="utf-8") as f:
            self._line_count = sum(1 for _ in f)

        # Count valid entries
        self._entry_count = 0
        with open(self._path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        json.loads(line)
                        self._entry_count += 1
                    except (json.JSONDecodeError, ValueError):
                        pass

    def _validate(self) -> None:
        """Validate that this is a valid LogXPy log file."""
        if self._entry_count == 0:
            raise LogFileError(f"No valid log entries found in: {self._path}")

    @property
    def path(self) -> Path:
        """Get the file path."""
        return self._path

    @property
    def is_valid(self) -> bool:
        """Check if file is a valid LogXPy log file."""
        return self._entry_count > 0

    @property
    def size(self) -> int:
        """Get current file size in bytes."""
        return self._size

    @property
    def line_count(self) -> int:
        """Get current number of lines in the file."""
        return self._line_count

    @property
    def entry_count(self) -> int:
        """Get current number of valid log entries."""
        return self._entry_count

    def refresh(self) -> int:
        """Refresh the file state and return new entry count.

        Returns:
            int: Updated entry count.
        """
        self._refresh_file_state()
        return self._entry_count

    def _parse_criteria(self, **criteria: Any) -> Callable[[LogEntry], bool]:
        """Parse criteria into a predicate function.

        Args:
            **criteria: Filter criteria.

        Returns:
            Callable[[LogEntry], bool]: Predicate function.
        """
        def predicate(entry: LogEntry) -> bool:
            for key, value in criteria.items():
                # Handle special operators
                if "__" in key:
                    field_name, operator = key.rsplit("__", 1)
                    field_value = entry.get(field_name)

                    match operator:
                        case "contains":
                            if isinstance(field_value, str) and isinstance(value, str):
                                if value.lower() not in field_value.lower():
                                    return False
                            elif field_value != value:
                                return False
                        case "gt":
                            if not (isinstance(field_value, (int, float)) and field_value > value):
                                return False
                        case "lt":
                            if not (isinstance(field_value, (int, float)) and field_value < value):
                                return False
                        case "gte":
                            if not (isinstance(field_value, (int, float)) and field_value >= value):
                                return False
                        case "lte":
                            if not (isinstance(field_value, (int, float)) and field_value <= value):
                                return False
                        case _:
                            return False
                else:
                    # Direct field comparison
                    if entry.get(key) != value:
                        return False
            return True

        return predicate

    def contains(self, **criteria: Any) -> bool:
        """Check if log file contains entries matching criteria.

        Args:
            **criteria: Filter criteria (e.g., message="error", level="error").

        Returns:
            bool: True if matching entry found.
        """
        predicate = self._parse_criteria(**criteria)

        with open(self._path, encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = LogEntry.from_dict(data, line_number)
                    if predicate(entry):
                        return True
                except (json.JSONDecodeError, ValueError, KeyError):
                    continue
        return False

    def contains_message(self, text: str, regex: bool = False) -> bool:
        """Check if file contains a specific message text.

        Args:
            text: Message text to search for.
            regex: Use regex matching if True.

        Returns:
            bool: True if message found.
        """
        import re

        pattern = re.compile(text, re.IGNORECASE) if regex else None

        with open(self._path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    message = data.get("message", "")
                    if message:
                        if regex:
                            if pattern and pattern.search(message):
                                return True
                        else:
                            if text.lower() in message.lower():
                                return True
                except (json.JSONDecodeError, ValueError):
                    continue
        return False

    def contains_error(self) -> bool:
        """Check if file contains any error level logs.

        Returns:
            bool: True if error found.
        """
        return self.contains(level="error")

    def contains_level(self, level: str) -> bool:
        """Check if file has specific log level.

        Args:
            level: Log level to check.

        Returns:
            bool: True if level found.
        """
        return self.contains(level=level)

    def find_first(self, **criteria: Any) -> LogEntry | None:
        """Find first entry matching criteria.

        Args:
            **criteria: Filter criteria.

        Returns:
            LogEntry | None: First matching entry or None.
        """
        predicate = self._parse_criteria(**criteria)

        with open(self._path, encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = LogEntry.from_dict(data, line_number)
                    if predicate(entry):
                        return entry
                except (json.JSONDecodeError, ValueError, KeyError):
                    continue
        return None

    def find_last(self, **criteria: Any) -> LogEntry | None:
        """Find last entry matching criteria.

        Args:
            **criteria: Filter criteria.

        Returns:
            LogEntry | None: Last matching entry or None.
        """
        predicate = self._parse_criteria(**criteria)

        last_entry: LogEntry | None = None

        with open(self._path, encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = LogEntry.from_dict(data, line_number)
                    if predicate(entry):
                        last_entry = entry
                except (json.JSONDecodeError, ValueError, KeyError):
                    continue

        return last_entry

    def find_all(self, **criteria: Any) -> list[LogEntry]:
        """Find all entries matching criteria.

        Args:
            **criteria: Filter criteria.

        Returns:
            list[LogEntry]: List of matching entries.
        """
        predicate = self._parse_criteria(**criteria)
        matches: list[LogEntry] = []

        with open(self._path, encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = LogEntry.from_dict(data, line_number)
                    if predicate(entry):
                        matches.append(entry)
                except (json.JSONDecodeError, ValueError, KeyError):
                    continue

        return matches

    def tail(self, n: int = 10) -> list[LogEntry]:
        """Get last n entries from the file.

        Args:
            n: Number of entries to return.

        Returns:
            list[LogEntry]: Last n entries.
        """
        entries: list[LogEntry] = []

        with open(self._path, encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entries.append(LogEntry.from_dict(data, line_number))
                    if len(entries) > n:
                        entries.pop(0)
                except (json.JSONDecodeError, ValueError, KeyError):
                    continue

        return entries

    def follow(
        self,
        callback: Callable[[LogEntry], None],
        interval: float = 0.1,
        filter_func: Callable[[LogEntry], bool] | None = None,
    ) -> None:
        """Monitor file for new entries and call callback for each new log.

        Blocks until interrupted or file is closed.

        Args:
            callback: Function to call for each new entry.
            interval: Polling interval in seconds.
            filter_func: Optional filter function. Only entries matching filter trigger callback.
        """
        self._last_position = self._size

        try:
            while True:
                self.refresh()
                if self._size > self._last_position:
                    # Read new lines - count from beginning to get accurate line numbers
                    line_number = 0
                    with open(self._path, encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            line_number += 1
                            # Only process lines after our last position
                            if f.tell() <= self._last_position:
                                continue
                            try:
                                data = json.loads(line)
                                entry = LogEntry.from_dict(data, line_number)
                                if filter_func is None or filter_func(entry):
                                    callback(entry)
                            except (json.JSONDecodeError, ValueError, KeyError):
                                continue
                    self._last_position = self._size
                time.sleep(interval)
        except KeyboardInterrupt:
            pass

    def watch(
        self,
        interval: float = 0.1,
        filter_func: Callable[[LogEntry], bool] | None = None,
    ) -> Iterator[LogEntry]:
        """Yield new entries as they are written to the file.

        Args:
            interval: Polling interval in seconds.
            filter_func: Optional filter function. Only matching entries are yielded.

        Yields:
            LogEntry: New log entries as they appear.
        """
        self._last_position = self._size

        try:
            while True:
                self.refresh()
                if self._size > self._last_position:
                    # Read new lines - count from beginning to get accurate line numbers
                    line_number = 0
                    with open(self._path, encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            line_number += 1
                            # Only process lines after our last position
                            if f.tell() <= self._last_position:
                                continue
                            try:
                                data = json.loads(line)
                                entry = LogEntry.from_dict(data, line_number)
                                if filter_func is None or filter_func(entry):
                                    yield entry
                            except (json.JSONDecodeError, ValueError, KeyError):
                                continue
                    self._last_position = self._size
                time.sleep(interval)
        except KeyboardInterrupt:
            pass

    def watch_filtered(
        self,
        level: str | None = None,
        message: str | None = None,
        task_uuid: str | None = None,
        interval: float = 0.1,
    ) -> Iterator[LogEntry]:
        """Watch file with built-in filters.

        Args:
            level: Filter by log level.
            message: Filter by message content (substring match).
            task_uuid: Filter by task UUID.
            interval: Polling interval in seconds.

        Yields:
            LogEntry: Matching new log entries.
        """
        def filter_func(entry: LogEntry) -> bool:
            if level and entry.level.value != level.lower():
                return False
            if message and entry.message and message.lower() not in entry.message.lower():
                return False
            if task_uuid and entry.task_uuid != task_uuid:
                return False
            return True

        yield from self.watch(interval=interval, filter_func=filter_func)

    def wait_for(self, **criteria: Any) -> LogEntry | None:
        """Wait for an entry matching criteria to appear.

        Returns:
            LogEntry | None: Matching entry or None if timeout.

        Note:
            This method waits indefinitely. Use wait_for_message or wait_for_error
            with timeout for time-limited waits.
        """
        predicate = self._parse_criteria(**criteria)
        self._last_position = self._size

        try:
            while True:
                self.refresh()
                if self._size > self._last_position:
                    # Count from beginning to get accurate line numbers
                    line_number = 0
                    with open(self._path, encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            line_number += 1
                            # Only process lines after our last position
                            if f.tell() <= self._last_position:
                                continue
                            try:
                                data = json.loads(line)
                                entry = LogEntry.from_dict(data, line_number)
                                if predicate(entry):
                                    return entry
                            except (json.JSONDecodeError, ValueError, KeyError):
                                continue
                    self._last_position = self._size
                time.sleep(0.1)
        except KeyboardInterrupt:
            return None

    def wait_for_message(self, text: str, timeout: float = 30.0) -> LogEntry | None:
        """Wait for a specific message to appear.

        Args:
            text: Message text to wait for.
            timeout: Maximum wait time in seconds.

        Returns:
            LogEntry | None: Entry with matching message or None.
        """
        start_time = time.time()

        try:
            while time.time() - start_time < timeout:
                entry = self.find_first(message=text)
                if entry:
                    return entry
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass

        return None

    def wait_for_error(self, _timeout: float = 30.0) -> LogEntry | None:
        """Wait for an error to appear.

        Args:
            timeout: Maximum wait time in seconds.

        Returns:
            LogEntry | None: First error entry or None.
        """
        return self.wait_for(level="error")

    def get_parser(self) -> LogParser:
        """Get a LogParser for this file.

        Returns:
            LogParser: Parser instance for this file.
        """
        return LogParser(self._path)

    def to_entries(self) -> list[LogEntry]:
        """Load all entries as LogEntries collection.

        Returns:
            list[LogEntry]: All log entries.
        """
        return self.get_parser().parse()
