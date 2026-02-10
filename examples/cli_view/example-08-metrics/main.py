#!/usr/bin/env python3
"""
Example 08: Metrics and Analytics

This example shows comprehensive metrics extraction using the new statistics module.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "../../src")

from logxpy_cli_view import (
    calculate_statistics,
    create_time_series,
    print_statistics,
    render_tasks,
    tasks_from_iterable,
)


def main() -> None:
    log_file = Path("nested_tasks.log")

    with open(log_file) as f:
        log_entries = [line.strip() for line in f if line.strip()]

    parsed_logs = [json.loads(line) for line in log_entries]

    print("=" * 70)
    print("Example 08: Comprehensive Metrics Analysis")
    print("=" * 70)

    # Full statistics report
    stats = calculate_statistics(parsed_logs)
    print_statistics(stats)

    # Show top action types
    print("\n" + "=" * 70)
    print("📋 Top Action Types")
    print("=" * 70)
    for action, count in stats.get_top_action_types(5):
        pct = (count / stats.total_tasks) * 100
        print(f"  {action}: {count} ({pct:.1f}%)")

    # Show top errors
    if stats.error_types:
        print("\n" + "=" * 70)
        print("❌ Top Errors")
        print("=" * 70)
        for error, count in stats.get_top_errors(5):
            print(f"  {error}: {count}")

    # Show slowest tasks
    print("\n" + "=" * 70)
    print("🐌 Slowest Tasks")
    print("=" * 70)
    slowest = stats.get_slow_tasks(parsed_logs, 5)
    for i, task in enumerate(slowest, 1):
        action = task.get("action_type", "unknown")
        duration = task.get("duration", 0)
        status = task.get("action_status", "?")
        icon = "✓" if status == "succeeded" else "✗" if status == "failed" else "○"
        print(f"  {i}. {action}: {duration:.3f}s [{icon}]")

    # Task depth distribution
    print("\n" + "=" * 70)
    print("🔢 Task Depth Distribution")
    print("=" * 70)
    for depth in sorted(stats.task_levels.keys()):
        count = stats.task_levels[depth]
        pct = (count / stats.total_tasks) * 100
        bar = "█" * int(pct / 5)
        print(f"  Level {depth}: {count:3d} ({pct:5.1f}%) {bar}")

    # Time series
    if stats.first_timestamp and stats.last_timestamp:
        print("\n" + "=" * 70)
        print("📈 Time Series")
        print("=" * 70)
        from datetime import timedelta

        ts = create_time_series(parsed_logs, bucket_size=timedelta(minutes=1))
        data = ts.to_list()
        print(f"Generated {len(data)} time buckets")
        for point in data[:5]:
            print(f"  {point['timestamp']}: {point['count']} tasks, "
                  f"{point['errors']} errors")

    # Render tree at the end
    print("\n" + "=" * 70)
    print("🌲 Task Tree")
    print("=" * 70)
    tasks = tasks_from_iterable(parsed_logs)
    render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50, human_readable=True)


if __name__ == "__main__":
    main()
