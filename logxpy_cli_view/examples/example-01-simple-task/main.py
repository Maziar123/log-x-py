#!/usr/bin/env python3
"""
Example 01: Simple Task Rendering

This example shows basic rendering of Eliot logs and introduces
the new export and statistics features.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "../../src")

from logxpy_cli_view import (
    ExportOptions,
    calculate_statistics,
    export_tasks,
    render_tasks,
    tasks_from_iterable,
)


def main() -> None:
    log_file = Path("simple_task.log")

    with open(log_file) as f:
        log_entries = [line.strip() for line in f if line.strip()]

    # Parse JSON for statistics
    parsed_logs = [json.loads(line) for line in log_entries]

    # Parse into tasks
    tasks = tasks_from_iterable(parsed_logs)

    print("=" * 70)
    print("Example 01: Simple Task Tree")
    print("=" * 70)
    import sys
    render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50, human_readable=True)

    # NEW: Show statistics
    print("\n" + "=" * 70)
    print("📊 Statistics")
    print("=" * 70)
    stats = calculate_statistics(parsed_logs)
    print(f"Total tasks: {stats.total_tasks}")
    print(f"Successful: {stats.successful_tasks} ({stats.success_rate:.1f}%)")
    print(f"Failed: {stats.failed_tasks} ({stats.failure_rate:.1f}%)")

    if stats.duration_stats["count"] > 0:
        print(f"Avg duration: {stats.duration_stats['mean']:.3f}s")

    # NEW: Export to different formats
    print("\n" + "=" * 70)
    print("📁 Export Examples (saved to /tmp/)")
    print("=" * 70)

    tasks = tasks_from_iterable(parsed_logs)  # Re-parse for export

    # Export to JSON
    export_tasks(
        tasks,
        "/tmp/example_01.json",
        format="json",
        options=ExportOptions(indent=2),
    )
    print("✓ Exported to /tmp/example_01.json")

    # Export to CSV
    tasks = tasks_from_iterable(parsed_logs)
    export_tasks(tasks, "/tmp/example_01.csv", format="csv")
    print("✓ Exported to /tmp/example_01.csv")

    # Export to HTML
    tasks = tasks_from_iterable(parsed_logs)
    export_tasks(
        tasks,
        "/tmp/example_01.html",
        format="html",
        title="Example 01: Simple Tasks",
    )
    print("✓ Exported to /tmp/example_01.html")
    print("\nOpen /tmp/example_01.html in your browser!")


if __name__ == "__main__":
    main()
