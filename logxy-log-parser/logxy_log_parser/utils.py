"""
Utility functions for logxy-log-parser.

Helper functions for timestamp parsing, duration formatting, and other common operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .types import Level


def parse_timestamp(ts: float) -> datetime:
    """Parse a Unix timestamp to datetime.

    Args:
        ts: Unix timestamp (seconds since epoch).

    Returns:
        datetime: Parsed datetime object.
    """
    return datetime.fromtimestamp(ts)


def format_timestamp(ts: float, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a Unix timestamp to string.

    Args:
        ts: Unix timestamp (seconds since epoch).
        fmt: Format string for datetime.strftime().

    Returns:
        str: Formatted timestamp string.
    """
    return datetime.fromtimestamp(ts).strftime(fmt)


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


def level_from_message_type(message_type: str) -> Level:
    """Extract log level from message type.

    Args:
        message_type: The message_type field from a log entry.

    Returns:
        Level: The corresponding log level.
    """
    # Message type format is "loggerx:LEVEL" e.g., "loggerx:info", "loggerx:error"
    if "loggerx:" in message_type:
        level_part = message_type.split("loggerx:")[1].lower()
        # Map to Level enum
        level_map = {
            "debug": Level.DEBUG,
            "info": Level.INFO,
            "success": Level.SUCCESS,
            "note": Level.NOTE,
            "warning": Level.WARNING,
            "error": Level.ERROR,
            "critical": Level.CRITICAL,
        }
        return level_map.get(level_part, Level.INFO)

    # Fallback for old format
    if message_type.endswith(":message"):
        return Level.INFO
    if message_type.endswith(":start_action"):
        return Level.INFO
    if message_type.endswith(":end_action"):
        return Level.SUCCESS
    if message_type.endswith(":failed"):
        return Level.ERROR
    return Level.INFO


def extract_task_uuid(entries: list[Any]) -> set[str]:
    """Extract all unique task UUIDs from log entries.

    Args:
        entries: List of log entries (dict or LogEntry objects).

    Returns:
        set[str]: Set of unique task UUIDs.
    """
    uuids = set()
    for entry in entries:
        if isinstance(entry, dict):
            uuid = entry.get("task_uuid")
        else:
            uuid = getattr(entry, "task_uuid", None)
        if uuid:
            uuids.add(uuid)
    return uuids


def merge_fields(*dicts: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple dictionaries into one.

    Later dictionaries override earlier ones for duplicate keys.

    Args:
        *dicts: Dictionaries to merge.

    Returns:
        dict[str, Any]: Merged dictionary.
    """
    result: dict[str, Any] = {}
    for d in dicts:
        result.update(d)
    return result
