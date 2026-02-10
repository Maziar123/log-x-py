"""Shared type definitions for LogXPy ecosystem.

This module contains all type aliases, enums, and constants shared across:
- logxpy (logging library)
- logxpy-cli-view (tree viewer)
- logxy-log-parser (log parser)

Supports both:
- New LogXPy compact format (ts, tid, lvl, mt, at, st, dur, msg)
- Legacy Eliot format (timestamp, task_uuid, task_level, etc.)

Python 3.12+ features used:
- Type aliases (PEP 695): `type Name = ...`
- StrEnum (PEP 663): Type-safe string enums
"""

from __future__ import annotations

from enum import IntEnum, StrEnum
from typing import Any

# ============================================================================
# Type Aliases (PEP 695 - Python 3.12+)
# ============================================================================

type LogEntry = dict[str, Any]
type LogDict = dict[str, Any]
type TaskLevelTuple = tuple[int, ...]
# Alias for TaskLevelTuple for backward compatibility
type TaskLevel = TaskLevelTuple
type ActionStatusLiteral = Literal["started", "succeeded", "failed"]
type FieldDict = dict[str, Any]
type ContextDict = dict[str, Any]
type MessageDict = dict[str, Any]


# ============================================================================
# Compact Field Name Constants (LogXPy Format)
# ============================================================================

# Primary compact field names (1-2 chars for minimal log size)
TS: str = "ts"              # timestamp (was: timestamp)
TID: str = "tid"            # task_id / task_uuid (Sqid format)
LVL: str = "lvl"            # task_level hierarchy
MT: str = "mt"              # message_type
AT: str = "at"              # action_type
ST: str = "st"              # action_status
DUR: str = "dur"            # duration in SECONDS (was duration_ns)
MSG: str = "msg"            # message text


# ============================================================================
# Legacy Field Name Constants (Eliot Format)
# ============================================================================

TIMESTAMP: str = "timestamp"
TASK_UUID: str = "task_uuid"
TASK_LEVEL: str = "task_level"
MESSAGE_TYPE: str = "message_type"
ACTION_TYPE: str = "action_type"
ACTION_STATUS: str = "action_status"
DURATION_NS: str = "duration_ns"
MESSAGE: str = "message"

# Legacy aliases (for backwards compatibility)
TASK_UUID_ALIAS: str = TID        # Alias: task_uuid -> tid
TASK_LEVEL_ALIAS: str = LVL       # Alias: task_level -> lvl
TIMESTAMP_ALIAS: str = TS         # Alias: timestamp -> ts
MESSAGE_TYPE_ALIAS: str = MT      # Alias: message_type -> mt
ACTION_TYPE_ALIAS: str = AT       # Alias: action_type -> at
ACTION_STATUS_ALIAS: str = ST     # Alias: action_status -> st
DURATION_NS_ALIAS: str = DUR      # Alias: duration_ns -> dur


# ============================================================================
# Field Name Mapping (Compact <-> Legacy)
# ============================================================================

# Legacy to compact mapping
LEGACY_TO_COMPACT: dict[str, str] = {
    TIMESTAMP: TS,
    TASK_UUID: TID,
    TASK_LEVEL: LVL,
    MESSAGE_TYPE: MT,
    ACTION_TYPE: AT,
    ACTION_STATUS: ST,
    DURATION_NS: DUR,
    MESSAGE: MSG,
}

# Compact to legacy mapping
COMPACT_TO_LEGACY: dict[str, str] = {
    TS: TIMESTAMP,
    TID: TASK_UUID,
    LVL: TASK_LEVEL,
    MT: MESSAGE_TYPE,
    AT: ACTION_TYPE,
    ST: ACTION_STATUS,
    DUR: DURATION_NS,
    MSG: MESSAGE,
}

# All known field names (both formats)
ALL_KNOWN_FIELDS: set[str] = {
    # Compact
    TS, TID, LVL, MT, AT, ST, DUR, MSG,
    # Legacy
    TIMESTAMP, TASK_UUID, TASK_LEVEL, MESSAGE_TYPE,
    ACTION_TYPE, ACTION_STATUS, DURATION_NS, MESSAGE,
    # Common additional fields
    "exc", "reason", "logxpy:traceback", "logxpy:duration",
    "eliot:duration", "fg", "bg", "level",
}


# ============================================================================
# Log Level Enums
# ============================================================================

class Level(IntEnum):
    """Numeric log levels for filtering and sorting.

    Matches standard syslog levels with additions for SUCCESS and NOTE.
    """
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    NOTE = 26
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LevelName(StrEnum):
    """String log level names (PEP 663 - Python 3.12+ StrEnum).

    Provides type-safe string values for log levels.
    """
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    NOTE = "note"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# For backwards compatibility with logxy-log-parser
class LevelStr(StrEnum):
    """Log level enum matching LogXPy LevelName (alias)."""
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    NOTE = "note"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LevelValue(IntEnum):
    """Numeric log levels for filtering and sorting (alias for Level)."""
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    NOTE = 26
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


# Map level name to value
LEVEL_VALUES: dict[str, int] = {
    "debug": 10,
    "info": 20,
    "success": 25,
    "note": 26,
    "warning": 30,
    "error": 40,
    "critical": 50,
}


# ============================================================================
# Action Status Enum
# ============================================================================

class ActionStatusStr(StrEnum):
    """Action status values as string enum (PEP 663)."""
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


# For backwards compatibility with logxy-log-parser
class ActionStatus(StrEnum):
    """Action status enum matching LogXPy ActionStatus (alias)."""
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


# ============================================================================
# Log Format Detection
# ============================================================================

class LogFormat(StrEnum):
    """Log format type for field naming convention."""

    COMPACT = "compact"    # New LogXPy: ts, tid, lvl, mt, at, st, dur, msg
    LEGACY = "legacy"      # Eliot: timestamp, task_uuid, task_level, etc.
    AUTO = "auto"          # Auto-detect from content
    UNKNOWN = "unknown"


# ============================================================================
# Message Type Patterns
# ============================================================================

MESSAGE_TYPE_PREFIX = "loggerx:"  # LoggerX message type prefix


# ============================================================================
# Utility Functions
# ============================================================================

def normalize_field_name(field: str) -> str:
    """Convert legacy field name to compact format.

    Args:
        field: Field name (compact or legacy)

    Returns:
        Compact field name (unchanged if already compact)
    """
    return LEGACY_TO_COMPACT.get(field, field)


def legacy_field_name(field: str) -> str:
    """Convert compact field name to legacy format.

    Args:
        field: Field name (compact or legacy)

    Returns:
        Legacy field name (unchanged if already legacy)
    """
    return COMPACT_TO_LEGACY.get(field, field)


def is_compact_field(field: str) -> bool:
    """Check if field name is compact format.

    Args:
        field: Field name to check

    Returns:
        True if field is a compact field name
    """
    return field in COMPACT_TO_LEGACY


def is_legacy_field(field: str) -> bool:
    """Check if field name is legacy format.

    Args:
        field: Field name to check

    Returns:
        True if field is a legacy field name
    """
    return field in LEGACY_TO_COMPACT


def detect_format(entry: LogDict) -> LogFormat:
    """Detect log format from entry fields.

    Args:
        entry: Log entry dictionary

    Returns:
        LogFormat.COMPACT, LogFormat.LEGACY, or LogFormat.UNKNOWN
    """
    # Check for compact fields (prioritize compact)
    compact_count = sum(1 for f in (TS, TID, LVL, MT, AT, ST, DUR) if f in entry)

    # Check for legacy fields
    legacy_count = sum(1 for f in (TIMESTAMP, TASK_UUID, TASK_LEVEL, MESSAGE_TYPE,
                                   ACTION_TYPE, ACTION_STATUS, DURATION_NS)
                       if f in entry)

    if compact_count >= 2:
        return LogFormat.COMPACT
    if legacy_count >= 2:
        return LogFormat.LEGACY
    return LogFormat.UNKNOWN


def get_field(entry: LogDict, compact_name: str, default: Any = None) -> Any:
    """Get field value, checking both compact and legacy names.

    Args:
        entry: Log entry dictionary
        compact_name: Compact field name (e.g., "ts", "tid")
        default: Default value if not found

    Returns:
        Field value or default
    """
    # Try compact first
    if compact_name in entry:
        return entry[compact_name]

    # Try legacy name
    legacy_name = COMPACT_TO_LEGACY.get(compact_name)
    if legacy_name and legacy_name in entry:
        return entry[legacy_name]

    return default


def get_level_name(level: Level | str) -> str:
    """Get string name from Level enum or string.

    Args:
        level: Either a Level enum or string level name.

    Returns:
        The lowercase string level name.
    """
    match level:
        case Level():
            return level.name.lower()
        case str():
            return level.lower()
        case _:
            raise TypeError(f"Invalid level type: {type(level)}")


def get_level_value(level: str | int | Level) -> Level:
    """Get Level enum from string, int, or Level.

    Args:
        level: String name, int value, or Level enum.

    Returns:
        Corresponding Level enum value.

    Raises:
        ValueError: If level string is not recognized.
    """
    match level:
        case Level():
            return level
        case int():
            return Level(level)
        case str():
            try:
                return Level[level.upper()]
            except KeyError as exc:
                raise ValueError(f"Unknown level: {level}") from exc
        case _:
            raise TypeError(f"Invalid level type: {type(level)}")


__all__ = [
    # Type aliases
    "LogEntry", "LogDict", "TaskLevelTuple", "TaskLevel", "ActionStatusLiteral",
    "FieldDict", "ContextDict", "MessageDict",
    # Compact field names
    "TS", "TID", "LVL", "MT", "AT", "ST", "DUR", "MSG",
    # Legacy field names
    "TIMESTAMP", "TASK_UUID", "TASK_LEVEL", "MESSAGE_TYPE",
    "ACTION_TYPE", "ACTION_STATUS", "DURATION_NS", "MESSAGE",
    # Legacy aliases
    "TASK_UUID_ALIAS", "TASK_LEVEL_ALIAS", "TIMESTAMP_ALIAS",
    "MESSAGE_TYPE_ALIAS", "ACTION_TYPE_ALIAS", "ACTION_STATUS_ALIAS",
    "DURATION_NS_ALIAS",
    # Mappings
    "LEGACY_TO_COMPACT", "COMPACT_TO_LEGACY", "ALL_KNOWN_FIELDS",
    # Level enums
    "Level", "LevelName", "LevelStr", "LevelValue", "LEVEL_VALUES",
    # Action status enums
    "ActionStatusStr", "ActionStatus",
    # Log format
    "LogFormat", "MESSAGE_TYPE_PREFIX",
    # Utility functions
    "normalize_field_name", "legacy_field_name",
    "is_compact_field", "is_legacy_field",
    "detect_format", "get_field",
    "get_level_name", "get_level_value",
]
