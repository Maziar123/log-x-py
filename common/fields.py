"""Shared field normalization and extraction utilities.

This module provides utilities for working with LogXPy log entries,
supporting both compact and legacy field naming conventions.

Functions extract field values while handling both formats transparently.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime
from typing import Any

from .types import (
    AT,
    ACTION_STATUS,
    ACTION_TYPE,
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
)


# ============================================================================
# Field Value Extraction
# ============================================================================

def get_field_value(entry: LogDict, compact_name: str, default: Any = None) -> Any:
    """Get field value, checking both compact and legacy names.

    Compact names are checked first for performance with new format.

    Args:
        entry: Log entry dictionary
        compact_name: Compact field name (e.g., "ts", "tid")
        default: Default value if not found

    Returns:
        Field value or default
    """
    # Try compact first (fast path for new format)
    if compact_name in entry:
        return entry[compact_name]

    # Try legacy name
    legacy_map = {
        TS: TIMESTAMP,
        TID: TASK_UUID,
        LVL: TASK_LEVEL,
        MT: MESSAGE_TYPE,
        AT: ACTION_TYPE,
        ST: ACTION_STATUS,
        DUR: DURATION_NS,
        MSG: MESSAGE,
    }
    legacy_name = legacy_map.get(compact_name)
    if legacy_name and legacy_name in entry:
        return entry[legacy_name]

    return default


def get_timestamp(entry: LogDict) -> float:
    """Extract timestamp from entry in seconds.

    Args:
        entry: Log entry dictionary

    Returns:
        Timestamp as float (seconds since epoch)
    """
    ts = get_field_value(entry, TS, 0)
    if isinstance(ts, str):
        try:
            return float(ts)
        except ValueError:
            return 0.0
    if isinstance(ts, (int, float)):
        return float(ts)
    return 0.0


def get_task_uuid(entry: LogDict) -> str:
    """Extract task UUID/TID from entry.

    Args:
        entry: Log entry dictionary

    Returns:
        Task UUID string
    """
    tid = get_field_value(entry, TID, "")
    return str(tid) if tid else ""


def get_task_level(entry: LogDict) -> tuple[int, ...]:
    """Extract task level from entry.

    Args:
        entry: Log entry dictionary

    Returns:
        Task level tuple
    """
    lvl = get_field_value(entry, LVL, [])
    if isinstance(lvl, list):
        return tuple(int(x) if isinstance(x, (int, float)) else 0 for x in lvl if x is not None)
    if isinstance(lvl, tuple):
        return lvl
    if isinstance(lvl, str):
        # String format: "/1" or "/1/1"
        if lvl.startswith("/"):
            parts = lvl[1:].split("/") if lvl != "/" else []
        else:
            parts = lvl.split("/")
        return tuple(int(p) for p in parts if p)
    return ()


def get_action_type(entry: LogDict) -> str | None:
    """Extract action type from entry.

    Args:
        entry: Log entry dictionary

    Returns:
        Action type string or None
    """
    return get_field_value(entry, AT)


def get_action_status(entry: LogDict) -> ActionStatus | None:
    """Extract action status from entry.

    Args:
        entry: Log entry dictionary

    Returns:
        ActionStatus enum or None
    """
    st = get_field_value(entry, ST)
    if st:
        try:
            return ActionStatus(st)
        except ValueError:
            pass
    return None


def get_message(entry: LogDict) -> str | None:
    """Extract message from entry.

    Args:
        entry: Log entry dictionary

    Returns:
        Message string or None
    """
    return get_field_value(entry, MSG)


def get_message_type(entry: LogDict) -> str | None:
    """Extract message type from entry.

    Args:
        entry: Log entry dictionary

    Returns:
        Message type string or None
    """
    return get_field_value(entry, MT)


# ============================================================================
# Duration Utilities
# ============================================================================

def extract_duration(entry: LogDict) -> float | None:
    """Extract duration from entry, handling both compact and legacy formats.

    CRITICAL: The new 'dur' field is in SECONDS, not nanoseconds!
    Legacy 'duration_ns' is in nanoseconds.

    Args:
        entry: Log entry dictionary

    Returns:
        Duration in seconds, or None if not found
    """
    # Check compact 'dur' first (seconds, new format)
    if DUR in entry:
        dur_val = entry[DUR]
        if dur_val is not None and not isinstance(dur_val, bool):
            return float(dur_val)

    # Check legacy 'duration_ns' (nanoseconds)
    if DURATION_NS in entry:
        dur_val = entry[DURATION_NS]
        if dur_val is not None and not isinstance(dur_val, bool):
            return float(dur_val) / 1e9  # Convert ns to seconds

    # Check other possible duration fields
    for field in ("logxpy:duration", "eliot:duration", "duration"):
        if field in entry:
            dur_val = entry[field]
            if dur_val is not None and not isinstance(dur_val, bool):
                # Assume seconds for these fields
                return float(dur_val)

    return None


def parse_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        str: Human-readable duration (e.g., "1h 23m 45.123s").
    """
    if seconds < 0:
        return f"-{parse_duration(-seconds)}"

    if seconds < 1e-6:
        return f"{seconds * 1e9:.3f}ns"
    if seconds < 1e-3:
        return f"{seconds * 1e6:.3f}µs"
    if seconds < 1:
        return f"{seconds * 1e3:.3f}ms"

    parts = []
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{secs:.3f}s")

    return " ".join(parts)


# ============================================================================
# Timestamp Utilities
# ============================================================================

def parse_timestamp(ts: float | str) -> datetime:
    """Parse a Unix timestamp to datetime.

    Args:
        ts: Unix timestamp (seconds since epoch) as float or string.

    Returns:
        datetime: Parsed datetime object.
    """
    if isinstance(ts, str):
        ts = float(ts)
    return datetime.fromtimestamp(ts)


def format_timestamp(ts: float | str, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a Unix timestamp to string.

    Args:
        ts: Unix timestamp (seconds since epoch).
        fmt: Format string for datetime.strftime().

    Returns:
        str: Formatted timestamp string.
    """
    if isinstance(ts, str):
        ts = float(ts)
    return datetime.fromtimestamp(ts).strftime(fmt)


# ============================================================================
# Entry Normalization
# ============================================================================

from .types import LEGACY_TO_COMPACT


def normalize_entry(entry: LogDict) -> LogDict:
    """Convert legacy field names to compact format in-place.

    Args:
        entry: Log entry with potentially mixed field names

    Returns:
        Normalized entry with compact field names
    """
    normalized: LogDict = {}
    for key, value in entry.items():
        compact_key = LEGACY_TO_COMPACT.get(key, key)
        normalized[compact_key] = value
    return normalized


# ============================================================================
# Entry Extraction Utilities
# ============================================================================

from more_itertools import unique_everseen  # type: ignore


def extract_task_uuids(entries: Iterable[Any]) -> set[str]:
    """Extract all unique task UUIDs from log entries.

    Uses more-itertools unique_everseen for efficient deduplication.

    Args:
        entries: Iterable of log entries (dict or LogEntry objects).

    Returns:
        set[str]: Set of unique task UUIDs.
    """
    def get_uuid(entry: Any) -> str | None:
        if isinstance(entry, dict):
            return get_task_uuid(entry)
        return getattr(entry, "task_uuid", None)

    return set(unique_everseen(filter(None, (get_uuid(e) for e in entries))))


__all__ = [
    # Field extraction
    "get_field_value", "get_timestamp", "get_task_uuid", "get_task_level",
    "get_action_type", "get_action_status", "get_message", "get_message_type",
    # Duration
    "extract_duration", "parse_duration",
    # Timestamp
    "parse_timestamp", "format_timestamp",
    # Normalization
    "normalize_entry",
    # Extraction
    "extract_task_uuids",
]
