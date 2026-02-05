"""Statistics and analytics for Eliot logs."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import mean, median, stdev
from typing import Any


@dataclass
class TaskStatistics:
    """Comprehensive statistics for Eliot tasks."""

    # Counts
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    started_tasks: int = 0

    # Duration stats
    durations: list[float] = field(default_factory=list)
    total_duration: float = 0.0

    # Action types
    action_types: Counter = field(default_factory=Counter)

    # Error types
    error_types: Counter = field(default_factory=Counter)

    # Timeline
    first_timestamp: float | None = None
    last_timestamp: float | None = None

    # Task levels
    task_levels: Counter = field(default_factory=Counter)

    # Custom fields
    field_counts: dict[str, int] = field(default_factory=dict)
    field_values: dict[str, Counter] = field(default_factory=dict)

    def add_task(self, task: dict[str, Any]) -> None:
        """Add a task to statistics."""
        self.total_tasks += 1

        # Status counts
        status = task.get("action_status")
        if status == "succeeded":
            self.successful_tasks += 1
        elif status == "failed":
            self.failed_tasks += 1
        elif status == "started":
            self.started_tasks += 1

        # Duration
        duration = task.get("duration")
        if duration is not None:
            self.durations.append(float(duration))
            self.total_duration += float(duration)

        # Action type
        action_type = task.get("action_type")
        if action_type:
            self.action_types[action_type] += 1

        # Error types
        if status == "failed":
            error = task.get("error", task.get("exception", "Unknown"))
            self.error_types[str(error)] += 1

        # Timeline
        timestamp = task.get("timestamp")
        if timestamp is not None:
            # Handle both float timestamps and ISO format strings
            if isinstance(timestamp, str):
                from datetime import datetime
                try:
                    ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp()
                except ValueError:
                    ts = 0.0
            else:
                ts = float(timestamp)
            if self.first_timestamp is None or ts < self.first_timestamp:
                self.first_timestamp = ts
            if self.last_timestamp is None or ts > self.last_timestamp:
                self.last_timestamp = ts

        # Task level
        task_level = task.get("task_level", [])
        if isinstance(task_level, list):
            depth = len(task_level)
            self.task_levels[depth] += 1

        # Track field presence
        for key in task:
            self.field_counts[key] = self.field_counts.get(key, 0) + 1

            # Track common field values (limited)
            if key not in self.field_values:
                self.field_values[key] = Counter()
            if len(self.field_values[key]) < 20:  # Limit distinct values
                value = task[key]
                if isinstance(value, (str, int, float, bool)):
                    self.field_values[key][str(value)] += 1

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_tasks == 0:
            return 0.0
        completed = self.successful_tasks + self.failed_tasks
        if completed == 0:
            return 0.0
        return (self.successful_tasks / completed) * 100

    @property
    def failure_rate(self) -> float:
        """Calculate failure rate as percentage."""
        if self.total_tasks == 0:
            return 0.0
        completed = self.successful_tasks + self.failed_tasks
        if completed == 0:
            return 0.0
        return (self.failed_tasks / completed) * 100

    @property
    def duration_stats(self) -> dict[str, float | None]:
        """Calculate duration statistics."""
        if not self.durations:
            return {
                "count": 0,
                "mean": None,
                "median": None,
                "min": None,
                "max": None,
                "stdev": None,
            }

        stats = {
            "count": len(self.durations),
            "mean": mean(self.durations),
            "median": median(self.durations),
            "min": min(self.durations),
            "max": max(self.durations),
        }

        if len(self.durations) > 1:
            stats["stdev"] = stdev(self.durations)
        else:
            stats["stdev"] = 0.0

        return stats

    @property
    def time_span(self) -> timedelta | None:
        """Calculate time span of logs."""
        if self.first_timestamp is None or self.last_timestamp is None:
            return None
        return timedelta(seconds=self.last_timestamp - self.first_timestamp)

    @property
    def tasks_per_second(self) -> float | None:
        """Calculate average tasks per second."""
        span = self.time_span
        if span is None or span.total_seconds() == 0:
            return None
        return self.total_tasks / span.total_seconds()

    def get_top_action_types(self, n: int = 5) -> list[tuple[str, int]]:
        """Get top N action types."""
        return self.action_types.most_common(n)

    def get_top_errors(self, n: int = 5) -> list[tuple[str, int]]:
        """Get top N error types."""
        return self.error_types.most_common(n)

    def get_slow_tasks(self, tasks: Iterable[dict], n: int = 5) -> list[dict]:
        """Get top N slowest tasks."""
        tasks_with_duration = [
            t for t in tasks
            if t.get("duration") is not None
        ]
        return sorted(
            tasks_with_duration,
            key=lambda t: t["duration"],
            reverse=True
        )[:n]


def calculate_statistics(tasks: Iterable[dict[str, Any]]) -> TaskStatistics:
    """
    Calculate comprehensive statistics for a collection of tasks.
    
    Args:
        tasks: Iterable of task dictionaries
        
    Returns:
        TaskStatistics object with computed metrics
        
    Example:
        >>> stats = calculate_statistics(tasks)
        >>> print(f"Success rate: {stats.success_rate:.1f}%")
    """
    stats = TaskStatistics()

    for task in tasks:
        stats.add_task(task)

    return stats


def print_statistics(stats: TaskStatistics) -> None:
    """Print statistics in a formatted way."""
    print("=" * 70)
    print("📊 ELIOT LOG STATISTICS")
    print("=" * 70)

    # Summary
    print("\n📈 SUMMARY")
    print("-" * 70)
    print(f"  Total tasks:      {stats.total_tasks}")
    print(f"  Successful:       {stats.successful_tasks} ({stats.success_rate:.1f}%)")
    print(f"  Failed:           {stats.failed_tasks} ({stats.failure_rate:.1f}%)")
    print(f"  In progress:      {stats.started_tasks}")

    # Timeline
    if stats.time_span:
        print("\n📅 TIMELINE")
        print("-" * 70)
        print(f"  Time span:        {stats.time_span}")
        if stats.tasks_per_second:
            print(f"  Tasks/second:     {stats.tasks_per_second:.2f}")

    # Duration stats
    duration = stats.duration_stats
    if duration["count"] > 0:
        print("\n⏱️  DURATION STATISTICS")
        print("-" * 70)
        print(f"  Tasks with duration: {duration['count']}")
        print(f"  Mean:             {duration['mean']:.4f}s")
        print(f"  Median:           {duration['median']:.4f}s")
        print(f"  Min:              {duration['min']:.4f}s")
        print(f"  Max:              {duration['max']:.4f}s")
        if duration["stdev"] is not None:
            print(f"  Std Dev:          {duration['stdev']:.4f}s")

    # Top action types
    if stats.action_types:
        print("\n📋 TOP ACTION TYPES")
        print("-" * 70)
        for action, count in stats.get_top_action_types(5):
            pct = (count / stats.total_tasks) * 100
            print(f"  {action}: {count} ({pct:.1f}%)")

    # Top errors
    if stats.error_types:
        print("\n❌ TOP ERRORS")
        print("-" * 70)
        for error, count in stats.get_top_errors(5):
            print(f"  {error}: {count}")

    # Task depth
    if stats.task_levels:
        print("\n🔢 TASK DEPTH DISTRIBUTION")
        print("-" * 70)
        for depth in sorted(stats.task_levels.keys()):
            count = stats.task_levels[depth]
            pct = (count / stats.total_tasks) * 100
            bar = "█" * int(pct / 5)
            print(f"  Level {depth}: {count:5d} ({pct:5.1f}%) {bar}")

    print("\n" + "=" * 70)


@dataclass
class TimeSeriesData:
    """Time series data for metrics."""

    bucket_size: timedelta
    buckets: dict[datetime, dict[str, Any]] = field(default_factory=dict)

    def add_point(self, timestamp: datetime, **metrics: Any) -> None:
        """Add a data point to the time series."""
        # Round to bucket
        bucket_time = self._round_to_bucket(timestamp)

        if bucket_time not in self.buckets:
            self.buckets[bucket_time] = {
                "count": 0,
                "errors": 0,
                "durations": [],
            }

        bucket = self.buckets[bucket_time]
        bucket["count"] += 1

        if metrics.get("failed"):
            bucket["errors"] += 1

        duration = metrics.get("duration")
        if duration is not None:
            bucket["durations"].append(duration)

    def _round_to_bucket(self, timestamp: datetime) -> datetime:
        """Round timestamp to bucket boundary."""
        if self.bucket_size.total_seconds() >= 3600:
            # Hour bucket
            return timestamp.replace(minute=0, second=0, microsecond=0)
        elif self.bucket_size.total_seconds() >= 60:
            # Minute bucket
            return timestamp.replace(second=0, microsecond=0)
        else:
            # Second bucket
            return timestamp.replace(microsecond=0)

    def to_list(self) -> list[dict[str, Any]]:
        """Convert to list of data points."""
        result = []
        for timestamp in sorted(self.buckets.keys()):
            bucket = self.buckets[timestamp]
            point = {
                "timestamp": timestamp.isoformat(),
                "count": bucket["count"],
                "errors": bucket["errors"],
                "error_rate": (bucket["errors"] / bucket["count"] * 100) if bucket["count"] > 0 else 0,
            }

            if bucket["durations"]:
                point["avg_duration"] = mean(bucket["durations"])
                point["max_duration"] = max(bucket["durations"])

            result.append(point)

        return result


def create_time_series(
    tasks: Iterable[dict[str, Any]],
    bucket_size: timedelta = timedelta(minutes=1),
) -> TimeSeriesData:
    """
    Create time series data from tasks.
    
    Args:
        tasks: Iterable of task dictionaries
        bucket_size: Size of each time bucket
        
    Returns:
        TimeSeriesData object
    """
    ts = TimeSeriesData(bucket_size=bucket_size)

    for task in tasks:
        timestamp = task.get("timestamp")
        if timestamp is None:
            continue

        dt = datetime.fromtimestamp(float(timestamp))
        ts.add_point(
            dt,
            failed=task.get("action_status") == "failed",
            duration=task.get("duration"),
        )

    return ts


__all__ = [
    "TaskStatistics",
    "TimeSeriesData",
    "calculate_statistics",
    "create_time_series",
    "print_statistics",
]
