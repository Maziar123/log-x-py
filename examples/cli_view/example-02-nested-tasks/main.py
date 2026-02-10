#!/usr/bin/env python3
"""
Example 02: Nested Tasks

This example demonstrates rendering tasks with nested children
and shows task level analysis.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "../../src")

from logxpy_cli_view import (
    calculate_statistics,
    filter_by_task_level,
    render_tasks,
    tasks_from_iterable,
)


def main() -> None:
    log_file = Path("nested_tasks.log")

    with open(log_file) as f:
        log_entries = [line.strip() for line in f if line.strip()]

    parsed_logs = [json.loads(line) for line in log_entries]
    tasks = tasks_from_iterable(parsed_logs)

    print("=" * 70)
    print("Example 02: Nested Task Tree (Full)")
    print("=" * 70)
    import sys
    render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50, human_readable=True)

    # NEW: Task level analysis
    print("\n" + "=" * 70)
    print("🔢 Task Level Analysis")
    print("=" * 70)

    stats = calculate_statistics(parsed_logs)
    print("\nTasks by depth level:")
    for level in sorted(stats.task_levels.keys()):
        count = stats.task_levels[level]
        bar = "█" * count
        print(f"  Level {level}: {count:3d} {bar}")

    # NEW: Filter by task level
    print("\n" + "=" * 70)
    print("🔍 Top-Level Tasks Only (Level 1)")
    print("=" * 70)
    top_level = list(filter(filter_by_task_level(max_level=1), parsed_logs))
    tasks = tasks_from_iterable(top_level)
    render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50)

    print(f"\nShowing {len(top_level)} of {len(parsed_logs)} tasks")


if __name__ == "__main__":
    main()
