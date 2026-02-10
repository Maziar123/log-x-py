"""Shared filter predicates for LogXPy log entries.

This module provides common predicate functions for filtering log entries.
These are pure functions that return bool, usable across all subprojects.

Python 3.12+ features used:
- Pattern matching (PEP 634): Clean value routing
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import datetime
from math import inf
from typing import Any

from .fields import (
    extract_duration,
    get_action_status,
    get_action_type,
    get_field_value,
    get_message,
    get_message_type,
    get_task_level,
    get_timestamp,
)
from .types import (
    AT,
    DUR,
    LVL,
    MSG,
    MT,
    ST,
    TID,
    ActionStatus,
    Level,
    LogDict,
)


# ============================================================================
# Level Predicates
# ============================================================================

def by_level(*levels: str | Level) -> Callable[[LogDict], bool]:
    """Create predicate that filters by log level(s).

    Args:
        *levels: One or more log levels to include (str or Level enum)

    Returns:
        Predicate function that returns True if entry matches any level
    """
    level_set = {lvl if isinstance(lvl, str) else lvl.value for lvl in levels}

    def _predicate(entry: LogDict) -> bool:
        mt = get_field_value(entry, MT, "")
        if mt:
            mt_lower = str(mt).lower()
            # Handle both compact format ("info", "error") and legacy ("loggerx:info")
            if "loggerx:" in mt_lower:
                level_part = mt_lower.split("loggerx:")[-1]
                return level_part in level_set
            return mt_lower in level_set
        return False

    return _predicate


def is_debug(entry: LogDict) -> bool:
    """Check if entry is DEBUG level."""
    return by_level(Level.DEBUG)(entry)


def is_info(entry: LogDict) -> bool:
    """Check if entry is INFO level."""
    return by_level(Level.INFO)(entry)


def is_warning(entry: LogDict) -> bool:
    """Check if entry is WARNING level."""
    return by_level(Level.WARNING)(entry)


def is_error(entry: LogDict) -> bool:
    """Check if entry is ERROR or CRITICAL level."""
    return by_level(Level.ERROR, Level.CRITICAL)(entry)


def is_critical(entry: LogDict) -> bool:
    """Check if entry is CRITICAL level."""
    return by_level(Level.CRITICAL)(entry)


# ============================================================================
# Action Type Predicates
# ============================================================================

def by_action_type(*types: str) -> Callable[[LogDict], bool]:
    """Create predicate that filters by action type(s).

    Args:
        *types: One or more action types to include

    Returns:
        Predicate function that returns True if entry matches any type
    """
    type_set = set(types)

    def _predicate(entry: LogDict) -> bool:
        at = get_action_type(entry)
        return at in type_set if at else False

    return _predicate


def by_action_type_pattern(pattern: str, regex: bool = False) -> Callable[[LogDict], bool]:
    """Create predicate that filters by action type pattern.

    Args:
        pattern: Pattern to match (glob or regex)
        regex: If True, treat pattern as regex; otherwise use glob-style matching

    Returns:
        Predicate function that returns True if action type matches
    """
    if regex:
        compiled = re.compile(pattern)

        def _predicate(entry: LogDict) -> bool:
            at = get_action_type(entry)
            return bool(at and compiled.search(at))
    else:
        # Simple glob-style matching (convert * to .*, ? to .)
        regex_pattern = "^" + pattern.replace("*", ".*").replace("?", ".") + "$"
        compiled = re.compile(regex_pattern, re.IGNORECASE)

        def _predicate(entry: LogDict) -> bool:
            at = get_action_type(entry)
            return bool(at and compiled.match(at))

    return _predicate


# ============================================================================
# Status Predicates
# ============================================================================

def by_status(status: ActionStatus | str) -> Callable[[LogDict], bool]:
    """Create predicate that filters by action status.

    Args:
        status: Action status to filter by

    Returns:
        Predicate function that returns True if entry matches status
    """
    status_str = status if isinstance(status, str) else status.value

    def _predicate(entry: LogDict) -> bool:
        st = get_action_status(entry)
        return st.value == status_str if st else False

    return _predicate


def is_started(entry: LogDict) -> bool:
    """Check if entry has started status."""
    return by_status(ActionStatus.STARTED)(entry)


def is_succeeded(entry: LogDict) -> bool:
    """Check if entry has succeeded status."""
    return by_status(ActionStatus.SUCCEEDED)(entry)


def is_failed(entry: LogDict) -> bool:
    """Check if entry has failed status."""
    return by_status(ActionStatus.FAILED)(entry)


def has_traceback(entry: LogDict) -> bool:
    """Check if entry has traceback information."""
    return "traceback" in entry or "exc" in entry or "exception" in entry


# ============================================================================
# Duration Predicates
# ============================================================================

def by_duration(
    min_seconds: float = 0,
    max_seconds: float = inf,
) -> Callable[[LogDict], bool]:
    """Create predicate that filters by duration.

    Args:
        min_seconds: Minimum duration in seconds (inclusive)
        max_seconds: Maximum duration in seconds (inclusive)

    Returns:
        Predicate function that returns True if duration is in range
    """
    def _predicate(entry: LogDict) -> bool:
        dur = extract_duration(entry)
        if dur is None:
            return False
        return min_seconds <= dur <= max_seconds

    return _predicate


def is_slow(threshold: float = 1.0) -> Callable[[LogDict], bool]:
    """Create predicate that filters for slow actions.

    Args:
        threshold: Duration threshold in seconds

    Returns:
        Predicate function that returns True if duration >= threshold
    """
    return by_duration(min_seconds=threshold)


def is_fast(threshold: float = 0.001) -> Callable[[LogDict], bool]:
    """Create predicate that filters for fast actions.

    Args:
        threshold: Duration threshold in seconds

    Returns:
        Predicate function that returns True if duration <= threshold
    """
    return by_duration(max_seconds=threshold)


# ============================================================================
# Time Predicates
# ============================================================================

def by_time_range(
    start: float | str | datetime,
    end: float | str | datetime,
) -> Callable[[LogDict], bool]:
    """Create predicate that filters by time range.

    Args:
        start: Start time (datetime, timestamp string, or float)
        end: End time (datetime, timestamp string, or float)

    Returns:
        Predicate function that returns True if timestamp is in range
    """
    # Convert start to timestamp
    start_ts: float
    if isinstance(start, str):
        start_ts = float(start)
    elif isinstance(start, datetime):
        start_ts = start.timestamp()
    else:
        start_ts = start

    # Convert end to timestamp
    end_ts: float
    if isinstance(end, str):
        end_ts = float(end)
    elif isinstance(end, datetime):
        end_ts = end.timestamp()
    else:
        end_ts = end

    def _predicate(entry: LogDict) -> bool:
        ts = get_timestamp(entry)
        return start_ts <= ts <= end_ts

    return _predicate


def after(timestamp: float | str | datetime) -> Callable[[LogDict], bool]:
    """Create predicate that filters entries after a timestamp.

    Args:
        timestamp: Timestamp to filter after

    Returns:
        Predicate function
    """
    ts_value: float
    if isinstance(timestamp, str):
        ts_value = float(timestamp)
    elif isinstance(timestamp, datetime):
        ts_value = timestamp.timestamp()
    else:
        ts_value = timestamp

    def _predicate(entry: LogDict) -> bool:
        return get_timestamp(entry) > ts_value

    return _predicate


def before(timestamp: float | str | datetime) -> Callable[[LogDict], bool]:
    """Create predicate that filters entries before a timestamp.

    Args:
        timestamp: Timestamp to filter before

    Returns:
        Predicate function
    """
    ts_value: float
    if isinstance(timestamp, str):
        ts_value = float(timestamp)
    elif isinstance(timestamp, datetime):
        ts_value = timestamp.timestamp()
    else:
        ts_value = timestamp

    def _predicate(entry: LogDict) -> bool:
        return get_timestamp(entry) < ts_value

    return _predicate


# ============================================================================
# Task/UUID Predicates
# ============================================================================

def by_task_uuid(*uuids: str) -> Callable[[LogDict], bool]:
    """Create predicate that filters by task UUID(s).

    Args:
        *uuids: One or more task UUIDs to include

    Returns:
        Predicate function
    """
    uuid_set = set(uuids)

    def _predicate(entry: LogDict) -> bool:
        tid = get_field_value(entry, TID, "")
        return tid in uuid_set

    return _predicate


def by_nesting_level(
    min_depth: int = 1,
    max_depth: int = 99,
) -> Callable[[LogDict], bool]:
    """Create predicate that filters by nesting depth.

    Args:
        min_depth: Minimum depth to include
        max_depth: Maximum depth to include

    Returns:
        Predicate function
    """
    def _predicate(entry: LogDict) -> bool:
        lvl = get_task_level(entry)
        depth = len(lvl)
        return min_depth <= depth <= max_depth

    return _predicate


# ============================================================================
# Content Predicates
# ============================================================================

def by_message(pattern: str, regex: bool = False) -> Callable[[LogDict], bool]:
    """Create predicate that filters by message content.

    Args:
        pattern: Text pattern to match
        regex: Use regex matching if True

    Returns:
        Predicate function
    """
    if regex:
        compiled = re.compile(pattern, re.IGNORECASE)

        def _predicate(entry: LogDict) -> bool:
            msg = get_message(entry)
            return bool(msg and compiled.search(msg))
    else:
        pattern_lower = pattern.lower()

        def _predicate(entry: LogDict) -> bool:
            msg = get_message(entry)
            return bool(msg and pattern_lower in msg.lower())

    return _predicate


def by_keyword(keyword: str, case_sensitive: bool = False) -> Callable[[LogDict], bool]:
    """Create predicate that filters by keyword in any field.

    Performs deep search through nested structures.

    Args:
        keyword: Keyword to search for
        case_sensitive: If True, case-sensitive search

    Returns:
        Predicate function
    """
    keyword_cmp = keyword if case_sensitive else keyword.lower()

    def _search(value: Any) -> bool:
        if isinstance(value, str):
            text = value if case_sensitive else value.lower()
            return keyword_cmp in text
        elif isinstance(value, dict):
            return any(_search(v) for v in value.values())
        elif isinstance(value, (list, tuple)):
            return any(_search(item) for item in value)
        return False

    def _predicate(entry: LogDict) -> bool:
        return _search(entry)

    return _predicate


def by_field_exists(field_path: str) -> Callable[[LogDict], bool]:
    """Create predicate that checks if a field exists (dot notation supported).

    Args:
        field_path: Field path (e.g., "user.id" or "metadata")

    Returns:
        Predicate function
    """
    def _predicate(entry: LogDict) -> bool:
        current: Any = entry
        for part in field_path.split("."):
            if not isinstance(current, dict) or part not in current:
                return False
            current = current[part]
        return True

    return _predicate


def by_field(field: str, value: Any) -> Callable[[LogDict], bool]:
    """Create predicate that filters by exact field value.

    Args:
        field: Field name to check
        value: Value to match

    Returns:
        Predicate function
    """
    def _predicate(entry: LogDict) -> bool:
        return get_field_value(entry, field) == value

    return _predicate


def by_field_contains(field: str, value: Any) -> Callable[[LogDict], bool]:
    """Create predicate that filters by field containing a value.

    Args:
        field: Field name to check
        value: Value to search for (substring for strings)

    Returns:
        Predicate function
    """
    def _predicate(entry: LogDict) -> bool:
        field_value = get_field_value(entry, field)
        if field_value is None:
            return False
        if isinstance(field_value, str) and isinstance(value, str):
            return value.lower() in field_value.lower()
        return bool(field_value == value)

    return _predicate


# ============================================================================
# Combinators
# ============================================================================

def combine_and(*predicates: Callable[[LogDict], bool]) -> Callable[[LogDict], bool]:
    """Combine predicates with AND logic.

    Args:
        *predicates: Predicate functions to combine

    Returns:
        Combined predicate function
    """
    def _combined(value: LogDict) -> bool:
        return all(p(value) for p in predicates)
    return _combined


def combine_or(*predicates: Callable[[LogDict], bool]) -> Callable[[LogDict], bool]:
    """Combine predicates with OR logic.

    Args:
        *predicates: Predicate functions to combine

    Returns:
        Combined predicate function
    """
    def _combined(value: LogDict) -> bool:
        return any(p(value) for p in predicates)
    return _combined


def combine_not(predicate: Callable[[LogDict], bool]) -> Callable[[LogDict], bool]:
    """Negate a predicate (NOT logic).

    Args:
        predicate: Predicate function to negate

    Returns:
        Negated predicate function
    """
    def _negated(value: LogDict) -> bool:
        return not predicate(value)
    return _negated


__all__ = [
    # Level predicates
    "by_level", "is_debug", "is_info", "is_warning", "is_error", "is_critical",
    # Action type predicates
    "by_action_type", "by_action_type_pattern",
    # Status predicates
    "by_status", "is_started", "is_succeeded", "is_failed", "has_traceback",
    # Duration predicates
    "by_duration", "is_slow", "is_fast",
    # Time predicates
    "by_time_range", "after", "before",
    # Task predicates
    "by_task_uuid", "by_nesting_level",
    # Content predicates
    "by_message", "by_keyword", "by_field_exists", "by_field", "by_field_contains",
    # Combinators
    "combine_and", "combine_or", "combine_not",
]
