#!/usr/bin/env python3
"""
View logs using logxpy_cli_view (eliottree) API directly
This bypasses the CLI and uses the Python API directly
"""

import json
import sys
from pathlib import Path

# Add both paths
sys.path.insert(0, str(Path(__file__).parent.parent / "logxpy_cli_view" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logxpy"))

# Import the core eliottree functionality
from eliottree import render_tasks, tasks_from_iterable


def view_log(log_file):
    """View a log file with tree rendering using eliottree."""
    log_path = Path(log_file)

    if not log_path.exists():
        print(f"Error: Log file not found: {log_file}")
        return

    print(f"\n{'=' * 70}")
    print(f"Viewing: {log_path.name}")
    print(f"File: {log_path}")
    print(f"{'=' * 70}\n")

    # Read and parse log entries
    with open(log_path) as f:
        log_entries = [json.loads(line) for line in f if line.strip()]

    print(f"Total log entries: {len(log_entries)}\n")

    # Convert to tasks
    tasks = tasks_from_iterable(log_entries)

    # Render with tree structure
    render_tasks(
        write=sys.stdout.write,
        tasks=tasks,
        human_readable=True,
        colorize=False,  # Disable colors to avoid colored dependency
        field_limit=100,
    )

    print(f"\n{'=' * 70}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python view_with_logxpy_cli_view.py <log_file>")
        print("\nExample:")
        print("  python view_with_logxpy_cli_view.py example_01_basic.log")
        sys.exit(1)

    view_log(sys.argv[1])
