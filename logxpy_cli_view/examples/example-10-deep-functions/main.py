#!/usr/bin/env python3
"""
Example 10: Deep Function Call Tree

This example demonstrates a complex, deeply nested function call tree
with 6 levels of nesting, simulating a real-world web request handling
scenario with authentication, validation, business logic, and persistence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "../../src")

from logxpy_cli_view import (
    calculate_statistics,
    filter_by_task_level,
    print_statistics,
    render_tasks,
    tasks_from_iterable,
)


def main() -> None:
    log_file = Path("deep_functions.log")

    with open(log_file) as f:
        log_entries = [line.strip() for line in f if line.strip()]

    parsed_logs = [json.loads(line) for line in log_entries]

    print("=" * 80)
    print("Example 10: Deep Function Call Tree (6 Levels Deep)")
    print("=" * 80)
    print("\nScenario: HTTP POST /api/v2/orders")
    print("A complex web request with full authentication, validation,")
    print("business logic processing, and event publishing.\n")

    # Full tree rendering
    print("=" * 80)
    print("Full Deep Tree (all 6 levels)")
    print("=" * 80)
    tasks = tasks_from_iterable(parsed_logs)
    render_tasks(
        write=sys.stdout.write,
        tasks=tasks,
        field_limit=60,
        human_readable=True,
        colorize_tree=True,
    )

    # Statistics
    print("\n" + "=" * 80)
    print("📊 Deep Tree Statistics")
    print("=" * 80)
    stats = calculate_statistics(parsed_logs)
    print_statistics(stats)

    # Show depth distribution
    print("\n" + "=" * 80)
    print("🔢 Nesting Depth Analysis")
    print("=" * 80)

    depth_counts: dict[int, int] = {}
    for log in parsed_logs:
        depth = len(log.get("task_level", []))
        depth_counts[depth] = depth_counts.get(depth, 0) + 1

    print("\nEntries by nesting depth:")
    max_depth = max(depth_counts.keys())
    for depth in range(1, max_depth + 1):
        count = depth_counts.get(depth, 0)
        bar = "█" * count
        indent = "  " * (depth - 1)
        print(f"  Level {depth}: {count:3d} {bar}")
        if depth < max_depth:
            print(f"{indent}    ↓")

    # Show call path for deepest level
    print("\n" + "=" * 80)
    print("🔍 Deepest Call Path (Level 6)")
    print("=" * 80)

    deepest = [log for log in parsed_logs if len(log.get("task_level", [])) == 6]
    for log in deepest:
        action = log.get("action_type", "unknown")
        status = log.get("action_status", "unknown")
        print(f"  → {action} [{status}]")

    # Filter by levels
    print("\n" + "=" * 80)
    print("🔍 Top-Level Only (Level 1)")
    print("=" * 80)
    top_level = list(filter(filter_by_task_level(max_level=1), parsed_logs))
    tasks = tasks_from_iterable(top_level)
    render_tasks(
        write=sys.stdout.write,
        tasks=tasks,
        field_limit=50,
        human_readable=True,
    )
    print(f"\nShowing {len(top_level)} of {len(parsed_logs)} entries")

    print("\n" + "=" * 80)
    print("✅ Deep function tree demonstration complete!")
    print("=" * 80)
    print("\nKey metrics:")
    print(f"  • Total log entries: {len(parsed_logs)}")
    print(f"  • Unique tasks: {len(set(log['task_uuid'] for log in parsed_logs))}")
    print(f"  • Max nesting depth: {max_depth} levels")
    print(f"  • Action types: {len(set(log.get('action_type') for log in parsed_logs))}")
    print(f"  • Total processing time: {max(log['timestamp'] for log in parsed_logs) - min(log['timestamp'] for log in parsed_logs):.3f}s")


if __name__ == "__main__":
    main()
