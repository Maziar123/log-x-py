"""
Filtering functionality for logxy-log-parser.

Contains LogEntries collection and LogFilter for chainable filtering operations.
Uses boltons for efficient grouping and iteration utilities.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable, Iterator
from datetime import datetime
from itertools import islice
from math import inf
from pathlib import Path
from typing import Any

from .core import LogEntry
from .utils import bucketize, parse_timestamp


class LogEntries:
    """Collection of log entries with filtering and aggregation methods."""

    def __init__(self, entries: list[LogEntry] | Iterator[LogEntry]):
        """Initialize with a list or iterator of LogEntry objects.

        Args:
            entries: List or iterator of LogEntry objects.
        """
        self._entries = list(entries) if not isinstance(entries, list) else entries

    def __len__(self) -> int:
        """Get the number of entries in this collection."""
        return len(self._entries)

    def __iter__(self) -> Iterator[LogEntry]:
        """Iterate over entries."""
        return iter(self._entries)

    def __getitem__(self, index: int) -> LogEntry:
        """Get entry at index."""
        return self._entries[index]

    def __repr__(self) -> str:
        """String representation."""
        return f"LogEntries(count={len(self)})"

    # Filtering methods

    def filter(self, predicate: Callable[[LogEntry], bool]) -> LogEntries:
        """Filter entries using a custom predicate function.

        Args:
            predicate: Function that takes LogEntry and returns bool.

        Returns:
            LogEntries: Filtered collection.
        """
        return LogEntries([e for e in self._entries if predicate(e)])

    def sort(self, key: str = "timestamp", reverse: bool = False) -> LogEntries:
        """Sort entries by a key.

        Args:
            key: Field name to sort by (default: timestamp).
            reverse: Sort in descending order if True.

        Returns:
            LogEntries: Sorted collection.
        """
        def sort_key(entry: LogEntry) -> Any:
            if key == "timestamp":
                return entry.timestamp
            elif key == "level":
                return entry.level.value
            elif key == "duration":
                return entry.duration or 0
            else:
                return entry.get(key)

        return LogEntries(sorted(self._entries, key=sort_key, reverse=reverse))

    def limit(self, n: int) -> LogEntries:
        """Limit to first n entries.

        Args:
            n: Maximum number of entries to return.

        Returns:
            LogEntries: Limited collection.
        """
        return LogEntries(list(islice(self._entries, n)))

    def unique(self, key: str | None = None) -> LogEntries:
        """Get unique entries based on a key.

        Args:
            key: Field name to check uniqueness. If None, uses full entry.

        Returns:
            LogEntries: Collection with unique entries.
        """
        if key is None:
            seen = set()
            unique = []
            for entry in self._entries:
                entry_tuple = tuple(sorted(entry.to_dict().items()))
                if entry_tuple not in seen:
                    seen.add(entry_tuple)
                    unique.append(entry)
            return LogEntries(unique)
        else:
            seen = set()
            unique = []
            for entry in self._entries:
                value = entry.get(key)
                if value not in seen:
                    seen.add(value)
                    unique.append(entry)
            return LogEntries(unique)

    # Aggregation methods

    def count_by_level(self) -> dict[str, int]:
        """Count entries by log level.

        Returns:
            dict[str, int]: Mapping of level to count.
        """
        counter = Counter(entry.level.value for entry in self._entries)
        return dict(counter)

    def count_by_type(self) -> dict[str, int]:
        """Count entries by action type.

        Returns:
            dict[str, int]: Mapping of action type to count.
        """
        counter = Counter(entry.action_type or "message" for entry in self._entries)
        return dict(counter)

    def group_by(self, key: str) -> dict[str, LogEntries]:
        """Group entries by a field value.

        Uses boltons' bucketize for efficient grouping.

        Args:
            key: Field name to group by.

        Returns:
            dict[str, LogEntries]: Mapping of value to LogEntries.
        """
        def _get_key(entry: LogEntry) -> str:
            return str(entry.get(key, ""))

        # Use boltons bucketize for efficient grouping
        groups = bucketize(self._entries, _get_key)
        return {k: LogEntries(v) for k, v in groups.items()}

    # Export methods (delegates to export module)

    def to_json(self, file: str | Path, pretty: bool = True) -> None:
        """Export entries to JSON file.

        Args:
            file: Output file path.
            pretty: Pretty-print JSON if True.
        """
        from .export import JsonExporter

        JsonExporter().export(self, file, pretty=pretty)

    def to_csv(self, file: str | Path, flatten: bool = True) -> None:
        """Export entries to CSV file.

        Args:
            file: Output file path.
            flatten: Flatten nested fields if True.
        """
        from .export import CsvExporter

        CsvExporter().export(self, file, flatten=flatten)

    def to_html(self, file: str | Path, template: str | None = None) -> None:
        """Export entries to HTML file.

        Args:
            file: Output file path.
            template: Optional HTML template path.
        """
        from .export import HtmlExporter

        HtmlExporter().export(self, file, template=template)

    def to_markdown(self, file: str | Path) -> None:
        """Export entries to Markdown file.

        Args:
            file: Output file path.
        """
        from .export import MarkdownExporter

        MarkdownExporter().export(self, file)

    def to_dataframe(self) -> Any:
        """Export entries to pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing log entries.

        Raises:
            ImportError: If pandas is not installed.
        """
        from .export import DataFrameExporter

        return DataFrameExporter().export(self)


class LogFilter:
    """Chainable filter builder for log entries."""

    def __init__(self, entries: LogEntries | list[LogEntry]):
        """Initialize with entries to filter.

        Args:
            entries: LogEntries collection or list of LogEntry.
        """
        self._entries = entries if isinstance(entries, LogEntries) else LogEntries(entries)

    # Level filters

    def by_level(self, *levels: str) -> LogEntries:
        """Filter by log level(s).

        Args:
            *levels: One or more log levels to include.

        Returns:
            LogEntries: Filtered entries.
        """
        level_set = set(levels)
        return self._entries.filter(lambda e: e.level.value in level_set)

    def debug(self) -> LogEntries:
        """Filter for debug level entries."""
        return self.by_level("debug")

    def info(self) -> LogEntries:
        """Filter for info level entries."""
        return self.by_level("info")

    def warning(self) -> LogEntries:
        """Filter for warning level entries."""
        return self.by_level("warning")

    def error(self) -> LogEntries:
        """Filter for error level entries."""
        return self.by_level("error", "critical")

    def critical(self) -> LogEntries:
        """Filter for critical level entries."""
        return self.by_level("critical")

    # Content filters

    def by_message(self, pattern: str, regex: bool = False) -> LogEntries:
        """Filter by message content.

        Args:
            pattern: Text pattern to match.
            regex: Use regex matching if True.

        Returns:
            LogEntries: Filtered entries.
        """
        if regex:
            compiled = re.compile(pattern, re.IGNORECASE)
            return self._entries.filter(lambda e: e.message is not None and compiled.search(e.message) is not None)
        else:
            return self._entries.filter(lambda e: e.message is not None and pattern.lower() in e.message.lower())

    def by_action_type(self, *types: str) -> LogEntries:
        """Filter by action type(s).

        Args:
            *types: One or more action types to include.

        Returns:
            LogEntries: Filtered entries.
        """
        type_set = set(types)
        return self._entries.filter(lambda e: e.action_type in type_set)

    def by_field(self, field: str, value: Any) -> LogEntries:
        """Filter by exact field value.

        Args:
            field: Field name to check.
            value: Value to match.

        Returns:
            LogEntries: Filtered entries.
        """
        return self._entries.filter(lambda e: e.get(field) == value)

    def by_field_contains(self, field: str, value: Any) -> LogEntries:
        """Filter by field containing a value.

        Args:
            field: Field name to check.
            value: Value to search for (substring for strings).

        Returns:
            LogEntries: Filtered entries.
        """
        def check(entry: LogEntry) -> bool:
            field_value = entry.get(field)
            if isinstance(field_value, str) and isinstance(value, str):
                return value.lower() in field_value.lower()
            if field_value is None:
                return False
            return bool(field_value == value)

        return self._entries.filter(check)

    # Time filters

    def by_time_range(self, start: str | datetime | float, end: str | datetime | float) -> LogEntries:
        """Filter by time range.

        Args:
            start: Start time (datetime, timestamp string, or float).
            end: End time (datetime, timestamp string, or float).

        Returns:
            LogEntries: Filtered entries.
        """
        # Convert to timestamps
        start_ts: float
        end_ts: float

        if isinstance(start, str):
            start_dt = parse_timestamp(float(start))
            start_ts = start_dt.timestamp()
        elif isinstance(start, datetime):
            start_ts = start.timestamp()
        else:
            start_ts = start

        if isinstance(end, str):
            end_dt = parse_timestamp(float(end))
            end_ts = end_dt.timestamp()
        elif isinstance(end, datetime):
            end_ts = end.timestamp()
        else:
            end_ts = end

        return self._entries.filter(lambda e: start_ts <= e.timestamp <= end_ts)

    def by_date(self, date: str) -> LogEntries:
        """Filter by date.

        Args:
            date: Date string in YYYY-MM-DD format.

        Returns:
            LogEntries: Filtered entries.
        """
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            start_ts = dt.timestamp()
            end_ts = (dt.replace(hour=23, minute=59, second=59)).timestamp()
            return self.by_time_range(start_ts, end_ts)
        except ValueError:
            return LogEntries([])

    def after(self, timestamp: str | datetime | float) -> LogEntries:
        """Filter entries after a timestamp.

        Args:
            timestamp: Timestamp to filter after.

        Returns:
            LogEntries: Filtered entries.
        """
        ts: float
        if isinstance(timestamp, str):
            dt = parse_timestamp(float(timestamp))
            ts = dt.timestamp()
        elif isinstance(timestamp, datetime):
            ts = timestamp.timestamp()
        else:
            ts = timestamp

        return self._entries.filter(lambda e: e.timestamp > ts)

    def before(self, timestamp: str | datetime | float) -> LogEntries:
        """Filter entries before a timestamp.

        Args:
            timestamp: Timestamp to filter before.

        Returns:
            LogEntries: Filtered entries.
        """
        ts: float
        if isinstance(timestamp, str):
            dt = parse_timestamp(float(timestamp))
            ts = dt.timestamp()
        elif isinstance(timestamp, datetime):
            ts = timestamp.timestamp()
        else:
            ts = timestamp

        return self._entries.filter(lambda e: e.timestamp < ts)

    # Task filters

    def by_task_uuid(self, *uuids: str) -> LogEntries:
        """Filter by task UUID(s).

        Args:
            *uuids: One or more task UUIDs to include.

        Returns:
            LogEntries: Filtered entries.
        """
        uuid_set = set(uuids)
        return self._entries.filter(lambda e: e.task_uuid in uuid_set)

    def by_nesting_level(self, min_depth: int = 1, max_depth: int = 99) -> LogEntries:
        """Filter by nesting depth.

        Args:
            min_depth: Minimum depth to include.
            max_depth: Maximum depth to include.

        Returns:
            LogEntries: Filtered entries.
        """
        return self._entries.filter(lambda e: min_depth <= e.depth <= max_depth)

    # Performance filters

    def by_duration(self, min_duration: float = 0, max_duration: float = inf) -> LogEntries:
        """Filter by action duration.

        Args:
            min_duration: Minimum duration in seconds.
            max_duration: Maximum duration in seconds.

        Returns:
            LogEntries: Filtered entries.
        """
        return self._entries.filter(
            lambda e: e.duration is not None and min_duration <= e.duration <= max_duration
        )

    def slow_actions(self, threshold: float = 1.0) -> LogEntries:
        """Filter for slow actions.

        Args:
            threshold: Duration threshold in seconds.

        Returns:
            LogEntries: Filtered entries.
        """
        return self._entries.filter(
            lambda e: e.duration is not None and e.duration >= threshold
        )

    def fast_actions(self, threshold: float = 0.001) -> LogEntries:
        """Filter for fast actions.

        Args:
            threshold: Duration threshold in seconds.

        Returns:
            LogEntries: Filtered entries.
        """
        return self._entries.filter(
            lambda e: e.duration is not None and e.duration <= threshold
        )

    # Status filters

    def with_traceback(self) -> LogEntries:
        """Filter for entries with traceback information."""
        return self._entries.filter(lambda e: "traceback" in e.fields or "exception" in e.fields)

    def failed_actions(self) -> LogEntries:
        """Filter for failed actions."""
        from .types import ActionStatus

        return self._entries.filter(lambda e: e.action_status == ActionStatus.FAILED)

    def succeeded_actions(self) -> LogEntries:
        """Filter for succeeded actions."""
        from .types import ActionStatus

        return self._entries.filter(lambda e: e.action_status == ActionStatus.SUCCEEDED)

    def started_actions(self) -> LogEntries:
        """Filter for started actions (not yet completed)."""
        from .types import ActionStatus

        return self._entries.filter(lambda e: e.action_status == ActionStatus.STARTED)

    # Delegate methods to LogEntries

    def limit(self, n: int) -> LogEntries:
        """Limit to first n entries.

        Args:
            n: Maximum number of entries to return.

        Returns:
            LogEntries: Limited collection.
        """
        return self._entries.limit(n)

    def sort(self, key: str = "timestamp", reverse: bool = False) -> LogEntries:
        """Sort entries by a key.

        Args:
            key: Field name to sort by (default: timestamp).
            reverse: Sort in descending order if True.

        Returns:
            LogEntries: Sorted collection.
        """
        return self._entries.sort(key, reverse)

    def count_by_level(self) -> dict[str, int]:
        """Count entries by log level.

        Returns:
            dict[str, int]: Mapping of level to count.
        """
        return self._entries.count_by_level()

    def count_by_type(self) -> dict[str, int]:
        """Count entries by action type.

        Returns:
            dict[str, int]: Mapping of action type to count.
        """
        return self._entries.count_by_type()

    def group_by(self, key: str) -> dict[str, LogEntries]:
        """Group entries by a field value.

        Args:
            key: Field name to group by.

        Returns:
            dict[str, LogEntries]: Mapping of value to LogEntries.
        """
        return self._entries.group_by(key)

    # Export methods (delegate to LogEntries)

    def to_json(self, file: str | Path, pretty: bool = True) -> None:
        """Export entries to JSON file.

        Args:
            file: Output file path.
            pretty: Pretty-print JSON if True.
        """
        self._entries.to_json(file, pretty)

    def to_csv(self, file: str | Path, flatten: bool = True) -> None:
        """Export entries to CSV file.

        Args:
            file: Output file path.
            flatten: Flatten nested fields if True.
        """
        self._entries.to_csv(file, flatten)

    def to_html(self, file: str | Path, template: str | None = None) -> None:
        """Export entries to HTML file.

        Args:
            file: Output file path.
            template: Optional HTML template path.
        """
        self._entries.to_html(file, template)

    def to_markdown(self, file: str | Path) -> None:
        """Export entries to Markdown file.

        Args:
            file: Output file path.
        """
        self._entries.to_markdown(file)

    def to_dataframe(self) -> Any:
        """Export entries to pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing log entries.

        Raises:
            ImportError: If pandas is not installed.
        """
        return self._entries.to_dataframe()
