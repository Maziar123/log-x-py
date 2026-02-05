#!/usr/bin/env python3
"""
Example 11: Async Tasks with Concurrent Operations

Demonstrates async/await patterns with concurrent task execution,
timeout handling, and task group coordination.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "../../src")

from logxpy_cli_view import (
    calculate_statistics,
    filter_by_action_type,
    print_statistics,
    render_tasks,
    tasks_from_iterable,
)


def main() -> None:
    log_file = Path("async_tasks.log")

    with open(log_file) as f:
        log_entries = [line.strip() for line in f if line.strip()]

    parsed_logs = [json.loads(line) for line in log_entries]

    print("=" * 80)
    print("Example 11: Async Tasks with Concurrent Operations")
    print("=" * 80)
    print("\nScenario: Batch processing with concurrent data fetching")
    print("Demonstrates async patterns: task groups, concurrent execution,")
    print("and coordination between parallel operations.\n")

    # Full tree rendering with color
    print("=" * 80)
    print("🌲 Full Async Task Tree")
    print("=" * 80)
    tasks = tasks_from_iterable(parsed_logs)
    render_tasks(
        write=sys.stdout.write,
        tasks=tasks,
        field_limit=70,
        human_readable=True,
        colorize_tree=True,
    )

    # Statistics
    print("\n" + "=" * 80)
    print("📊 Async Task Statistics")
    print("=" * 80)
    stats = calculate_statistics(parsed_logs)
    print_statistics(stats)

    # Concurrent task analysis
    print("\n" + "=" * 80)
    print("⚡ Concurrent Execution Analysis")
    print("=" * 80)

    # Find tasks that ran concurrently (same parent, overlapping timestamps)
    concurrent_groups = {}
    for log in parsed_logs:
        level = log.get("task_level", [])
        if len(level) == 4:  # Level 4 tasks under async_task_group
            parent_key = tuple(level[:3])
            if parent_key not in concurrent_groups:
                concurrent_groups[parent_key] = []
            concurrent_groups[parent_key].append(log)

    print(f"\nFound {len(concurrent_groups)} concurrent task group(s)")
    for parent, tasks in concurrent_groups.items():
        print(f"\n  Task Group {parent}:")
        for t in tasks:
            if t.get("action_status") == "started":
                print(f"    ⚡ {t.get('action_type')} started at {t.get('timestamp')}")

    # Filter specific action types
    print("\n" + "=" * 80)
    print("🔍 Database Operations Only")
    print("=" * 80)
    db_tasks = list(filter(filter_by_action_type("database_query"), parsed_logs))
    tasks = tasks_from_iterable(db_tasks)
    render_tasks(
        write=sys.stdout.write,
        tasks=tasks,
        field_limit=60,
        human_readable=True,
    )

    print("\n" + "=" * 80)
    print("✅ Async task demonstration complete!")
    print("=" * 80)
    print("\nKey metrics:")
    print(f"  • Total log entries: {len(parsed_logs)}")
    print("  • Concurrent tasks executed: 3 (user, orders, prefs)")
    print(f"  • Success rate: {stats.success_rate:.1f}%")
    print(f"  • Processing time: {max(log['timestamp'] for log in parsed_logs) - min(log['timestamp'] for log in parsed_logs):.3f}s")


if __name__ == "__main__":
    main()
