"""Core parsing functionality for logxy-log-parser.

Contains LogEntry dataclass and LogParser for parsing LogXPy log files.

Supports both:
- New LogXPy compact format (ts, tid, lvl, mt, at, st, dur, msg)
- Legacy Eliot format (timestamp, task_uuid, task_level, etc.)

Python 3.12+ features used:
- Type aliases (PEP 695): `type Name = ...`
- Pattern matching (PEP 634): Clean value routing
- Dataclass slots (PEP 681): Memory optimization
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from common.types import (
    ACTION_STATUS,
    ACTION_TYPE,
    ALL_KNOWN_FIELDS,
    AT,
    DUR,
    DURATION_NS,
    LVL,
    MESSAGE,
    MESSAGE_TYPE,
    MSG,
    MT,
    ST,
    TASK_LEVEL,
    TASK_UUID,
    TID,
    TIMESTAMP,
    TS,
    ActionStatus,
    Level,
    LogDict,
    TaskLevel,
)
from .utils import extract_duration, get_field_value, level_from_entry


@dataclass(frozen=True, slots=True)
class LogEntry:
    """Immutable log entry with typed accessors.

    Represents a single log entry from a LogXPy log file.
    Supports both compact and legacy field naming conventions.
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
    _format: str = "auto"  # Detected format: "compact", "legacy", or "auto"

    @property
    def level(self) -> Level:
        """Get the log level for this entry."""
        # Check direct level field first
        if "level" in self.fields:
            level_val = self.fields["level"]
            if isinstance(level_val, str):
                try:
                    return Level(level_val.lower())
                except ValueError:
                    pass
        return level_from_entry({
            MT: self.message_type,
            AT: self.action_type,
            ST: self.action_status.value if self.action_status else None,
        })

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

        Handles both compact and legacy field naming conventions.

        Args:
            data: Dictionary containing log entry data.
            line_number: Line number in the source file.

        Returns:
            LogEntry: New LogEntry instance.
        """
        # Detect format first
        detected_format = "compact" if TS in data or TID in data else "legacy"

        # Use get_field_value to check both naming conventions
        # Task level parsing
        task_level = cls._parse_task_level(data)

        # Action status parsing
        action_status = cls._parse_action_status(data)

        # Duration parsing (handles seconds vs nanoseconds)
        duration = extract_duration(data)

        # Timestamp parsing
        timestamp = get_field_value(data, TS, 0)
        if isinstance(timestamp, str):
            try:
                timestamp = float(timestamp)
            except ValueError:
                timestamp = 0.0
        elif isinstance(timestamp, (int, float)):
            timestamp = float(timestamp)

        # Extract fields (everything not a known field)
        known_fields = ALL_KNOWN_FIELDS | {"status"}
        fields = {k: v for k, v in data.items() if k not in known_fields}

        return cls(
            timestamp=timestamp,
            task_uuid=get_field_value(data, TID, ""),
            task_level=task_level,
            message_type=get_field_value(data, MT, ""),
            message=get_field_value(data, MSG),
            action_type=get_field_value(data, AT),
            action_status=action_status,
            duration=duration,
            fields=fields,
            line_number=line_number,
            _format=detected_format,
        )

    @staticmethod
    def _parse_task_level(data: LogDict) -> TaskLevel:
        """Parse task level from entry data.

        Handles compact ('lvl') and legacy ('task_level') field names.
        Supports array, string, and numeric formats.

        Args:
            data: Log entry dictionary

        Returns:
            TaskLevel as tuple of integers
        """
        # Try compact then legacy
        lvl_raw = get_field_value(data, LVL, [])

        if isinstance(lvl_raw, list):
            return tuple(int(x) if isinstance(x, (int, float)) else 0
                       for x in lvl_raw if x is not None)

        if isinstance(lvl_raw, tuple):
            return lvl_raw

        if isinstance(lvl_raw, str):
            # String format: "/1" or "/1/1"
            if lvl_raw.startswith("/"):
                parts = lvl_raw[1:].split("/") if lvl_raw != "/" else []
            else:
                parts = lvl_raw.split("/") if lvl_raw else []
            return tuple(int(p) for p in parts if p)

        if isinstance(lvl_raw, (int, float)):
            return (int(lvl_raw),)

        return ()

    @staticmethod
    def _parse_action_status(data: LogDict) -> ActionStatus | None:
        """Parse action status from entry data.

        Args:
            data: Log entry dictionary

        Returns:
            ActionStatus enum or None
        """
        # Check compact 'st' first, then legacy 'action_status'
        status_val = get_field_value(data, ST) or data.get("status")

        if status_val:
            try:
                return ActionStatus(status_val)
            except (ValueError, TypeError):
                pass

        # Infer from action_type presence
        if get_field_value(data, AT):
            # Default to started if action_type exists but no status
            return ActionStatus.STARTED

        return None

    def to_dict(self, output_format: str = "compact") -> LogDict:
        """Convert LogEntry back to dictionary format.

        Args:
            output_format: Output format - "compact" or "legacy"

        Returns:
            LogDict: Dictionary representation of this entry.
        """
        if output_format == "legacy":
            return self._to_legacy_dict()
        return self._to_compact_dict()

    def _to_compact_dict(self) -> LogDict:
        """Convert to compact field name format."""
        result: LogDict = {
            TS: self.timestamp,
            TID: self.task_uuid,
            LVL: list(self.task_level),
            MT: self.message_type,
        }

        if self.message:
            result[MSG] = self.message
        if self.action_type:
            result[AT] = self.action_type
        if self.action_status:
            result[ST] = self.action_status.value
        if self.duration is not None:
            result[DUR] = self.duration  # Seconds in compact format

        result.update(self.fields)
        return result

    def _to_legacy_dict(self) -> LogDict:
        """Convert to legacy field name format."""
        result: LogDict = {
            TIMESTAMP: self.timestamp,
            TASK_UUID: self.task_uuid,
            TASK_LEVEL: list(self.task_level),
            MESSAGE_TYPE: self.message_type,
        }

        if self.message:
            result[MESSAGE] = self.message
        if self.action_type:
            result[ACTION_TYPE] = self.action_type
        if self.action_status:
            result[ACTION_STATUS] = self.action_status.value
        if self.duration is not None:
            result[DURATION_NS] = int(self.duration * 1e9)  # Nanoseconds in legacy

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
    Automatically detects compact vs legacy format.
    """

    def __init__(
        self,
        source: str | Path | Any | list[dict[str, Any]],
        log_format: str = "auto",
    ):
        """Initialize with file path, file object, or raw data.

        Args:
            source: File path (str/Path), file-like object, or list of dicts.
            log_format: Expected format - "compact", "legacy", or "auto" (default).
        """
        self._source = source
        self._format = log_format
        self._entries: list[LogEntry] | None = None
        self._errors: list[ParseError] = []

    @property
    def errors(self) -> list[ParseError]:
        """Get list of parsing errors.

        Returns:
            list[ParseError]: List of parse errors encountered.
        """
        return self._errors.copy()

    @property
    def format(self) -> str:
        """Get detected format."""
        return self._format

    def parse(self) -> list[LogEntry]:
        """Parse entire source into LogEntries.

        Returns:
            list[LogEntry]: All parsed log entries.
        """
        if self._entries is not None:
            return self._entries

        entries: list[LogEntry] = []

        if isinstance(self._source, (str, Path)):
            path = Path(self._source)
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    entries = self._parse_file(f)
        elif isinstance(self._source, list):
            entries = [LogEntry.from_dict(d) for d in self._source]
        elif hasattr(self._source, "read"):
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
