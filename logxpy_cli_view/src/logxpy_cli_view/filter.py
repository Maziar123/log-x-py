"""Filter functions for Eliot tasks."""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from functools import cache
from typing import Any

import jmespath

from logxpy_cli_view._compat import get

UTC = timezone.utc


@cache
def _compile_jmespath(query: str) -> jmespath.parser.ParsedResult:
    """Compile and cache JMESPath query expression."""
    return jmespath.compile(query)


def filter_by_jmespath(query: str) -> Callable[[dict[str, Any]], bool]:
    """Filter by JMESPath query expression."""
    expn = _compile_jmespath(query)
    def _filter(task: dict[str, Any]) -> bool:
        return bool(expn.search(task))
    return _filter


def filter_by_uuid(task_uuid: str) -> Callable[[dict[str, Any]], bool]:
    """Filter by task UUID."""
    return filter_by_jmespath(f"task_uuid == `{task_uuid}`")


def _parse_timestamp(timestamp: float) -> datetime:
    """Parse timestamp to UTC datetime."""
    return datetime.fromtimestamp(timestamp, tz=UTC)


def filter_by_start_date(start_date: datetime) -> Callable[[dict[str, Any]], bool]:
    """Filter tasks with timestamps >= start_date."""
    def _filter(task: dict[str, Any]) -> bool:
        ts = get(task, "ts")
        if ts is None:
            return False
        return _parse_timestamp(ts) >= start_date
    return _filter


def filter_by_end_date(end_date: datetime) -> Callable[[dict[str, Any]], bool]:
    """Filter tasks with timestamps < end_date."""
    def _filter(task: dict[str, Any]) -> bool:
        ts = get(task, "ts")
        if ts is None:
            return False
        return _parse_timestamp(ts) < end_date
    return _filter


def filter_by_relative_time(lookback: timedelta) -> Callable[[dict[str, Any]], bool]:
    """Filter tasks within relative time window from now."""
    cutoff = datetime.now(UTC) - lookback
    return filter_by_start_date(cutoff)


def filter_by_action_status(status: str) -> Callable[[dict[str, Any]], bool]:
    """Filter by action status (started, succeeded, failed)."""
    return filter_by_jmespath(f"action_status == `{status}`")


def filter_by_action_type(pattern: str, regex: bool = False) -> Callable[[dict[str, Any]], bool]:
    """Filter by action type (supports regex)."""
    if regex:
        compiled = re.compile(pattern)
        def _filter(task: dict[str, Any]) -> bool:
            return bool(compiled.search(get(task, "at", "")))
        return _filter
    return filter_by_jmespath(f"at == `{pattern}` || action_type == `{pattern}`")


def filter_by_field_exists(field_path: str) -> Callable[[dict[str, Any]], bool]:
    """Filter tasks that have specified field (dot notation supported)."""
    def _filter(task: dict[str, Any]) -> bool:
        current: Any = task
        for part in field_path.split("."):
            if not isinstance(current, dict) or part not in current:
                return False
            current = current[part]
        return True
    return _filter


def filter_by_keyword(keyword: str, case_sensitive: bool = False) -> Callable[[dict[str, Any]], bool]:
    """Filter tasks containing keyword in any field (deep search)."""
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

    return lambda task: _search(task)


def filter_by_task_level(min_level: int | None = None, max_level: int | None = None) -> Callable[[dict[str, Any]], bool]:
    """Filter tasks by depth level."""
    def _filter(task: dict[str, Any]) -> bool:
        level = get(task, "lvl", [])
        depth = len(level) if isinstance(level, list) else 1
        if min_level is not None and depth < min_level:
            return False
        if max_level is not None and depth > max_level:
            return False
        return True
    return _filter


def filter_by_duration(min_seconds: float | None = None, max_seconds: float | None = None) -> Callable[[dict[str, Any]], bool]:
    """Filter tasks by duration."""
    def _filter(task: dict[str, Any]) -> bool:
        duration = get(task, "dur")
        if duration is None:
            return False
        if min_seconds is not None and duration < min_seconds:
            return False
        if max_seconds is not None and duration > max_seconds:
            return False
        return True
    return _filter


def filter_sample(every_n: int) -> Callable[[dict[str, Any]], bool]:
    """Sample every Nth task."""
    counter = [0]
    def _filter(task: dict[str, Any]) -> bool:
        counter[0] += 1
        return (counter[0] - 1) % every_n == 0
    return _filter


def combine_filters_and(*filters: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    """Combine filters with AND logic."""
    return lambda value: all(f(value) for f in filters)


def combine_filters_or(*filters: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    """Combine filters with OR logic."""
    return lambda value: any(f(value) for f in filters)


def combine_filters_not(filter_fn: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    """Negate a filter (NOT logic)."""
    return lambda value: not filter_fn(value)


__all__ = [
    "combine_filters_and",
    "combine_filters_not",
    "combine_filters_or",
    "filter_by_action_status",
    "filter_by_action_type",
    "filter_by_duration",
    "filter_by_end_date",
    "filter_by_field_exists",
    "filter_by_jmespath",
    "filter_by_keyword",
    "filter_by_relative_time",
    "filter_by_start_date",
    "filter_by_task_level",
    "filter_by_uuid",
    "filter_sample",
]
