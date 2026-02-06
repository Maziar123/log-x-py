"""Core types and protocols - logxpy-compatible field names."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Protocol, runtime_checkable

# LogXPy field names (compatible with structured logging format)
TASK_UUID = "task_uuid"
TASK_LEVEL = "task_level"
TIMESTAMP = "timestamp"
MESSAGE_TYPE = "message_type"
ACTION_TYPE = "action_type"
ACTION_STATUS = "action_status"


class Level(IntEnum):
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    NOTE = 26
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@dataclass(frozen=True, slots=True)
class Record:
    """Immutable log record with structured logging field names."""

    timestamp: float  # Unix timestamp
    level: Level
    message: str
    fields: dict[str, Any]
    context: dict[str, Any]
    task_uuid: str  # Task identifier
    task_level: tuple[int, ...]  # Hierarchical task level
    action_type: str | None = None
    action_status: str | None = None
    message_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to structured logging dict format."""
        d = {
            TIMESTAMP: self.timestamp,
            TASK_UUID: self.task_uuid,
            TASK_LEVEL: list(self.task_level),
            **self.context,
            **self.fields,
        }
        if self.message_type:
            d[MESSAGE_TYPE] = self.message_type
            d["message"] = self.message
        if self.action_type:
            d[ACTION_TYPE] = self.action_type
            d[ACTION_STATUS] = self.action_status
        return d


@runtime_checkable
class Destination(Protocol):
    async def write(self, record: Record) -> None: ...
    async def flush(self) -> None: ...
    async def close(self) -> None: ...


@runtime_checkable
class Formatter(Protocol):
    def supports(self, obj: Any) -> bool: ...
    def format(self, obj: Any, **opts: Any) -> dict[str, Any]: ...
