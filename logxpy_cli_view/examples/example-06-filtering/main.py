#!/usr/bin/env python3
"""
Example 06: Filtering Tasks

This example demonstrates all the new filtering capabilities.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "../../src")

from logxpy_cli_view import (
    combine_filters_and,
    combine_filters_not,
    combine_filters_or,
    filter_by_action_status,
    filter_by_action_type,
    filter_by_duration,
    filter_by_field_exists,
    filter_by_keyword,
    filter_by_task_level,
    render_tasks,
    tasks_from_iterable,
)


def main() -> None:
    log_file = Path("web_service.log")

    with open(log_file) as f:
        log_entries = [line.strip() for line in f if line.strip()]

    parsed_logs = [json.loads(line) for line in log_entries]

    print("=" * 70)
    print("Example 06a: All Tasks (Unfiltered)")
    print("=" * 70)
    tasks = tasks_from_iterable(parsed_logs)
    render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50)
    print(f"\nTotal: {len(parsed_logs)} tasks")

    # Filter 1: By status
    print("\n" + "=" * 70)
    print("🔍 Filter 1: Failed Tasks Only")
    print("=" * 70)
    failed = list(filter(filter_by_action_status("failed"), parsed_logs))
    if failed:
        tasks = tasks_from_iterable(failed)
        render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50)
        print(f"\nFound {len(failed)} failed tasks")
    else:
        print("No failed tasks")

    # Filter 2: By action type (regex)
    print("\n" + "=" * 70)
    print("🔍 Filter 2: HTTP Requests (regex: http:.*)")
    print("=" * 70)
    http = list(filter(
        filter_by_action_type(r"http:.*", regex=True),
        parsed_logs
    ))
    if http:
        tasks = tasks_from_iterable(http)
        render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50)
        print(f"\nFound {len(http)} HTTP tasks")

    # Filter 3: By duration
    print("\n" + "=" * 70)
    print("🔍 Filter 3: Slow Tasks (> 1 second)")
    print("=" * 70)
    slow = list(filter(filter_by_duration(min_seconds=1.0), parsed_logs))
    if slow:
        tasks = tasks_from_iterable(slow)
        render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50)
        print(f"\nFound {len(slow)} slow tasks")
    else:
        print("No slow tasks found")

    # Filter 4: By field existence
    print("\n" + "=" * 70)
    print("🔍 Filter 4: Tasks with 'error' field")
    print("=" * 70)
    with_errors = list(filter(filter_by_field_exists("error"), parsed_logs))
    if with_errors:
        tasks = tasks_from_iterable(with_errors)
        render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50)
        print(f"\nFound {len(with_errors)} tasks with errors")
    else:
        print("No tasks with error field")

    # Filter 5: By keyword
    print("\n" + "=" * 70)
    print("🔍 Filter 5: Tasks containing 'database'")
    print("=" * 70)
    db_tasks = list(filter(filter_by_keyword("database"), parsed_logs))
    if db_tasks:
        tasks = tasks_from_iterable(db_tasks)
        render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50)
        print(f"\nFound {len(db_tasks)} database-related tasks")
    else:
        print("No database-related tasks")

    # Filter 6: Combined filters (AND)
    print("\n" + "=" * 70)
    print("🔍 Filter 6: Failed HTTP requests (AND)")
    print("=" * 70)
    combined = list(filter(
        combine_filters_and(
            filter_by_action_status("failed"),
            filter_by_action_type(r"http:.*", regex=True),
        ),
        parsed_logs
    ))
    if combined:
        tasks = tasks_from_iterable(combined)
        render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50)
        print(f"\nFound {len(combined)} failed HTTP requests")
    else:
        print("No failed HTTP requests")

    # Filter 7: Combined filters (OR)
    print("\n" + "=" * 70)
    print("🔍 Filter 7: Database OR Auth tasks (OR)")
    print("=" * 70)
    combined_or = list(filter(
        combine_filters_or(
            filter_by_keyword("database"),
            filter_by_keyword("auth"),
        ),
        parsed_logs
    ))
    if combined_or:
        tasks = tasks_from_iterable(combined_or)
        render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50)
        print(f"\nFound {len(combined_or)} database or auth tasks")
    else:
        print("No database or auth tasks")

    # Filter 8: Negation
    print("\n" + "=" * 70)
    print("🔍 Filter 8: All EXCEPT GET requests (NOT)")
    print("=" * 70)
    not_get = list(filter(
        combine_filters_not(filter_by_action_type("http:request:get")),
        parsed_logs
    ))
    if not_get:
        tasks = tasks_from_iterable(not_get)
        render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50)
        print(f"\nFound {len(not_get)} non-GET tasks")

    # Filter 9: By task level
    print("\n" + "=" * 70)
    print("🔍 Filter 9: Top-level tasks only (max_level=1)")
    print("=" * 70)
    top_level = list(filter(filter_by_task_level(max_level=1), parsed_logs))
    if top_level:
        tasks = tasks_from_iterable(top_level)
        render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50)
        print(f"\nFound {len(top_level)} top-level tasks")

    print("\n" + "=" * 70)
    print("✅ All filtering examples complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
