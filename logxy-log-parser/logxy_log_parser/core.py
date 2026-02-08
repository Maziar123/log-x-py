"""
Core parsing functionality for logxy-log-parser.

Contains LogEntry dataclass and LogParser for parsing LogXPy log files.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .types import ActionStatus, Level, LogDict, TaskLevel
from .utils import level_from_message_type


@dataclass(frozen=True, slots=True)
class LogEntry:
    """Immutable log entry with typed accessors.

    Represents a single log entry from a LogXPy log file.
    """

    timestamp: float
    task_uuid: str
    task_level: TaskLevel
    message_type: str
    message: str | None
    action_type: str | None
    action_status: ActionStatus | None
    duration: float | None
    fields: dict[str, Any]
    line_number: int = 0  # Line number in the log file (0 if unknown)

    @property
    def level(self) -> Level:
        """Get the log level for this entry."""
        return level_from_message_type(self.message_type)

    @property
    def depth(self) -> int:
        """Get the nesting depth of this entry."""
        return len(self.task_level)

    @property
    def is_error(self) -> bool:
        """Check if this is an error-level entry."""
        return self.level in (Level.ERROR, Level.CRITICAL)

    @property
    def is_action(self) -> bool:
        """Check if this is an action entry (start/end/failed)."""
        return self.action_type is not None

    @property
    def is_message(self) -> bool:
        """Check if this is a message entry."""
        return "message" in self.message_type

    @classmethod
    def from_dict(cls, data: LogDict, line_number: int = 0) -> LogEntry:
        """Create LogEntry from a dictionary.

        Args:
            data: Dictionary containing log entry data.

        Returns:
            LogEntry: New LogEntry instance.
        """
        # Parse task_level - handle both array format [1,1] and string format "/1/1"
        task_level_raw = data.get("task_level")
        if task_level_raw is not None:
            if isinstance(task_level_raw, list):
                # Array format: [1] or [1,1] or [1,1,1]
                task_level = tuple(int(x) if isinstance(x, (int, float)) else 0
                                   for x in task_level_raw if x is not None)
            elif isinstance(task_level_raw, str):
                # String format: "/1" or "/1/1"
                if task_level_raw.startswith("/"):
                    level_parts = task_level_raw[1:].split("/") if task_level_raw != "/" else []
                    task_level = tuple(int(p) for p in level_parts if p)
                else:
                    # Try to split by /
                    level_parts = task_level_raw.split("/") if task_level_raw else []
                    task_level = tuple(int(p) for p in level_parts if p)
            elif isinstance(task_level_raw, (int, float)):
                task_level = (int(task_level_raw),)
            else:
                task_level = ()
        else:
            # Fallback: try old "level" field for backward compatibility
            level_str = data.get("level", "/")
            if isinstance(level_str, str) and level_str.startswith("/"):
                level_parts = level_str[1:].split("/") if level_str != "/" else []
                task_level = tuple(int(p) for p in level_parts if p)
            else:
                task_level = ()

        # Parse action status - check both action_status and status fields
        action_status = data.get("action_status") or data.get("status")
        if action_status:
            try:
                action_status = ActionStatus(action_status)
            except ValueError:
                action_status = None
        else:
            action_status = None

        # Parse duration - check multiple possible field names
        duration = None
        for field in ("duration_ns", "logxpy:duration", "eliot:duration", "duration"):
            if field in data:
                duration_val = data[field]
                if duration_val is not None:
                    if field == "duration_ns":
                        duration = duration_val / 1e9  # Convert nanoseconds to seconds
                    else:
                        # Already in seconds or unknown format
                        duration = float(duration_val) if not isinstance(duration_val, bool) else None
                    break

        # Extract known fields (everything else goes to fields dict)
        # Note: "level" field is for log level, not task level - keep it in fields if not a known level
        known_fields = {
            "task_uuid",
            "timestamp",
            "task_level",
            "message_type",
            "message",
            "action_type",
            "action_status",
            "status",
            "duration_ns",
            "logxpy:duration",
            "eliot:duration",
            "duration",
            # logxpy specific
            "logxpy:traceback",
            "exception",
            "reason",
            # Keep log level in entries for reference but don't store in fields
            "level",
        }
        fields = {k: v for k, v in data.items() if k not in known_fields}

        # Get timestamp (could be string or number)
        timestamp = data.get("timestamp", 0)
        if isinstance(timestamp, str):
            # Try to parse as float
            try:
                timestamp = float(timestamp)
            except ValueError:
                timestamp = 0
        elif isinstance(timestamp, (int, float)):
            timestamp = float(timestamp)

        return cls(
            timestamp=timestamp,
            task_uuid=data.get("task_uuid", ""),
            task_level=task_level,
            message_type=data.get("message_type", ""),
            message=data.get("message"),
            action_type=data.get("action_type"),
            action_status=action_status,
            duration=duration,
            fields=fields,
            line_number=line_number,
        )

    def to_dict(self) -> LogDict:
        """Convert LogEntry back to dictionary format.

        Returns:
            LogDict: Dictionary representation of this entry.
        """
        result: LogDict = {
            "task_uuid": self.task_uuid,
            "timestamp": self.timestamp,
            "task_level": list(self.task_level),  # Array format for logxpy
            "message_type": self.message_type,
        }

        if self.message:
            result["message"] = self.message
        if self.action_type:
            result["action_type"] = self.action_type
        if self.action_status:
            result["action_status"] = self.action_status.value
        if self.duration is not None:
            result["duration_ns"] = int(self.duration * 1e9)

        result.update(self.fields)
        return result

    def get(self, key: str, default: Any = None) -> Any:
        """Get a field value from the entry.

        Checks both named fields and the fields dictionary.

        Args:
            key: Field name to look up.
            default: Default value if key not found.

        Returns:
            Any: Field value or default.
        """
        if hasattr(self, key):
            return getattr(self, key)
        return self.fields.get(key, default)

    def __str__(self) -> str:
        """String representation of the log entry."""
        parts = [f"[{self.level.value.upper()}]"]
        if self.message:
            parts.append(self.message)
        elif self.action_type:
            parts.append(f"{self.action_type} ({self.action_status or 'unknown'})")
        return " ".join(parts)


class ParseError:
    """Represents a parsing error with context."""

    def __init__(self, line_number: int, line: str, error: str):
        """Initialize parse error.

        Args:
            line_number: Line number where error occurred.
            line: The raw line content.
            error: Error message.
        """
        self.line_number = line_number
        self.line = line
        self.error = error

    def __str__(self) -> str:
        """String representation of the error."""
        preview = self.line[:100] + "..." if len(self.line) > 100 else self.line
        return f"Line {self.line_number}: {self.error}\n  {preview}"

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary.

        Returns:
            dict[str, Any]: Error dictionary.
        """
        return {
            "line_number": self.line_number,
            "line": self.line[:200],  # Truncate for safety
            "error": self.error,
        }


class LogParser:
    """Parse LogXPy JSON log files.

    Supports parsing from file paths, file objects, or raw data.
    """

    def __init__(self, source: str | Path | Any | list[dict[str, Any]]):
        """Initialize with file path, file object, or raw data.

        Args:
            source: File path (str/Path), file-like object, or list of dicts.
        """
        self._source = source
        self._entries: list[LogEntry] | None = None
        self._errors: list[ParseError] = []

    @property
    def errors(self) -> list[ParseError]:
        """Get list of parsing errors.

        Returns:
            list[ParseError]: List of parse errors encountered.
        """
        return self._errors.copy()

    def parse(self) -> list[LogEntry]:
        """Parse entire source into LogEntries.

        Returns:
            list[LogEntry]: All parsed log entries.
        """
        if self._entries is not None:
            return self._entries

        entries: list[LogEntry] = []

        if isinstance(self._source, (str, Path)):
            # Parse from file path
            path = Path(self._source)
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    entries = self._parse_file(f)
        elif isinstance(self._source, list):
            # Parse from list of dicts
            entries = [LogEntry.from_dict(d) for d in self._source]
        elif hasattr(self._source, "read"):
            # Parse from file-like object
            entries = self._parse_file(self._source)
        else:
            raise ValueError(f"Unsupported source type: {type(self._source)}")

        self._entries = entries
        return entries

    def parse_stream(self) -> Iterator[LogEntry]:
        """Stream parse for memory-efficient processing.

        Yields:
            LogEntry: Each log entry as it's parsed.
        """
        if isinstance(self._source, (str, Path)):
            path = Path(self._source)
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    yield from self._parse_stream_file(f)
        elif isinstance(self._source, list):
            for d in self._source:
                yield LogEntry.from_dict(d)
        elif hasattr(self._source, "read"):
            yield from self._parse_stream_file(self._source)
        else:
            raise ValueError(f"Unsupported source type: {type(self._source)}")

    def _parse_file(self, file_obj: Any) -> list[LogEntry]:
        """Parse all lines from a file object.

        Args:
            file_obj: File-like object to read from.

        Returns:
            list[LogEntry]: All parsed entries.
        """
        entries: list[LogEntry] = []
        self._errors = []
        line_number = 0

        for line in file_obj:
            line_number += 1
            line_stripped = line.strip()
            if not line_stripped:
                continue
            try:
                data = json.loads(line_stripped)
                entries.append(LogEntry.from_dict(data, line_number))
            except json.JSONDecodeError as e:
                self._errors.append(ParseError(line_number, line_stripped, f"JSON decode error: {e}"))
            except (ValueError, KeyError, TypeError) as e:
                self._errors.append(ParseError(line_number, line_stripped, f"Parse error: {e}"))
        return entries

    def _parse_stream_file(self, file_obj: Any) -> Iterator[LogEntry]:
        """Stream parse lines from a file object.

        Args:
            file_obj: File-like object to read from.

        Yields:
            LogEntry: Each parsed entry.
        """
        line_number = 0
        for line in file_obj:
            line_number += 1
            line_stripped = line.strip()
            if not line_stripped:
                continue
            try:
                data = json.loads(line_stripped)
                yield LogEntry.from_dict(data, line_number)
            except (json.JSONDecodeError, ValueError, KeyError):
                # Skip malformed lines in stream mode (no error tracking)
                continue

    def __len__(self) -> int:
        """Get the number of entries in the parsed log.

        Returns:
            int: Number of entries.
        """
        if self._entries is None:
            self.parse()
        return len(self._entries) if self._entries else 0
