"""
Analysis functionality for logxy-log-parser.

Contains LogAnalyzer for statistical and pattern analysis of log entries.
Uses boltons for efficient grouping and iteration utilities.
"""

from __future__ import annotations

import statistics
from collections import Counter
from dataclasses import dataclass

from .core import LogEntry
from .filter import LogEntries
from .types import ActionStatus
from .utils import bucketize


@dataclass(frozen=True, slots=True)
class DurationStats:
    """Duration statistics for a set of actions."""

    count: int
    total: float
    mean: float
    median: float
    min: float
    max: float
    std: float
    p25: float
    p75: float
    p95: float
    p99: float


@dataclass(frozen=True, slots=True)
class ErrorSummary:
    """Error analysis summary."""

    total_count: int
    unique_types: int
    most_common: tuple[str, int]
    by_level: dict[str, int]
    by_action: dict[str, int]


@dataclass(frozen=True, slots=True)
class ActionStat:
    """Individual action statistic."""

    action_type: str
    count: int
    total_duration: float
    mean_duration: float
    min_duration: float
    max_duration: float


@dataclass(frozen=True, slots=True)
class ErrorPattern:
    """Error pattern for analysis."""

    error_type: str
    count: int
    first_seen: float
    last_seen: float
    example_message: str | None


@dataclass(frozen=True, slots=True)
class TimePeriod:
    """Time period for timeline analysis."""

    start: float
    end: float
    entry_count: int


@dataclass(frozen=True, slots=True)
class Timeline:
    """Timeline of log activity."""

    intervals: list[TimePeriod]
    total_entries: int


class LogAnalyzer:
    """Advanced log analysis."""

    def __init__(self, entries: LogEntries | list[LogEntry]):
        """Initialize with entries to analyze.

        Args:
            entries: LogEntries collection or list of LogEntry.
        """
        self._entries = entries if isinstance(entries, LogEntries) else LogEntries(entries)

    # Helper methods

    def _group_by_action(self, filtered: bool = True) -> dict[str, list[LogEntry]]:
        """Group entries by action type using boltons bucketize.

        Args:
            filtered: If True, only include entries with action_type and duration.

        Returns:
            dict[str, list[LogEntry]]: Action type to entries mapping.
        """
        if filtered:
            entries = [e for e in self._entries if e.action_type and e.duration is not None]
        else:
            entries = [e for e in self._entries if e.action_type]

        return bucketize(entries, lambda e: e.action_type or "")  # type: ignore[no-untyped-call]

    def _action_stats_from_groups(
        self, groups: dict[str, list[LogEntry]]
    ) -> dict[str, tuple[list[float], ActionStat]]:
        """Calculate statistics from action groups.

        Args:
            groups: Action type to entries mapping.

        Returns:
            dict: Action type to (durations, ActionStat) mapping.
        """
        result = {}
        for action_type, entries in groups.items():
            durations = [e.duration for e in entries if e.duration is not None]
            if durations:
                result[action_type] = (
                    durations,
                    ActionStat(
                        action_type=action_type,
                        count=len(durations),
                        total_duration=sum(durations),
                        mean_duration=sum(durations) / len(durations),
                        min_duration=min(durations),
                        max_duration=max(durations),
                    ),
                )
        return result

    def _calculate_duration_stats(self, durations: list[float]) -> DurationStats:
        """Calculate duration statistics.

        Args:
            durations: List of duration values.

        Returns:
            DurationStats: Calculated statistics.
        """
        if not durations:
            return DurationStats(
                count=0, total=0, mean=0, median=0, min=0, max=0, std=0, p25=0, p75=0, p95=0, p99=0
            )

        sorted_durations = sorted(durations)
        n = len(sorted_durations)

        total = sum(durations)
        mean = total / n
        median = statistics.median(durations)

        # Calculate percentiles
        p25_idx = int(n * 0.25)
        p75_idx = int(n * 0.75)
        p95_idx = int(n * 0.95)
        p99_idx = int(n * 0.99)

        p25 = sorted_durations[p25_idx]
        p75 = sorted_durations[p75_idx]
        p95 = sorted_durations[p95_idx]
        p99 = sorted_durations[p99_idx]

        # Calculate standard deviation
        std = statistics.stdev(durations) if n > 1 else 0

        return DurationStats(
            count=n,
            total=total,
            mean=mean,
            median=median,
            min=min(durations),
            max=max(durations),
            std=std,
            p25=p25,
            p75=p75,
            p95=p95,
            p99=p99,
        )

    def _parse_interval(self, interval: str) -> float:
        """Parse interval string to seconds.

        Args:
            interval: Interval string (e.g., "1min", "5min", "1hour").

        Returns:
            float: Interval in seconds.
        """
        interval = interval.lower()

        match interval:
            case s if "sec" in s:
                return float(s.replace("sec", "").replace("s", ""))
            case s if "min" in s:
                return float(s.replace("min", "").replace("m", "")) * 60
            case s if "hour" in s:
                return float(s.replace("hour", "").replace("h", "")) * 3600
            case s if "day" in s:
                return float(s.replace("day", "").replace("d", "")) * 86400
            case _:
                return float(interval) * 60

    # Performance methods

    def slowest_actions(self, n: int = 10) -> list[ActionStat]:
        """Get the slowest actions.

        Args:
            n: Number of actions to return.

        Returns:
            list[ActionStat]: Slowest action statistics.
        """
        groups = self._group_by_action()
        stats = self._action_stats_from_groups(groups)

        # Sort by mean duration (descending)
        sorted_stats = sorted(stats.items(), key=lambda x: x[1][1].mean_duration, reverse=True)
        return [stat for _, stat in sorted_stats[:n]]

    def fastest_actions(self, n: int = 10) -> list[ActionStat]:
        """Get the fastest actions.

        Args:
            n: Number of actions to return.

        Returns:
            list[ActionStat]: Fastest action statistics.
        """
        groups = self._group_by_action()
        stats = self._action_stats_from_groups(groups)

        # Sort by mean duration (ascending)
        sorted_stats = sorted(stats.items(), key=lambda x: x[1][1].mean_duration)
        return [stat for _, stat in sorted_stats[:n]]

    def duration_by_action(self) -> dict[str, DurationStats]:
        """Get duration statistics by action type.

        Returns:
            dict[str, DurationStats]: Mapping of action type to stats.
        """
        groups = self._group_by_action()
        result = {}
        for action_type, entries in groups.items():
            durations = [e.duration for e in entries if e.duration is not None]
            result[action_type] = self._calculate_duration_stats(durations)
        return result

    def percentile_durations(self, percentile: float = 95) -> list[ActionStat]:
        """Get actions at a specific percentile.

        Args:
            percentile: Percentile value (e.g., 95 for 95th percentile).

        Returns:
            list[ActionStat]: Actions at the specified percentile.
        """
        groups = self._group_by_action()
        stats = self._action_stats_from_groups(groups)
        return [stat for _, stat in sorted(stats.values(), key=lambda x: x.mean_duration, reverse=True)]

    # Error methods

    def error_summary(self) -> ErrorSummary:
        """Get error analysis summary.

        Returns:
            ErrorSummary: Error analysis summary.
        """
        error_entries = [e for e in self._entries if e.is_error]

        # Use bucketize for counting by level
        level_groups = bucketize(error_entries, lambda e: e.level.value)  # type: ignore[no-untyped-call]
        by_level = {k: len(v) for k, v in level_groups.items()}

        # Use bucketize for counting by action
        action_groups = bucketize(error_entries, lambda e: e.action_type or "unknown")  # type: ignore[no-untyped-call]
        by_action = {k: len(v) for k, v in action_groups.items()}

        # Find most common error
        error_messages = [e.message for e in error_entries if e.message]
        most_common_msg = Counter(error_messages).most_common(1)
        most_common = (most_common_msg[0][0], most_common_msg[0][1]) if most_common_msg else ("", 0)

        return ErrorSummary(
            total_count=len(error_entries),
            unique_types=len(by_action),
            most_common=most_common,
            by_level=by_level,
            by_action=by_action,
        )

    def error_patterns(self) -> list[ErrorPattern]:
        """Find error patterns.

        Returns:
            list[ErrorPattern]: List of error patterns.
        """
        error_entries = [e for e in self._entries if e.is_error]

        # Group by error type using boltons bucketize
        error_groups = bucketize(error_entries, lambda e: e.action_type or "message")  # type: ignore[no-untyped-call]

        result = []
        for error_type, entries in error_groups.items():
            timestamps = [e.timestamp for e in entries]
            example = entries[0].message if entries and entries[0].message else None

            result.append(
                ErrorPattern(
                    error_type=error_type,
                    count=len(entries),
                    first_seen=min(timestamps),
                    last_seen=max(timestamps),
                    example_message=example,
                )
            )

        # Sort by count (descending)
        result.sort(key=lambda x: x.count, reverse=True)
        return result

    def failure_rate_by_action(self) -> dict[str, float]:
        """Calculate failure rate by action type.

        Returns:
            dict[str, float]: Mapping of action type to failure rate (0-1).
        """
        groups = self._group_by_action(filtered=False)

        result = {}
        for action_type, entries in groups.items():
            total = len(entries)
            failed = sum(1 for e in entries if e.action_status == ActionStatus.FAILED)
            result[action_type] = failed / total if total > 0 else 0.0

        return result

    def most_common_errors(self, n: int = 10) -> list[tuple[str, int]]:
        """Get most common error messages.

        Args:
            n: Number of errors to return.

        Returns:
            list[tuple[str, int]]: List of (message, count) tuples.
        """
        error_messages = [e.message for e in self._entries if e.is_error and e.message]
        return Counter(error_messages).most_common(n)

    # Task analysis methods

    def task_duration_stats(self) -> dict[str, DurationStats]:
        """Get duration statistics by task UUID.

        Returns:
            dict[str, DurationStats]: Mapping of task UUID to stats.
        """
        filtered = [e for e in self._entries if e.task_uuid and e.duration is not None]

        # Group by task UUID using boltons bucketize
        task_groups = bucketize(filtered, lambda e: e.task_uuid or "")  # type: ignore[no-untyped-call]

        result = {}
        for task_uuid, entries in task_groups.items():
            durations = [e.duration for e in entries if e.duration is not None]
            result[task_uuid] = self._calculate_duration_stats(durations)

        return result

    def deepest_nesting(self) -> int:
        """Get the deepest nesting level.

        Returns:
            int: Maximum nesting depth.
        """
        return max((e.depth for e in self._entries), default=0)

    def widest_tasks(self) -> list[tuple[str, int]]:
        """Get tasks with the most child actions.

        Returns:
            list[tuple[str, int]]: List of (task_uuid, child_count) tuples.
        """
        # Use bucketize to count by task UUID
        task_groups = bucketize(self._entries, lambda e: e.task_uuid or "")  # type: ignore[no-untyped-call]
        task_counts = {k: len(v) for k, v in task_groups.items()}

        # Sort by count (descending)
        return sorted(task_counts.items(), key=lambda x: x[1], reverse=True)

    def orphans(self) -> LogEntries:
        """Get orphaned entries (entries without matching start/end).

        Returns:
            LogEntries: Collection of orphaned entries.
        """
        # Track started actions
        started: dict[str, set[str]] = {}  # task_uuid -> set of action types

        # First pass: collect started actions
        for entry in self._entries:
            if entry.action_status == ActionStatus.STARTED and entry.action_type:
                started.setdefault(entry.task_uuid, set()).add(entry.action_type)

        # Second pass: find orphans
        orphans: list[LogEntry] = []

        for entry in self._entries:
            match entry.action_status:
                case ActionStatus.SUCCEEDED | ActionStatus.FAILED:
                    if entry.task_uuid in started and entry.action_type in started[entry.task_uuid]:
                        started[entry.task_uuid].discard(entry.action_type)
                case ActionStatus.STARTED:
                    # Check if this action was never completed
                    if entry.task_uuid in started and entry.action_type in started[entry.task_uuid]:
                        # This is a duplicate start, mark as orphan
                        orphans.append(entry)
                case _:
                    pass

        return LogEntries(orphans)

    # Timeline methods

    def timeline(self, interval: str = "1min") -> Timeline:
        """Get timeline of log activity.

        Args:
            interval: Time interval (e.g., "1min", "5min", "1hour").

        Returns:
            Timeline: Timeline of log activity.
        """
        if not self._entries:
            return Timeline(intervals=[], total_entries=0)

        interval_seconds = self._parse_interval(interval)

        # Get time range
        timestamps = [e.timestamp for e in self._entries]
        start_time = min(timestamps)
        end_time = max(timestamps)

        # Create intervals
        intervals: list[TimePeriod] = []
        current_start = start_time

        while current_start < end_time:
            current_end = current_start + interval_seconds
            count = sum(1 for ts in timestamps if current_start <= ts < current_end)
            intervals.append(TimePeriod(start=current_start, end=current_end, entry_count=count))
            current_start = current_end

        return Timeline(intervals=intervals, total_entries=len(self._entries))

    def peak_periods(self, n: int = 5) -> list[TimePeriod]:
        """Get peak activity periods.

        Args:
            n: Number of periods to return.

        Returns:
            list[TimePeriod]: Peak activity periods.
        """
        timeline = self.timeline(interval="1min")
        return sorted(timeline.intervals, key=lambda x: x.entry_count, reverse=True)[:n]

    def quiet_periods(self, n: int = 5) -> list[TimePeriod]:
        """Get quiet activity periods.

        Args:
            n: Number of periods to return.

        Returns:
            list[TimePeriod]: Quiet activity periods.
        """
        timeline = self.timeline(interval="1min")
        non_zero = [p for p in timeline.intervals if p.entry_count > 0]
        return sorted(non_zero, key=lambda x: x.entry_count)[:n]

    # Report generation

    def generate_report(self, report_format: str = "html") -> str:
        """Generate analysis report.

        Args:
            report_format: Report format ("html", "text", "json").

        Returns:
            str: Report content.
        """
        match report_format:
            case "html":
                return self._generate_html_report()
            case "text":
                return self._generate_text_report()
            case "json":
                return self._generate_json_report()
            case _:
                raise ValueError(f"Unsupported format: {report_format}")

    def _generate_html_report(self) -> str:
        """Generate HTML report."""
        error_summary = self.error_summary()
        deepest = self.deepest_nesting()
        widest = self.widest_tasks()[:5]

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Log Analysis Report</title>
    <style>
        body {{ font-family: sans-serif; margin: 20px; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px; }}
        h2 {{ margin-top: 0; }}
        .stat {{ display: inline-block; margin: 10px; padding: 10px; background: white; border-radius: 3px; }}
        .stat-label {{ font-weight: bold; color: #666; }}
        .stat-value {{ font-size: 1.2em; }}
    </style>
</head>
<body>
    <h1>Log Analysis Report</h1>
    <div class="section">
        <h2>Overview</h2>
        <div class="stat"><span class="stat-label">Total Entries:</span> <span class="stat-value">{len(self._entries)}</span></div>
        <div class="stat"><span class="stat-label">Errors:</span> <span class="stat-value">{error_summary.total_count}</span></div>
        <div class="stat"><span class="stat-label">Deepest Nesting:</span> <span class="stat-value">{deepest}</span></div>
    </div>
    <div class="section">
        <h2>Error Summary</h2>
        <p>Most common error: <strong>{error_summary.most_common[0]}</strong> ({error_summary.most_common[1]} occurrences)</p>
        <p>Unique error types: {error_summary.unique_types}</p>
    </div>
    <div class="section">
        <h2>Widest Tasks</h2>
        <ul>
            {"".join(f"<li>{task_uuid}: {count} entries</li>" for task_uuid, count in widest)}
        </ul>
    </div>
</body>
</html>
"""

    def _generate_text_report(self) -> str:
        """Generate text report."""
        error_summary = self.error_summary()
        deepest = self.deepest_nesting()
        widest = self.widest_tasks()[:5]

        lines = [
            "Log Analysis Report",
            "=" * 50,
            "",
            f"Total Entries: {len(self._entries)}",
            f"Errors: {error_summary.total_count}",
            f"Deepest Nesting: {deepest}",
            "",
            "Error Summary:",
            f"  Most common: {error_summary.most_common[0]} ({error_summary.most_common[1]} occurrences)",
            f"  Unique types: {error_summary.unique_types}",
            "",
            "Widest Tasks:",
        ]

        for task_uuid, count in widest:
            lines.append(f"  {task_uuid}: {count} entries")

        return "\n".join(lines)

    def _generate_json_report(self) -> str:
        """Generate JSON report."""
        import json

        error_summary = self.error_summary()
        report = {
            "total_entries": len(self._entries),
            "error_summary": {
                "total_count": error_summary.total_count,
                "unique_types": error_summary.unique_types,
                "most_common": error_summary.most_common,
                "by_level": error_summary.by_level,
                "by_action": error_summary.by_action,
            },
            "deepest_nesting": self.deepest_nesting(),
            "widest_tasks": self.widest_tasks()[:5],
        }

        return json.dumps(report, indent=2)
