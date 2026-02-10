"""Core types and protocols - logxpy-compatible field names.

Python 3.12+ features used:
- Type aliases (PEP 695): `type Name = ...`
- StrEnum (PEP 663): Type-safe string enums
- Dataclass slots (PEP 681): Memory optimization
- Runtime checkable protocols
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import Any, Literal, Protocol, runtime_checkable

from pyrsistent import pvector


# ============================================================================
# Type Aliases (PEP 695 - Python 3.12+)
# ============================================================================

type LogEntry = dict[str, Any]
type TaskLevelTuple = tuple[int, ...]
type ActionStatusLiteral = Literal["started", "succeeded", "failed"]
type FieldDict = dict[str, Any]
type ContextDict = dict[str, Any]
type MessageDict = dict[str, Any]


# ============================================================================
# LogXPy Field Name Constants
# ============================================================================

# Compact field names (minimize log size)
# Standard: 1-2 char abbreviations for common fields
TS: str = "ts"              # timestamp (was: timestamp)
TID: str = "tid"            # task_id (was: task_uuid)
LVL: str = "lvl"            # task_level (was: task_level)
MT: str = "mt"              # message_type (was: message_type)
AT: str = "at"              # action_type (was: action_type)
ST: str = "st"              # action_status (was: action_status)
DUR: str = "dur"            # duration (was: duration_ns)
MSG: str = "msg"            # message (common)

# Legacy field names (for backwards compatibility)
TASK_UUID: str = TID        # Alias: task_uuid -> tid
TASK_LEVEL: str = LVL       # Alias: task_level -> lvl
TIMESTAMP: str = TS         # Alias: timestamp -> ts
MESSAGE_TYPE: str = MT      # Alias: message_type -> mt
ACTION_TYPE: str = AT       # Alias: action_type -> at
ACTION_STATUS: str = ST     # Alias: action_status -> st
DURATION_NS: str = DUR      # Alias: duration_ns -> dur


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


class ActionStatusStr(StrEnum):
    """Action status values as string enum (PEP 663)."""
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


# ============================================================================
# TaskLevel Class
# ============================================================================
# Moved here to avoid circular import between _action and _message
# ============================================================================

class TaskLevel:
    """
    The location of a message within the tree of actions of a task.

    @ivar level: A list of integers. Each item indicates a child
        relationship, and the value indicates message count. E.g. [2, 3]
        indicates this is the third message within an action which is
        the second item in the task.
    """

    __slots__ = ("_level",)

    def __init__(self, level: list[int] | None = None):
        self._level: list[int] = level or []

    def as_list(self) -> list[int]:
        """Return the current level.

        @return: List of integers.
        """
        return self._level[:]

    # Backwards compatibility:
    @property
    def level(self) -> pvector:
        return pvector(self._level)

    def __lt__(self, other: TaskLevel) -> bool:
        return self._level < other._level

    def __le__(self, other: TaskLevel) -> bool:
        return self._level <= other._level

    def __gt__(self, other: TaskLevel) -> bool:
        return self._level > other._level

    def __ge__(self, other: TaskLevel) -> bool:
        return self._level >= other._level

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TaskLevel):
            return False
        return self._level == other._level

    def __hash__(self) -> int:
        return hash(tuple(self._level))

    @classmethod
    def from_string(cls, string: str) -> TaskLevel:
        """
        Convert a serialized Unicode string to a TaskLevel.

        @param string: Output of TaskLevel.to_string.
        @return: TaskLevel parsed from the string.
        """
        # Use list comprehension with walrus for cleaner parsing
        return cls(level=[int(i) for i in string.split("/") if i])

    def to_string(self) -> str:
        """
        Convert to a Unicode string, for serialization purposes.

        @return: str representation of the TaskLevel.
        """
        return "/" + "/".join(map(str, self._level))

    def next_sibling(self) -> TaskLevel:
        """
        Return the next TaskLevel, that is a task at the same level as this
        one, but one after.

        @return: TaskLevel which follows this one.
        """
        new_level = self._level[:]
        new_level[-1] += 1
        return TaskLevel(level=new_level)

    def child(self) -> TaskLevel:
        """
        Return a child of this TaskLevel.

        @return: TaskLevel which is the first child of this one.
        """
        new_level = self._level[:]
        new_level.append(1)
        return TaskLevel(level=new_level)

    def parent(self) -> TaskLevel | None:
        """
        Return the parent of this TaskLevel, or None if it doesn't have
        one.

        @return: TaskLevel which is the parent of this one.
        """
        if not self._level:
            return None
        return TaskLevel(level=self._level[:-1])

    def is_sibling_of(self, task_level: TaskLevel) -> bool:
        """
        Is this task a sibling of task_level?
        """
        return self.parent() == task_level.parent()

    # PEP 8 compatibility:
    from_string = from_string
    to_string = to_string


# ============================================================================
# Record Dataclass
# ============================================================================

@dataclass(frozen=True, slots=True)
class Record:
    """Immutable log record with structured logging field names.

    Uses slots (PEP 681) for ~40% memory reduction vs regular dataclass.
    Frozen for thread-safety and hashability.
    """

    timestamp: float  # Unix timestamp
    level: Level
    message: str
    fields: FieldDict
    context: ContextDict
    task_uuid: str  # Task identifier
    task_level: TaskLevel  # Hierarchical task level
    action_type: str | None = None
    action_status: ActionStatusStr | None = None
    message_type: str | None = None

    def to_dict(self) -> LogEntry:
        """Convert to structured logging dict format.

        Returns:
            A dict compatible with LogXPy log format.
        """
        d: LogEntry = {
            TIMESTAMP: self.timestamp,
            TASK_UUID: self.task_uuid,
            TASK_LEVEL: list(self.task_level),
            **self.context,
            **self.fields,
        }
        if self.message_type:
            d[MT] = self.message_type
            d[MSG] = self.message
        if self.action_type:
            d[ACTION_TYPE] = self.action_type
            if self.action_status:
                # Handle both ActionStatusStr enum and plain strings
                status = self.action_status.value if hasattr(self.action_status, "value") else self.action_status
                d[ACTION_STATUS] = status
        return d


# ============================================================================
# Protocols
# ============================================================================

@runtime_checkable
class Destination(Protocol):
    """Protocol for log output destinations.

    A destination can write records, flush buffers, and close resources.
    All methods are async for non-blocking I/O.
    """

    async def write(self, record: Record) -> None:
        """Write a log record to the destination."""

    async def flush(self) -> None:
        """Flush any buffered output."""

    async def close(self) -> None:
        """Close the destination and release resources."""


@runtime_checkable
class Formatter(Protocol):
    """Protocol for value formatters.

    Formatters know how to convert specific types into
    structured logging fields.
    """

    def supports(self, obj: Any) -> bool:
        """Check if this formatter supports the given object type."""

    def format(self, obj: Any, **opts: Any) -> FieldDict:
        """Format the object into a dict of log fields."""


# ============================================================================
# Type Helpers
# ============================================================================

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
