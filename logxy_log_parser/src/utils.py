"""Utility functions for logxy-log-parser.

Helper functions for level detection, field merging, batch processing,
and re-exports of shared utilities from common/.

Uses boltons and more-itertools libraries for enhanced dictionary and iteration utilities.

Python 3.12+ features used:
- Type aliases (PEP 695): `type Name = ...`
- Pattern matching (PEP 634): Clean value routing
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

import boltons.dictutils as du
import boltons.iterutils as iu

from common.types import (
    MT,
    ST,
    Level,
    LogDict,
)

# ============================================================================
# Re-exports from common.fields (shared with logxpy_cli_view)
# ============================================================================
from common.fields import (
    extract_duration,
    extract_task_uuids,
    format_timestamp,
    get_field_value,
    get_task_level,
    get_task_uuid,
    get_timestamp,
    normalize_entry,
    parse_duration,
    parse_timestamp,
)

# ============================================================================
# Re-exports from common.iterutils (more-itertools wrappers)
# ============================================================================
from common.iterutils import (
    chunked,
    first,
    flatten,
    pairwise,
    unique_everseen,
    windowed,
)

# ============================================================================
# Re-exports from common.dictutils (boltons wrappers)
# ============================================================================
from common.dictutils import OrderedMultiDict

# ============================================================================
# boltons.iterutils re-exports (not yet in common/)
# ============================================================================
bucketize = iu.bucketize
is_iterable = iu.is_iterable
split = iu.split
unique = iu.unique

# boltons.dictutils re-exports
OMD = du.OMD  # type: ignore[type-arg]


# ============================================================================
# Level Detection (parser-specific)
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
# Dictionary Utilities (parser-specific helpers)
# ============================================================================

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
# Batch Processing Utilities
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


__all__ = [
    # From common.fields (re-exported)
    "parse_timestamp",
    "format_timestamp",
    "parse_duration",
    "extract_duration",
    "normalize_entry",
    "get_field_value",
    "get_timestamp",
    "get_task_uuid",
    "get_task_level",
    "extract_task_uuids",
    # Parser-specific: Level
    "level_from_message_type",
    "level_from_entry",
    # Parser-specific: Dictionary
    "merge_fields",
    "subdict",
    "remap_entry",
    # Parser-specific: Batch
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
