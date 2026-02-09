"""Utility functions for logxy-log-parser.

Helper functions for timestamp parsing, duration formatting, field normalization,
and other common operations.

Uses boltons and more-itertools libraries for enhanced dictionary and iteration utilities.

Python 3.12+ features used:
- Type aliases (PEP 695): `type Name = ...`
- Pattern matching (PEP 634): Clean value routing
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime
from typing import Any

import boltons.dictutils as du
import boltons.iterutils as iu
from more_itertools import chunked
from more_itertools import pairwise as _pairwise
from more_itertools import unique_everseen
from more_itertools import windowed as _windowed

from .types import (
    ACTION_STATUS,
    ACTION_TYPE,
    AT,
    DUR,
    DURATION_NS,
    LEGACY_TO_COMPACT,
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
    Level,
    LogDict,
)

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
# Duration Utilities
# ============================================================================

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


# ============================================================================
# Level Detection
# ============================================================================

def level_from_message_type(message_type: str) -> Level:
    """Extract log level from message type.

    Handles both new LoggerX format ("loggerx:LEVEL") and legacy Eliot format.

    Args:
        message_type: The message_type field from a log entry.

    Returns:
        Level: The corresponding log level.
    """
    # Map message type suffixes to levels
    suffix_map: dict[str, Level] = {
        ":message": Level.INFO,
        ":start_action": Level.INFO,
        ":end_action": Level.SUCCESS,
        ":failed": Level.ERROR,
    }

    # LoggerX format: "loggerx:LEVEL"
    if "loggerx:" in message_type:
        level_part = message_type.split("loggerx:")[1].lower()
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

    # Direct level name (compact format)
    if message_type in Level.__members__.values():
        return Level(message_type)

    # Legacy suffixes
    for suffix, level in suffix_map.items():
        if message_type.endswith(suffix):
            return level

    return Level.INFO


def level_from_entry(entry: LogDict) -> Level:
    """Extract log level from entry, checking multiple sources.

    Priority:
    1. 'level' field (direct)
    2. 'mt' / 'message_type' field
    3. Action status (failed -> error)

    Args:
        entry: Log entry dictionary

    Returns:
        Level: The detected log level
    """
    # Check direct 'level' field first
    if "level" in entry:
        level_val = entry["level"]
        if isinstance(level_val, str):
            try:
                return Level(level_val.lower())
            except ValueError:
                pass

    # Check message type
    mt = get_field_value(entry, MT, "")
    if mt:
        return level_from_message_type(str(mt))

    # Check action status
    st = get_field_value(entry, ST, "")
    if st == "failed":
        return Level.ERROR

    return Level.INFO


# ============================================================================
# Field Normalization
# ============================================================================

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


# ============================================================================
# Entry Extraction Utilities
# ============================================================================

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


# ============================================================================
# Dictionary Utilities (boltons wrapper)
# ============================================================================

def merge_fields(*dicts: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple dictionaries into one.

    Later dictionaries override earlier ones for duplicate keys.
    Uses boltons.iterutils for enhanced merging capabilities.

    Args:
        *dicts: Dictionaries to merge.

    Returns:
        dict[str, Any]: Merged dictionary.
    """
    result: dict[str, Any] = {}
    for d in dicts:
        result.update(d)
    return result


def subdict(d: dict[str, Any], keys: set[str] | list[str] | tuple[str, ...]) -> dict[str, Any]:
    """Extract a subset of dictionary keys.

    Args:
        d: Source dictionary.
        keys: Keys to extract.

    Returns:
        dict[str, Any]: Dictionary with only the specified keys.
    """
    return du.subdict(d, keys)  # type: ignore[no-any-return]


def remap_entry(entry: LogDict, func: Callable[[str, Any], tuple[str, Any] | None]) -> LogDict:
    """Remap entry fields using a function.

    Uses boltons.iterutils.remap for deep transformation.

    Args:
        entry: Source entry dictionary
        func: Function that takes (path, key, value) and returns
              (new_key, new_value) or None to remove

    Returns:
        Remapped dictionary
    """
    return iu.remap(entry, func)  # type: ignore


# ============================================================================
# Batch Processing Utilities (more-itertools wrapper)
# ============================================================================

def process_in_batches(
    items: Iterable[Any],
    batch_size: int,
    func: Callable[[list[Any]], Any],
) -> list[Any]:
    """Process items in batches using more-itertools.chunked.

    Args:
        items: Iterable of items to process
        batch_size: Size of each batch
        func: Function to call with each batch

    Returns:
        List of results from each batch
    """
    results = []
    for batch in chunked(items, batch_size):
        results.append(func(list(batch)))
    return results


# ============================================================================
# Re-exports (boltons + more-itertools)
# ============================================================================

# boltons.iterutils
bucketize = iu.bucketize
first = iu.first
is_iterable = iu.is_iterable
split = iu.split
unique = iu.unique
flatten = iu.flatten

# boltons.dictutils
OMD = du.OMD  # type: ignore[type-arg]
OrderedMultiDict = du.OrderedMultiDict

# more_itertools (re-export for convenience)
pairwise = _pairwise
windowed = _windowed


__all__ = [
    # Timestamp
    "parse_timestamp",
    "format_timestamp",
    # Duration
    "parse_duration",
    "extract_duration",
    # Level
    "level_from_message_type",
    "level_from_entry",
    # Field normalization
    "normalize_entry",
    "get_field_value",
    "get_timestamp",
    "get_task_uuid",
    "get_task_level",
    # Extraction
    "extract_task_uuids",
    # Dictionary
    "merge_fields",
    "subdict",
    "remap_entry",
    # Batch
    "process_in_batches",
    # boltons re-exports
    "bucketize",
    "chunked",
    "first",
    "is_iterable",
    "split",
    "unique",
    "flatten",
    "OMD",
    "OrderedMultiDict",
    # more-itertools re-exports
    "pairwise",
    "windowed",
    "unique_everseen",
]
