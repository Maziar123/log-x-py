#!/usr/bin/env python3
"""
Example 03: Error Handling

This example shows how failed tasks are displayed and demonstrates
error analysis features.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "../../src")

from logxpy_cli_view import (
    calculate_statistics,
    filter_by_action_status,
    filter_by_keyword,
    print_statistics,
    render_tasks,
    tasks_from_iterable,
)


def main() -> None:
    log_file = Path("with_errors.log")

    with open(log_file) as f:
        log_entries = [line.strip() for line in f if line.strip()]

    parsed_logs = [json.loads(line) for line in log_entries]

    print("=" * 70)
    print("Example 03: All Tasks (with errors highlighted)")
    print("=" * 70)
    tasks = tasks_from_iterable(parsed_logs)
    render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50, human_readable=True)

    # NEW: Error analysis
    print("\n" + "=" * 70)
    print("❌ Error Analysis")
    print("=" * 70)

    stats = calculate_statistics(parsed_logs)
    print_statistics(stats)

    # NEW: Filter to show only failed tasks
    print("\n" + "=" * 70)
    print("🔍 Failed Tasks Only")
    print("=" * 70)

    failed_tasks = list(filter(filter_by_action_status("failed"), parsed_logs))
    if failed_tasks:
        tasks = tasks_from_iterable(failed_tasks)
        render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50)
        print(f"\nFound {len(failed_tasks)} failed tasks")
    else:
        print("No failed tasks found")

    # NEW: Search for specific error types
    print("\n" + "=" * 70)
    print("🔍 Tasks with 'Exception' or 'Error' keywords")
    print("=" * 70)

    error_tasks = list(filter(filter_by_keyword("exception"), parsed_logs))
    if error_tasks:
        tasks = tasks_from_iterable(error_tasks)
        render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50)
    else:
        print("No tasks with error keywords found")


if __name__ == "__main__":
    main()
