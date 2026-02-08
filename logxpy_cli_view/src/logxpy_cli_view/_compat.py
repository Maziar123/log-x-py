"""Field name compatibility layer for compact and legacy formats.

Supports both new compact format (ts, tid, mt) and legacy format (timestamp, task_uuid, message_type).
"""

from __future__ import annotations

import functools
import json
import warnings
from typing import Callable, TypeVar

# Field name mappings: compact -> list of possible names (compact first for fast path)
FIELD_MAP = {
    "ts": ["ts", "timestamp"],
    "tid": ["tid", "task_uuid"],
    "lvl": ["lvl", "task_level"],
    "mt": ["mt", "message_type"],
    "at": ["at", "action_type"],
    "st": ["st", "action_status"],
    "msg": ["msg", "message"],
    "dur": ["dur", "duration", "logxpy:duration"],
    "fg": ["fg", "logxpy:foreground"],
    "bg": ["bg", "logxpy:background"],
}


def get(data: dict, name: str, default=None):
    """Get field value, trying compact then legacy names.

    Args:
        data: Dictionary to search
        name: Compact field name (e.g., "ts", "tid")
        default: Default value if not found

    Returns:
        Field value or default

    Example:
        >>> entry = {"ts": 123.45, "tid": "Xa.1"}
        >>> get(entry, "ts")  # 123.45
        >>> get(entry, "timestamp")  # 123.45 (alias)
    """
    for key in FIELD_MAP.get(name, [name]):
        if key in data:
            return data[key]
    return default


def has(data: dict, name: str) -> bool:
    """Check if field exists (compact or legacy).

    Args:
        data: Dictionary to check
        name: Compact field name

    Returns:
        True if field exists
    """
    return any(key in data for key in FIELD_MAP.get(name, [name]))


def get_message_type(task: dict) -> str | None:
    """Get message type, handling both formats.

    Returns compact value (e.g., "info" not "loggerx:info").
    """
    mt = get(task, "mt")
    if mt and ":" in mt:
        # Legacy format "loggerx:info" -> "info"
        return mt.split(":")[-1]
    return mt


def get_timestamp(task: dict) -> float | None:
    """Get timestamp as float."""
    ts = get(task, "ts")
    if ts is None:
        return None
    if isinstance(ts, str):
        from datetime import datetime
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return float(ts)
    return float(ts)


# Export all compact field names for convenience
TS = "ts"
TID = "tid"
LVL = "lvl"
MT = "mt"
AT = "at"
ST = "st"
MSG = "msg"
DUR = "dur"
FG = "fg"
BG = "bg"


# =============================================================================
# Compatibility Utilities
# =============================================================================

F = TypeVar("F", bound=Callable)


def deprecated(message: str) -> Callable[[F], F]:
    """Decorator to mark a function/class as deprecated.

    Args:
        message: Deprecation message to display

    Returns:
        Decorator function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated. {message}",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)
        return wrapper  # type: ignore
    return decorator


def catch_errors(func: F) -> F:
    """Decorator to catch and log errors.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function that catches exceptions
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            warnings.warn(f"Error in {func.__name__}: {e}", RuntimeWarning)
            return None
    return wrapper  # type: ignore


def dump_json_bytes(data: dict) -> bytes:
    """Serialize data to JSON bytes.

    Args:
        data: Dictionary to serialize

    Returns:
        JSON-encoded bytes
    """
    return json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")


__all__ = [
    "get",
    "has",
    "get_message_type",
    "get_timestamp",
    "TS",
    "TID",
    "LVL",
    "MT",
    "AT",
    "ST",
    "MSG",
    "DUR",
    "FG",
    "BG",
    "FIELD_MAP",
    "deprecated",
    "catch_errors",
    "dump_json_bytes",
]
