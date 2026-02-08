"""
Simple, rich one-line API for parsing logxpy log files.

This module provides the easiest way to parse and validate logxpy logs:

    # One line to parse a log file
    entries = parse_log("example.log")
    
    # One line to parse with validation
    result = check_log("example.log")
    
    # One line to parse and analyze
    report = analyze_log("example.log")

The API handles logxpy format automatically (task_level arrays, action_status fields).
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

from .core import LogEntry as BaseLogEntry
from .types import ActionStatus, Level


@dataclass(frozen=True, slots=True)
class LogXPyEntry:
    """Log entry compatible with logxpy format (task_level arrays).
    
    Use this for logs created by logxpy library.
    """
    
    timestamp: float
    task_uuid: str
    task_level: tuple[int, ...]
    message_type: str
    message: str | None
    action_type: str | None
    action_status: ActionStatus | None
    duration: float | None
    fields: dict[str, Any]
    raw: dict[str, Any] = field(repr=False)  # Original raw data
    line_number: int = 0  # Line number in source file (0 if unknown)
    
    @property
    def level(self) -> Level:
        """Get log level from message_type."""
        mt = self.message_type.lower()
        if "critical" in mt:
            return Level.CRITICAL
        elif "error" in mt:
            return Level.ERROR
        elif "warning" in mt:
            return Level.WARNING
        elif "debug" in mt:
            return Level.DEBUG
        elif "note" in mt:
            return Level.NOTE
        elif "success" in mt:
            return Level.SUCCESS
        return Level.INFO
    
    @property
    def depth(self) -> int:
        """Get nesting depth from task_level."""
        return len(self.task_level)
    
    @property
    def is_error(self) -> bool:
        """Check if this is an error entry."""
        return self.level in (Level.ERROR, Level.CRITICAL)
    
    @property
    def is_action(self) -> bool:
        """Check if this is an action entry."""
        return self.action_type is not None
    
    @property
    def is_message(self) -> bool:
        """Check if this is a message entry."""
        return not self.is_action
    
    @property
    def has_duration(self) -> bool:
        """Check if entry has timing information."""
        return self.duration is not None
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get field value by key (checks fields dict first)."""
        if key in ("timestamp", "task_uuid", "task_level", "message_type", 
                   "message", "action_type", "action_status", "duration"):
            return getattr(self, key, default)
        return self.fields.get(key, default)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert back to dictionary format."""
        result: dict[str, Any] = {
            "timestamp": self.timestamp,
            "task_uuid": self.task_uuid,
            "task_level": list(self.task_level),
            "message_type": self.message_type,
        }
        if self.message:
            result["message"] = self.message
        if self.action_type:
            result["action_type"] = self.action_type
        if self.action_status:
            result["action_status"] = self.action_status.value
        if self.duration is not None:
            result["duration_ns"] = int(self.duration * 1e9)
        result.update(self.fields)
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, Any], line_number: int = 0) -> LogXPyEntry:
        """Create entry from logxpy JSON dictionary.
        
        Args:
            data: JSON dictionary from log line
            line_number: Line number in source file (0 if unknown)
        """
        # Parse task_level (array format: [1] or [1,1])
        task_level_raw = data.get("task_level", [])
        if isinstance(task_level_raw, list):
            task_level = tuple(task_level_raw)
        else:
            task_level = ()
        
        # Parse action_status
        action_status = None
        status_val = data.get("action_status") or data.get("status")
        if status_val:
            try:
                action_status = ActionStatus(status_val)
            except ValueError:
                action_status = None
        
        # Parse duration
        duration = None
        if "duration_ns" in data:
            duration = data["duration_ns"] / 1e9
        elif "logxpy:duration" in data:
            duration = data["logxpy:duration"]
        
        # Extract known fields
        known_fields = {
            "timestamp", "task_uuid", "task_level", "message_type", "message",
            "action_type", "action_status", "status", "duration_ns", 
            "logxpy:duration", "logxpy:traceback", "level",
        }
        fields = {k: v for k, v in data.items() if k not in known_fields}
        
        # Parse timestamp
        ts = data.get("timestamp", 0)
        if isinstance(ts, str):
            try:
                ts = float(ts)
            except ValueError:
                ts = 0
        
        return cls(
            timestamp=ts,
            task_uuid=data.get("task_uuid", ""),
            task_level=task_level,
            message_type=data.get("message_type", ""),
            message=data.get("message"),
            action_type=data.get("action_type"),
            action_status=action_status,
            duration=duration,
            fields=fields,
            raw=data,
            line_number=line_number,
        )


@dataclass
class ParseResult:
    """Result of parsing a log file."""
    
    entries: list[LogXPyEntry]
    total_lines: int
    parsed_count: int
    skipped_count: int
    errors: list[str]
    
    def __len__(self) -> int:
        return len(self.entries)
    
    def __iter__(self) -> Iterator[LogXPyEntry]:
        return iter(self.entries)
    
    def __getitem__(self, index: int) -> LogXPyEntry:
        return self.entries[index]


@dataclass
class CheckResult:
    """Result of checking/validating a log file."""
    
    # Parse info
    entries: list[LogXPyEntry]
    total_lines: int
    parsed_count: int
    skipped_count: int
    
    # Validation
    validation_errors: list[str]
    is_valid: bool
    
    # Statistics
    stats: LogStats = field(repr=False)
    
    def __len__(self) -> int:
        return len(self.entries)
    
    def __iter__(self) -> Iterator[LogXPyEntry]:
        return iter(self.entries)


@dataclass
class LogStats:
    """Statistics for a log file."""
    
    unique_tasks: int
    max_depth: int
    entries_with_duration: int
    total_fields: int
    
    # Actions
    actions_started: int
    actions_succeeded: int
    actions_failed: int
    
    # Levels
    levels: dict[str, int]
    
    # Action types
    action_types: dict[str, int]
    
    # Errors
    error_count: int
    
    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "unique_tasks": self.unique_tasks,
            "max_depth": self.max_depth,
            "entries_with_duration": self.entries_with_duration,
            "total_fields": self.total_fields,
            "actions": {
                "started": self.actions_started,
                "succeeded": self.actions_succeeded,
                "failed": self.actions_failed,
            },
            "levels": self.levels,
            "action_types": self.action_types,
            "errors": self.error_count,
        }


@dataclass
class AnalysisReport:
    """Complete analysis report for a log file."""
    
    # Basic info
    file_path: Path
    entries: list[LogXPyEntry]
    
    # Statistics
    stats: LogStats
    
    # Validation
    validation_errors: list[str]
    is_valid: bool
    
    # Analysis
    slowest_actions: list[tuple[str, float]]  # (action_type, duration)
    errors: list[LogXPyEntry]
    
    def print_summary(self) -> None:
        """Print a summary of the analysis."""
        print(f"\n📊 Log Analysis: {self.file_path.name}")
        print("=" * 60)
        print(f"  Total entries: {len(self.entries)}")
        print(f"  Unique tasks:  {self.stats.unique_tasks}")
        print(f"  Max depth:     {self.stats.max_depth}")
        print(f"  Errors:        {self.stats.error_count}")
        print(f"\n  Actions: {self.stats.actions_started} started, "
              f"{self.stats.actions_succeeded} succeeded, "
              f"{self.stats.actions_failed} failed")
        
        if self.slowest_actions:
            print(f"\n  Slowest actions:")
            for action, duration in self.slowest_actions[:3]:
                print(f"    - {action}: {duration*1000:.2f}ms")
        
        if not self.is_valid:
            print(f"\n  ⚠️  Validation errors: {len(self.validation_errors)}")
    
    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "file": str(self.file_path),
            "entry_count": len(self.entries),
            "is_valid": self.is_valid,
            "stats": self.stats.to_dict(),
            "slowest_actions": self.slowest_actions,
        }


def parse_log(source: str | Path) -> ParseResult:
    """Parse a log file in ONE LINE.
    
    Args:
        source: Path to log file
        
    Returns:
        ParseResult with entries and metadata
        
    Example:
        >>> result = parse_log("app.log")
        >>> print(f"Parsed {len(result)} entries")
        >>> for entry in result:
        ...     print(entry.message)
    """
    path = Path(source)
    entries: list[LogXPyEntry] = []
    errors: list[str] = []
    total_lines = 0
    
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            total_lines += 1
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                entries.append(LogXPyEntry.from_dict(data, line_number=line_num))
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                errors.append(f"Line {line_num}: {e}")
    
    return ParseResult(
        entries=entries,
        total_lines=total_lines,
        parsed_count=len(entries),
        skipped_count=total_lines - len(entries),
        errors=errors,
    )


def parse_line(line: str) -> LogXPyEntry | None:
    """Parse a single log line.
    
    Args:
        line: JSON log line
        
    Returns:
        LogXPyEntry or None if invalid
        
    Example:
        >>> entry = parse_line('{"timestamp": 123, "task_uuid": "abc", ...}')
        >>> if entry:
        ...     print(entry.message)
    """
    try:
        data = json.loads(line.strip())
        return LogXPyEntry.from_dict(data)
    except (json.JSONDecodeError, ValueError, KeyError):
        return None


def check_log(source: str | Path) -> CheckResult:
    """Parse and validate a log file in ONE LINE.
    
    Args:
        source: Path to log file
        
    Returns:
        CheckResult with entries, validation, and stats
        
    Example:
        >>> result = check_log("app.log")
        >>> if result.is_valid:
        ...     print(f"All {len(result)} entries valid")
        ... else:
        ...     print(f"Found {len(result.validation_errors)} errors")
    """
    # Parse
    parse_result = parse_log(source)
    
    # Validate each entry
    validation_errors: list[str] = []
    for i, entry in enumerate(parse_result.entries, 1):
        # Check required fields
        if not entry.task_uuid:
            validation_errors.append(f"Line {i}: Missing task_uuid")
        if entry.timestamp <= 0:
            validation_errors.append(f"Line {i}: Invalid timestamp")
        if not entry.message_type and not entry.action_type:
            validation_errors.append(f"Line {i}: Missing message_type and action_type")
        
        # Check action consistency
        if entry.is_action and entry.action_status == ActionStatus.FAILED:
            if not entry.is_error and "exception" not in entry.fields:
                validation_errors.append(f"Line {i}: Failed action without error details")
    
    # Calculate stats
    stats = _calculate_stats(parse_result.entries)
    
    return CheckResult(
        entries=parse_result.entries,
        total_lines=parse_result.total_lines,
        parsed_count=parse_result.parsed_count,
        skipped_count=parse_result.skipped_count,
        validation_errors=validation_errors,
        is_valid=len(validation_errors) == 0,
        stats=stats,
    )


def analyze_log(source: str | Path) -> AnalysisReport:
    """Parse, validate, and analyze a log file in ONE LINE.
    
    Args:
        source: Path to log file
        
    Returns:
        AnalysisReport with complete analysis
        
    Example:
        >>> report = analyze_log("app.log")
        >>> report.print_summary()
    """
    check_result = check_log(source)
    path = Path(source)
    
    # Find slowest actions
    action_durations: dict[str, list[float]] = {}
    for entry in check_result.entries:
        if entry.action_type and entry.duration is not None:
            if entry.action_type not in action_durations:
                action_durations[entry.action_type] = []
            action_durations[entry.action_type].append(entry.duration)
    
    slowest = [
        (action, sum(durations)/len(durations))
        for action, durations in action_durations.items()
    ]
    slowest.sort(key=lambda x: x[1], reverse=True)
    
    # Find errors
    errors = [e for e in check_result.entries if e.is_error]
    
    return AnalysisReport(
        file_path=path,
        entries=check_result.entries,
        stats=check_result.stats,
        validation_errors=check_result.validation_errors,
        is_valid=check_result.is_valid,
        slowest_actions=slowest,
        errors=errors,
    )


def _calculate_stats(entries: list[LogXPyEntry]) -> LogStats:
    """Calculate statistics for entries."""
    # Unique tasks
    unique_tasks = len(set(e.task_uuid for e in entries))
    
    # Max depth
    max_depth = max((e.depth for e in entries), default=0)
    
    # Duration count
    entries_with_duration = sum(1 for e in entries if e.duration is not None)
    
    # Total fields
    total_fields = sum(len(e.fields) for e in entries)
    
    # Action counts
    actions_started = sum(1 for e in entries if e.action_status == ActionStatus.STARTED)
    actions_succeeded = sum(1 for e in entries if e.action_status == ActionStatus.SUCCEEDED)
    actions_failed = sum(1 for e in entries if e.action_status == ActionStatus.FAILED)
    
    # Level distribution
    level_counts = Counter(e.level.value for e in entries)
    
    # Action types
    action_type_counts = Counter(
        e.action_type for e in entries if e.action_type
    )
    
    # Error count
    error_count = sum(1 for e in entries if e.is_error)
    
    return LogStats(
        unique_tasks=unique_tasks,
        max_depth=max_depth,
        entries_with_duration=entries_with_duration,
        total_fields=total_fields,
        actions_started=actions_started,
        actions_succeeded=actions_succeeded,
        actions_failed=actions_failed,
        levels=dict(level_counts),
        action_types=dict(action_type_counts),
        error_count=error_count,
    )


# Convenience exports
__all__ = [
    # Core classes
    "LogXPyEntry",
    "ParseResult",
    "CheckResult",
    "LogStats",
    "AnalysisReport",
    # One-line functions
    "parse_log",
    "parse_line", 
    "check_log",
    "analyze_log",
]
