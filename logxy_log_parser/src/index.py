"""
Indexing functionality for logxy-log-parser.

Provides fast indexed lookups for large log files.
"""

from __future__ import annotations

import gzip
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .core import LogEntry


@dataclass
class IndexStats:
    """Statistics for a log index."""

    total_entries: int = 0
    unique_tasks: int = 0
    level_counts: dict[str, int] = field(default_factory=dict)
    time_range: tuple[float, float] = (0, 0)
    file_size: int = 0
    indexed_at: float = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary.

        Returns:
            dict[str, Any]: Stats dictionary.
        """
        return {
            "total_entries": self.total_entries,
            "unique_tasks": self.unique_tasks,
            "level_counts": self.level_counts,
            "time_range": self.time_range,
            "file_size": self.file_size,
            "indexed_at": self.indexed_at,
        }


@dataclass
class LogPosition:
    """Position of a log entry in a file."""

    offset: int
    line_number: int
    timestamp: float
    level: str
    task_uuid: str


class LogIndex:
    """Index for fast lookups in log files.

    Maintains indexes by:
    - Line number/offset (for direct access)
    - Task UUID (for finding all entries in a task)
    - Level (for quick level filtering)
    - Time range (for time-based queries)
    """

    def __init__(self, source: str | Path) -> None:
        """Initialize index for a log file.

        Args:
            source: Path to the log file.
        """
        self._path = Path(source)
        self._entries_by_line: dict[int, LogPosition] = {}
        self._entries_by_task: dict[str, list[int]] = defaultdict(list)
        self._entries_by_level: dict[str, list[int]] = defaultdict(list)
        self._time_index: list[tuple[float, int]] = []  # (timestamp, line_number)
        self._stats = IndexStats()
        self._built = False

    @property
    def stats(self) -> IndexStats:
        """Get index statistics.

        Returns:
            IndexStats: Index statistics.
        """
        return self._stats

    @property
    def is_built(self) -> bool:
        """Check if index has been built.

        Returns:
            bool: True if index is built.
        """
        return self._built

    def build(self, force: bool = False) -> None:
        """Build the index from the log file.

        Args:
            force: Rebuild even if already indexed.
        """
        if self._built and not force:
            return

        self._entries_by_line.clear()
        self._entries_by_task.clear()
        self._entries_by_level.clear()
        self._time_index.clear()

        import time

        # Handle gzip files
        open_func = gzip.open if str(self._path).endswith(".gz") else open

        with open_func(self._path, "rt", encoding="utf-8") as f:
            line_number = 0
            offset = 0
            task_uuids = set()
            min_ts = float("inf")
            max_ts = 0

            for line in f:
                line_start = offset
                line_number += 1
                offset = f.tell() if hasattr(f, "tell") else 0

                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    timestamp = data.get("timestamp", 0)
                    if isinstance(timestamp, str):
                        timestamp = float(timestamp)

                    task_uuid = data.get("task_uuid", "")
                    message_type = data.get("message_type", "")

                    # Determine level from message_type
                    if "loggerx:" in message_type:
                        level = message_type.split("loggerx:")[1].lower()
                    else:
                        level = "info"

                    # Create position record
                    pos = LogPosition(
                        offset=line_start,
                        line_number=line_number,
                        timestamp=timestamp,
                        level=level,
                        task_uuid=task_uuid,
                    )

                    self._entries_by_line[line_number] = pos
                    self._entries_by_task[task_uuid].append(line_number)
                    self._entries_by_level[level].append(line_number)
                    self._time_index.append((timestamp, line_number))

                    # Update stats
                    task_uuids.add(task_uuid)
                    min_ts = min(min_ts, timestamp)
                    max_ts = max(max_ts, timestamp)

                except (json.JSONDecodeError, ValueError):
                    # Skip malformed lines
                    continue

        # Sort time index
        self._time_index.sort()

        # Update stats
        self._stats = IndexStats(
            total_entries=len(self._entries_by_line),
            unique_tasks=len(task_uuids),
            level_counts={k: len(v) for k, v in self._entries_by_level.items()},
            time_range=(min_ts, max_ts) if min_ts != float("inf") else (0, 0),
            file_size=self._path.stat().st_size,
            indexed_at=time.time(),
        )

        self._built = True

    def find_by_task(self, task_uuid: str) -> list[LogPosition]:
        """Find all entries for a task UUID.

        Args:
            task_uuid: Task UUID to search for.

        Returns:
            list[LogPosition]: List of positions.
        """
        if not self._built:
            self.build()
        return [self._entries_by_line[n] for n in self._entries_by_task.get(task_uuid, [])]

    def find_by_level(self, level: str) -> list[LogPosition]:
        """Find all entries at a log level.

        Args:
            level: Log level to filter by.

        Returns:
            list[LogPosition]: List of positions.
        """
        if not self._built:
            self.build()
        return [self._entries_by_line[n] for n in self._entries_by_level.get(level.lower(), [])]

    def find_by_time_range(self, start: float, end: float) -> list[LogPosition]:
        """Find entries in a time range.

        Args:
            start: Start timestamp.
            end: End timestamp.

        Returns:
            list[LogPosition]: List of positions.
        """
        if not self._built:
            self.build()

        # Binary search for start
        import bisect

        start_idx = bisect.bisect_left([t for t, _ in self._time_index], start)
        end_idx = bisect.bisect_right([t for t, _ in self._time_index], end)

        line_numbers = [ln for _, ln in self._time_index[start_idx:end_idx]]
        return [self._entries_by_line[n] for n in line_numbers if n in self._entries_by_line]

    def get_lines(self, positions: list[LogPosition]) -> list[LogEntry]:
        """Load entries at specific positions.

        Args:
            positions: List of positions to load.

        Returns:
            list[LogEntry]: Loaded log entries.
        """
        # Handle gzip files
        open_func = gzip.open if str(self._path).endswith(".gz") else open

        entries = []

        # Group positions by line number for efficient access
        positions_by_line = {p.line_number: p for p in positions}

        with open_func(self._path, "rt", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if line_num in positions_by_line:
                    try:
                        data = json.loads(line.strip())
                        from .core import LogEntry
                        entries.append(LogEntry.from_dict(data, line_num))

                        # Stop if we've loaded all requested entries
                        if len(entries) == len(positions):
                            break
                    except (json.JSONDecodeError, ValueError):
                        continue

        return entries

    def query(
        self,
        task_uuid: str | None = None,
        level: str | None = None,
        start_time: float | None = None,
        end_time: float | None = None,
    ) -> list[LogPosition]:
        """Query the index with multiple filters.

        Args:
            task_uuid: Optional task UUID filter.
            level: Optional level filter.
            start_time: Optional start timestamp.
            end_time: Optional end timestamp.

        Returns:
            list[LogPosition]: Filtered list of positions.
        """
        if not self._built:
            self.build()

        # Start with all entries or filtered by first criterion
        if task_uuid:
            positions = {p.line_number: p for p in self.find_by_task(task_uuid)}
        elif level:
            positions = {p.line_number: p for p in self.find_by_level(level)}
        else:
            positions = dict(self._entries_by_line.items())

        # Apply additional filters
        if task_uuid and task_uuid not in self._entries_by_task:
            return []

        if level and level.lower() not in self._entries_by_level:
            return []

        if task_uuid:
            task_lines = set(self._entries_by_task[task_uuid])
            positions = {ln: p for ln, p in positions.items() if ln in task_lines}

        if level:
            level_lines = set(self._entries_by_level[level.lower()])
            positions = {ln: p for ln, p in positions.items() if ln in level_lines}

        if start_time is not None or end_time is not None:
            start = start_time or 0
            end = end_time or float("inf")
            time_filtered = self.find_by_time_range(start, end)
            time_lines = {p.line_number for p in time_filtered}
            positions = {ln: p for ln, p in positions.items() if ln in time_lines}

        return list(positions.values())

    def save(self, index_path: str | Path | None = None) -> None:
        """Save index to a file.

        Args:
            index_path: Path to save index. Defaults to <log_file>.index.
        """
        if index_path is None:
            index_path = self._path.with_suffix(self._path.suffix + ".index")

        import pickle

        index_data = {
            "entries_by_line": self._entries_by_line,
            "entries_by_task": dict(self._entries_by_task),
            "entries_by_level": dict(self._entries_by_level),
            "time_index": self._time_index,
            "stats": self._stats,
            "source_path": str(self._path),
            "source_mtime": self._path.stat().st_mtime,
        }

        with open(index_path, "wb") as f:
            pickle.dump(index_data, f)

    @classmethod
    def load(cls, index_path: str | Path) -> LogIndex:
        """Load index from a file.

        Args:
            index_path: Path to the index file.

        Returns:
            LogIndex: Loaded index.
        """
        import pickle

        with open(index_path, "rb") as f:
            data = pickle.load(f)

        # Create index instance
        source_path = Path(data["source_path"])
        index = cls(source_path)

        # Restore data
        index._entries_by_line = data["entries_by_line"]
        index._entries_by_task = defaultdict(list, data["entries_by_task"])
        index._entries_by_level = defaultdict(list, data["entries_by_level"])
        index._time_index = data["time_index"]
        index._stats = data["stats"]
        index._built = True

        return index

    def is_stale(self) -> bool:
        """Check if the index is stale (log file modified since indexing).

        Returns:
            bool: True if index needs rebuilding.
        """
        if not self._path.exists():
            return True
        return self._path.stat().st_mtime > self._stats.indexed_at


class IndexedLogParser:
    """Parser that uses indexing for fast queries on large files."""

    def __init__(self, source: str | Path, auto_index: bool = True) -> None:
        """Initialize indexed parser.

        Args:
            source: Path to the log file.
            auto_index: Automatically build index on first query.
        """
        self._path = Path(source)
        self._index = LogIndex(self._path)
        self._auto_index = auto_index

    @property
    def index(self) -> LogIndex:
        """Get the underlying index.

        Returns:
            LogIndex: The log index.
        """
        if self._auto_index and not self._index.is_built:
            self._index.build()
        return self._index

    def query(
        self,
        task_uuid: str | None = None,
        level: str | None = None,
        start_time: float | None = None,
        end_time: float | None = None,
        load_entries: bool = True,
    ) -> list[LogEntry] | list[LogPosition]:
        """Query the log file with filters.

        Args:
            task_uuid: Optional task UUID filter.
            level: Optional level filter.
            start_time: Optional start timestamp.
            end_time: Optional end timestamp.
            load_entries: Whether to load full entries or just positions.

        Returns:
            list[LogEntry] | list[LogPosition]: Query results.
        """
        positions = self._index.query(
            task_uuid=task_uuid,
            level=level,
            start_time=start_time,
            end_time=end_time,
        )

        if load_entries:
            return self._index.get_lines(positions)
        return positions

    def get_task(self, task_uuid: str) -> list[LogEntry]:
        """Get all entries for a task.

        Args:
            task_uuid: Task UUID.

        Returns:
            list[LogEntry]: All entries for the task.
        """
        return self._index.get_lines(self._index.find_by_task(task_uuid))

    def get_errors(self) -> list[LogEntry]:
        """Get all error-level entries.

        Returns:
            list[LogEntry]: All error entries.
        """
        error_positions = []
        for level_name in ("error", "critical"):
            error_positions.extend(self._index.find_by_level(level_name))
        return self._index.get_lines(error_positions)

    def get_time_range(self, start: float, end: float) -> list[LogEntry]:
        """Get entries in a time range.

        Args:
            start: Start timestamp.
            end: End timestamp.

        Returns:
            list[LogEntry]: Entries in range.
        """
        return self._index.get_lines(self._index.find_by_time_range(start, end))
