"""
Simple one-line API for logxy-log-parser.

Features (by priority):
a. Check presence - Verify if specific entries exist
b. Type & count - Identify entry types and count occurrences
c. Python-native - Work with results using standard itertools and list operations
d. Productive - Rich, ready-to-use log checking with minimal boilerplate

Example:
    >>> from logxy_log_parser import parse_log, check_log, analyze_log
    >>>
    >>> # One line to parse (returns list[LogEntry] - Python native!)
    >>> entries = parse_log("app.log")
    >>>
    >>> # Check presence
    >>> if check_log("app.log").has_error:
    ...     print("Errors found!")
    >>>
    >>> # Type & count
    >>> from logxy_log_parser import count_by, group_by
    >>> errors = count_by(entries, level="error")
    >>> by_action = group_by(entries, "action_type")
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from common.types import Level
from .core import LogEntry
from .utils import bucketize


# ============================================================================
# Check Result - Presence checks (Feature a)
# ============================================================================

@dataclass(frozen=True, slots=True)
class CheckResult:
    """Result of checking a log file.

    Feature: Check presence - has_error, has_level(), has_action(), contains()
    """
    entries: list[LogEntry]
    file_path: Path
    total_lines: int
    error_count: int = 0
    validation_errors: list[str] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.entries)

    def __iter__(self) -> Iterator[LogEntry]:
        return iter(self.entries)

    def __getitem__(self, index: int) -> LogEntry:
        return self.entries[index]

    @property
    def is_valid(self) -> bool:
        """Check if parsing was successful."""
        return len(self.validation_errors) == 0

    @property
    def has_error(self) -> bool:
        """Check if any error entries exist."""
        return any(e.is_error for e in self.entries)

    @property
    def has_critical(self) -> bool:
        """Check if any critical entries exist."""
        return any(e.level == Level.CRITICAL for e in self.entries)

    def has_level(self, *levels: str) -> bool:
        """Check if entries with specified levels exist."""
        level_set = set(Level(l) for l in levels)
        return any(e.level in level_set for e in self.entries)

    def has_action(self, *action_types: str) -> bool:
        """Check if entries with specified action types exist."""
        action_set = set(action_types)
        return any(e.action_type in action_set for e in self.entries if e.action_type)

    def has_field(self, field_name: str) -> bool:
        """Check if any entry contains the specified field."""
        return any(field_name in e.fields for e in self.entries)

    def contains(self, **criteria: Any) -> bool:
        """Check if entries matching all criteria exist.

        >>> result.contains(level="error")
        >>> result.contains(action_type="db:query", status="failed")
        """
        return any(
            all(
                getattr(e, k, None) == v
                or (k in e.fields and e.fields[k] == v)
                for k, v in criteria.items()
            )
            for e in self.entries
        )

    def find(self, **criteria: Any) -> list[LogEntry]:
        """Find all entries matching criteria."""
        return [
            e for e in self.entries
            if all(
                getattr(e, k, None) == v
                or (k in e.fields and e.fields[k] == v)
                for k, v in criteria.items()
            )
        ]

    def first(self, **criteria: Any) -> LogEntry | None:
        """Get first entry matching criteria."""
        for e in self.entries:
            if all(
                getattr(e, k, None) == v
                or (k in e.fields and e.fields[k] == v)
                for k, v in criteria.items()
            ):
                return e
        return None

    def count(self, **criteria: Any) -> int:
        """Count entries matching criteria."""
        return sum(
            1 for e in self.entries
            if all(
                getattr(e, k, None) == v
                or (k in e.fields and e.fields[k] == v)
                for k, v in criteria.items()
            )
        )

    def where(self, predicate: Callable[[LogEntry], bool]) -> list[LogEntry]:
        """Filter entries by predicate function."""
        return [e for e in self.entries if predicate(e)]


# ============================================================================
# Stats Result - Type & count (Feature b)
# ============================================================================

@dataclass(frozen=True, slots=True)
class LogStats:
    """Statistics for log entries.

    Feature: Type & count - pre-computed distributions
    """
    total: int
    level_counts: dict[str, int]
    action_counts: dict[str, int]
    task_count: int
    error_count: int
    max_depth: int
    has_duration: int

    @property
    def success_rate(self) -> float:
        """Get success rate (succeeded / total actions)."""
        started = self.action_counts.get("started", 0)
        if started == 0:
            return 0.0
        succeeded = self.action_counts.get("succeeded", 0)
        return succeeded / started

    @property
    def error_rate(self) -> float:
        """Get error rate."""
        if self.total == 0:
            return 0.0
        return self.error_count / self.total

    def summary(self) -> str:
        """Get formatted summary string."""
        return (
            f"Entries: {self.total}, "
            f"Tasks: {self.task_count}, "
            f"Errors: {self.error_count}, "
            f"Max Depth: {self.max_depth}"
        )


# ============================================================================
# Analysis Result - Productive (Feature d)
# ============================================================================

@dataclass(frozen=True, slots=True)
class AnalysisReport:
    """Complete analysis report.

    Feature: Productive - rich results with minimal code
    """
    file_path: Path
    check: CheckResult
    stats: LogStats
    slowest: list[tuple[str, float]]
    errors: list[LogEntry]

    def print_summary(self) -> None:
        """Print formatted summary to stdout."""
        print(f"\n📊 Log Analysis: {self.file_path.name}")
        print("=" * 50)
        print(self.stats.summary())
        print(f"  Levels: {self.stats.level_counts}")
        print(f"  Actions: {self.stats.action_counts}")
        if self.slowest:
            print("\n  Slowest actions:")
            for action, duration in self.slowest[:5]:
                print(f"    - {action}: {duration*1000:.2f}ms")
        if self.errors:
            print(f"\n  Errors: {len(self.errors)}")
            for e in self.errors[:3]:
                msg = e.message or e.message_type
                print(f"    - {msg[:60]}")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file": str(self.file_path),
            "total": self.stats.total,
            "tasks": self.stats.task_count,
            "errors": self.stats.error_count,
            "levels": self.stats.level_counts,
            "actions": self.stats.action_counts,
            "slowest": self.slowest,
            "error_rate": self.stats.error_rate,
        }


# ============================================================================
# One-Line API Functions
# ============================================================================

def parse_log(source: str | Path) -> list[LogEntry]:
    """Parse a log file in ONE LINE.

    Feature: Python-native - returns standard list[LogEntry]

    Args:
        source: Path to log file

    Returns:
        List of LogEntry objects

    Example:
        >>> entries = parse_log("app.log")
        >>> for entry in entries:
        ...     print(entry.message)
    """
    path = Path(source)
    entries: list[LogEntry] = []

    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                entries.append(LogEntry.from_dict(data, line_number=line_num))
            except (json.JSONDecodeError, ValueError):
                pass  # Skip invalid lines

    return entries


def parse_line(line: str) -> LogEntry | None:
    """Parse a single log line.

    Args:
        line: JSON log line

    Returns:
        LogEntry or None if invalid

    Example:
        >>> entry = parse_line('{"ts": 123, "tid": "Xa.1", ...}')
        >>> if entry:
        ...     print(entry.message)
    """
    try:
        data = json.loads(line.strip())
        return LogEntry.from_dict(data)
    except (json.JSONDecodeError, ValueError):
        return None


def check_log(source: str | Path) -> CheckResult:
    """Parse and validate a log file in ONE LINE.

    Feature: Check presence - comprehensive validation

    Args:
        source: Path to log file

    Returns:
        CheckResult with has_error, has_level(), contains(), etc.

    Example:
        >>> result = check_log("app.log")
        >>> if result.has_error:
        ...     print(f"Found {result.error_count} errors")
        >>> if result.has_action("db:query"):
        ...     print("Has database queries")
        >>> if result.contains(level="error", action_type="http"):
        ...     print("Has HTTP errors")
    """
    path = Path(source)
    entries = parse_log(path)

    # Count errors
    error_count = sum(1 for e in entries if e.is_error)

    # Validate entries
    validation_errors: list[str] = []
    for i, entry in enumerate(entries, 1):
        if entry.timestamp <= 0:
            validation_errors.append(f"Line {i}: Invalid timestamp")
        if not entry.task_uuid:
            validation_errors.append(f"Line {i}: Missing task_uuid")

    return CheckResult(
        entries=entries,
        file_path=path,
        total_lines=sum(1 for _ in open(path, encoding="utf-8")),
        error_count=error_count,
        validation_errors=validation_errors,
    )


def analyze_log(source: str | Path) -> AnalysisReport:
    """Parse, validate, and analyze a log file in ONE LINE.

    Feature: Productive - rich analysis with minimal code

    Args:
        source: Path to log file

    Returns:
        AnalysisReport with stats, slowest actions, errors

    Example:
        >>> report = analyze_log("app.log")
        >>> report.print_summary()
    """
    check_result = check_log(source)
    entries = check_result.entries

    # Count by level using bucketize
    level_groups = bucketize(entries, lambda e: e.level.value)  # type: ignore
    level_counts = {k: len(v) for k, v in level_groups.items()}

    # Count by action status using bucketize
    status_groups = bucketize(entries, lambda e: e.action_status.value if e.action_status else "message")  # type: ignore
    action_counts = {k: len(v) for k, v in status_groups.items()}

    task_count = len({e.task_uuid for e in entries})
    error_count = sum(1 for e in entries if e.is_error)
    max_depth = max((e.depth for e in entries), default=0)
    has_duration = sum(1 for e in entries if e.duration is not None)

    stats = LogStats(
        total=len(entries),
        level_counts=level_counts,
        action_counts=action_counts,
        task_count=task_count,
        error_count=error_count,
        max_depth=max_depth,
        has_duration=has_duration,
    )

    # Find slowest actions using bucketize
    with_duration = [e for e in entries if e.duration is not None and e.action_type]
    action_groups = bucketize(with_duration, lambda e: e.action_type or "")  # type: ignore

    slowest = [
        (action, sum(e.duration for e in group) / len(group))
        for action, group in sorted(action_groups.items())
    ]
    slowest.sort(key=lambda x: x[1], reverse=True)

    # Get errors
    errors = [e for e in entries if e.is_error]

    return AnalysisReport(
        file_path=check_result.file_path,
        check=check_result,
        stats=stats,
        slowest=slowest,
        errors=errors,
    )


# ============================================================================
# Type & Count Helper Functions (Feature b)
# ============================================================================

def count_by(
    entries: Iterable[LogEntry],
    *,
    level: str | None = None,
    action_type: str | None = None,
    action_status: str | None = None,
) -> int:
    """Count entries matching criteria.

    Feature: Type & count - simplified counting

    Args:
        entries: Iterable of log entries
        level: Filter by log level
        action_type: Filter by action type
        action_status: Filter by action status

    Returns:
        Count of matching entries

    Example:
        >>> errors = count_by(entries, level="error")
        >>> db_queries = count_by(entries, action_type="db:query")
        >>> failed = count_by(entries, action_status="failed")
    """
    return sum(
        1 for e in entries
        if (level is None or e.level.value == level)
        and (action_type is None or e.action_type == action_type)
        and (action_status is None or (e.action_status and e.action_status.value == action_status))
    )


def group_by(
    entries: Iterable[LogEntry],
    key: str,
) -> dict[str, list[LogEntry]]:
    """Group entries by a field value.

    Feature: Type & count - using boltons bucketize

    Args:
        entries: Iterable of log entries
        key: Field name to group by (can be attribute or fields dict key)

    Returns:
        Dictionary mapping values to lists of entries

    Example:
        >>> by_level = group_by(entries, "level")
        >>> by_action = group_by(entries, "action_type")
    """
    def get_key(e: LogEntry) -> str:
        val = getattr(e, key, None)
        if val is None:
            val = e.fields.get(key)
        return str(val) if val is not None else ""

    return bucketize(entries, get_key)  # type: ignore[no-untyped-call]


def types(entries: Iterable[LogEntry], field_name: str = "action_type") -> set[str]:
    """Get unique values for a field.

    Feature: Type & count - get unique types

    Args:
        entries: Iterable of log entries
        field_name: Field name to get unique values for

    Returns:
        Set of unique values

    Example:
        >>> action_types = types(entries, "action_type")
        >>> levels = types(entries, "level")
    """
    unique_values = set()
    for e in entries:
        val = getattr(e, field_name, None)
        if val is None:
            val = e.fields.get(field_name)
        if val is not None:
            unique_values.add(str(val))
    return unique_values


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # One-line API
    "parse_log",
    "parse_line",
    "check_log",
    "analyze_log",
    # Result classes
    "CheckResult",
    "LogStats",
    "AnalysisReport",
    # Type & count helpers
    "count_by",
    "group_by",
    "types",
]
