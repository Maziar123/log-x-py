"""
Log aggregation and time-series analysis for logxy-log-parser.

Provides functionality for aggregating logs from multiple files and
performing time-series analysis.
"""

from __future__ import annotations

import gzip
import json
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .core import LogEntry
from .filter import LogEntries


@dataclass
class TimeBucket:
    """A bucket of time-series data."""

    start: float
    end: float
    count: int
    level_counts: dict[str, int] = field(default_factory=dict)
    error_count: int = 0
    task_uuids: set[str] = field(default_factory=set)

    def add_entry(self, entry: LogEntry) -> None:
        """Add an entry to this bucket.

        Args:
            entry: LogEntry to add.
        """
        self.count += 1
        level = entry.level.value
        self.level_counts[level] = self.level_counts.get(level, 0) + 1
        if entry.is_error:
            self.error_count += 1
        if entry.task_uuid:
            self.task_uuids.add(entry.task_uuid)

    @property
    def error_rate(self) -> float:
        """Calculate error rate for this bucket.

        Returns:
            float: Error rate (0-1).
        """
        return self.error_count / self.count if self.count > 0 else 0


@dataclass
class AggregatedStats:
    """Statistics for aggregated logs."""

    total_entries: int = 0
    total_files: int = 0
    time_range: tuple[float, float] = (0, 0)
    level_counts: dict[str, int] = field(default_factory=dict)
    unique_tasks: int = 0
    file_stats: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary.

        Returns:
            dict[str, Any]: Stats dictionary.
        """
        return {
            "total_entries": self.total_entries,
            "total_files": self.total_files,
            "time_range": self.time_range,
            "level_counts": self.level_counts,
            "unique_tasks": self.unique_tasks,
            "file_stats": self.file_stats,
        }


class LogAggregator:
    """Aggregate logs from multiple files."""

    def __init__(self, sources: list[str | Path]) -> None:
        """Initialize aggregator with multiple log sources.

        Args:
            sources: List of log file paths.
        """
        self._sources = [Path(s) for s in sources]
        self._entries: list[LogEntry] = []
        self._stats = AggregatedStats()

    def aggregate(self, progress_callback: Callable[[int, int], None] | None = None) -> LogEntries:
        """Aggregate all log files.

        Args:
            progress_callback: Optional callback(current, total) for progress updates.

        Returns:
            LogEntries: All aggregated entries.
        """
        all_entries: list[LogEntry] = []
        all_task_uuids = set()
        min_ts = float("inf")
        max_ts = 0.0
        level_counts: dict[str, int] = {}
        file_stats: dict[str, dict[str, Any]] = {}

        for i, source in enumerate(self._sources):
            # Update progress
            if progress_callback:
                progress_callback(i + 1, len(self._sources))

            # Check if file is gzipped
            open_func = gzip.open if str(source).endswith(".gz") else open

            entries = []
            file_level_counts: dict[str, int] = {}

            try:
                with open_func(source, "rt", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            entry = LogEntry.from_dict(data)
                            entries.append(entry)

                            # Track stats
                            level = entry.level.value
                            level_counts[level] = level_counts.get(level, 0) + 1
                            file_level_counts[level] = file_level_counts.get(level, 0) + 1

                            if entry.task_uuid:
                                all_task_uuids.add(entry.task_uuid)

                            min_ts = min(min_ts, entry.timestamp)
                            max_ts = max(max_ts, entry.timestamp)

                        except (json.JSONDecodeError, ValueError):
                            continue
            except OSError:
                # Skip files that can't be read
                continue

            all_entries.extend(entries)
            file_stats[str(source)] = {
                "entries": len(entries),
                "level_counts": file_level_counts,
            }

        # Update stats
        self._stats = AggregatedStats(
            total_entries=len(all_entries),
            total_files=len(self._sources),
            time_range=(min_ts, max_ts) if min_ts != float("inf") else (0, 0),
            level_counts=level_counts,
            unique_tasks=len(all_task_uuids),
            file_stats=file_stats,
        )

        self._entries = all_entries
        return LogEntries(all_entries)

    @property
    def stats(self) -> AggregatedStats:
        """Get aggregation statistics.

        Returns:
            AggregatedStats: Aggregation statistics.
        """
        return self._stats


class TimeSeriesAnalyzer:
    """Analyze logs as a time series."""

    def __init__(self, entries: LogEntries | list[LogEntry]) -> None:
        """Initialize analyzer with log entries.

        Args:
            entries: Log entries to analyze.
        """
        if isinstance(entries, LogEntries):
            self._entries = list(entries)
        else:
            self._entries = entries

    def bucket_by_interval(
        self, interval_seconds: float = 60
    ) -> list[TimeBucket]:
        """Bucket entries by time interval.

        Args:
            interval_seconds: Bucket size in seconds.

        Returns:
            list[TimeBucket]: Time buckets.
        """
        if not self._entries:
            return []

        # Find time range
        timestamps = [e.timestamp for e in self._entries]
        min_ts = min(timestamps)

        # Create buckets
        buckets: dict[float, TimeBucket] = {}
        for entry in self._entries:
            # Calculate bucket key
            bucket_key = int((entry.timestamp - min_ts) // interval_seconds) * interval_seconds + min_ts

            if bucket_key not in buckets:
                buckets[bucket_key] = TimeBucket(
                    start=bucket_key,
                    end=bucket_key + interval_seconds,
                    count=0,
                )

            buckets[bucket_key].add_entry(entry)

        # Return sorted by time
        return [buckets[k] for k in sorted(buckets.keys())]

    def detect_anomalies(
        self, window_size: int = 10, threshold: float = 2.0
    ) -> list[dict[str, Any]]:
        """Detect anomalies in log rate.

        Args:
            window_size: Size of rolling window for baseline.
            threshold: Number of standard deviations for anomaly detection.

        Returns:
            list[dict[str, Any]]: Detected anomalies.
        """
        import statistics

        buckets = self.bucket_by_interval(interval_seconds=60)
        if len(buckets) < window_size * 2:
            return []

        counts = [b.count for b in buckets]
        anomalies = []

        for i in range(window_size, len(buckets) - window_size):
            # Get baseline from window around current point (excluding it)
            window = counts[i - window_size:i] + counts[i + 1:i + 1 + window_size]
            mean = statistics.mean(window)
            stdev = statistics.stdev(window) if len(window) > 1 else 0

            if stdev > 0:
                z_score = (counts[i] - mean) / stdev
                if abs(z_score) > threshold:
                    anomalies.append({
                        "timestamp": buckets[i].start,
                        "count": counts[i],
                        "expected": mean,
                        "z_score": z_score,
                        "type": "spike" if z_score > 0 else "drop",
                    })

        return anomalies

    def error_rate_trend(self, interval_seconds: float = 60) -> list[dict[str, Any]]:
        """Calculate error rate trend over time.

        Args:
            interval_seconds: Time interval for buckets.

        Returns:
            list[dict[str, Any]]: Error rate data points.
        """
        buckets = self.bucket_by_interval(interval_seconds)

        trend = []
        for bucket in buckets:
            trend.append({
                "timestamp": bucket.start,
                "error_rate": bucket.error_rate,
                "error_count": bucket.error_count,
                "total_count": bucket.count,
            })

        return trend

    def level_distribution_over_time(self, interval_seconds: float = 60) -> dict[str, list[tuple[float, int]]]:
        """Calculate level distribution over time.

        Args:
            interval_seconds: Time interval for buckets.

        Returns:
            dict[str, list[tuple[float, int]]]: Level to (timestamp, count) mapping.
        """
        buckets = self.bucket_by_interval(interval_seconds)

        distribution: dict[str, list[tuple[float, int]]] = defaultdict(list)

        for bucket in buckets:
            for level, count in bucket.level_counts.items():
                distribution[level].append((bucket.start, count))

        return dict(distribution)

    def activity_heatmap(
        self, hour_granularity: bool = False
    ) -> dict[str | int, dict[str | int, int]]:
        """Generate activity heatmap by time period.

        Args:
            hour_granularity: If True, group by hour of day. If False, by day of week.

        Returns:
            dict: Nested mapping of time period to counts.
        """
        heatmap: dict[str | int, dict[str | int, int]] = defaultdict(lambda: defaultdict(int))

        for entry in self._entries:
            dt = datetime.fromtimestamp(entry.timestamp)

            if hour_granularity:
                # By hour of day (0-23)
                outer_key: int | str = dt.hour
                inner_key = dt.weekday()  # Day of week
            else:
                # By day of week and hour
                outer_key = dt.strftime("%A")  # Day name
                inner_key = dt.hour

            level = entry.level.value
            heatmap[f"{outer_key}"][f"{inner_key}_{level}"] += 1

        # Convert nested defaultdicts to regular dicts
        return {
            str(k): {str(k2): v2 for k2, v2 in v.items()}
            for k, v in heatmap.items()
        }

    def burst_detection(
        self, threshold: float = 1.5, min_interval: float = 5
    ) -> list[dict[str, Any]]:
        """Detect bursts in log activity.

        Args:
            threshold: Multiplier of median count to consider a burst.
            min_interval: Minimum interval between bursts in seconds.

        Returns:
            list[dict[str, Any]]: Detected bursts.
        """
        import statistics

        # Use small intervals for burst detection
        buckets = self.bucket_by_interval(interval_seconds=min_interval)

        if not buckets:
            return []

        counts = [b.count for b in buckets]
        median = statistics.median(counts)
        threshold_value = median * threshold

        bursts = []
        current_burst_start = None
        current_max = 0

        for bucket in buckets:
            if bucket.count > threshold_value:
                if current_burst_start is None:
                    current_burst_start = bucket.start
                current_max = max(current_max, bucket.count)
            else:
                if current_burst_start is not None:
                    bursts.append({
                        "start": current_burst_start,
                        "end": bucket.start,
                        "peak_count": current_max,
                        "threshold": threshold_value,
                    })
                    current_burst_start = None
                    current_max = 0

        # Handle burst that extends to end
        if current_burst_start is not None:
            bursts.append({
                "start": current_burst_start,
                "end": buckets[-1].end,
                "peak_count": current_max,
                "threshold": threshold_value,
            })

        return bursts


class MultiFileAnalyzer:
    """Analyze logs across multiple files."""

    def __init__(self, directory: str | Path, pattern: str = "*.log") -> None:
        """Initialize analyzer for a directory.

        Args:
            directory: Directory containing log files.
            pattern: Glob pattern for log files.
        """
        self._directory = Path(directory)
        self._pattern = pattern
        self._files: list[Path] = []
        self._scan_directory()

    def _scan_directory(self) -> None:
        """Scan directory for matching log files."""
        self._files = sorted(self._directory.glob(self._pattern))
        # Also check for gzipped files
        self._files.extend(sorted(self._directory.glob(f"{self._pattern}.gz")))

    @property
    def file_count(self) -> int:
        """Get number of log files found.

        Returns:
            int: Number of files.
        """
        return len(self._files)

    def analyze_all(self) -> dict[str, Any]:
        """Analyze all log files in the directory.

        Returns:
            dict[str, Any]: Combined analysis results.
        """
        aggregator = LogAggregator([str(f) for f in self._files])
        entries = aggregator.aggregate()

        from .analyzer import LogAnalyzer

        analyzer = LogAnalyzer(entries)
        error_summary = analyzer.error_summary()

        return {
            "directory": str(self._directory),
            "files": self._files,
            "file_count": self._files,
            "aggregation_stats": aggregator.stats.to_dict(),
            "error_summary": {
                "total_count": error_summary.total_count,
                "unique_types": error_summary.unique_types,
                "by_level": error_summary.by_level,
            },
            "slowest_actions": [(a.action_type, a.mean_duration)
                               for a in analyzer.slowest_actions(5)],
        }

    def time_series_analysis(
        self, interval_seconds: float = 3600
    ) -> list[dict[str, Any]]:
        """Perform time-series analysis across all files.

        Args:
            interval_seconds: Interval for bucketing.

        Returns:
            list[dict[str, Any]]: Time series data.
        """
        aggregator = LogAggregator([str(f) for f in self._files])
        entries = aggregator.aggregate()

        analyzer = TimeSeriesAnalyzer(entries)
        buckets = analyzer.bucket_by_interval(interval_seconds)

        return [
            {
                "timestamp": b.start,
                "count": b.count,
                "error_count": b.error_count,
                "error_rate": b.error_rate,
            }
            for b in buckets
        ]
