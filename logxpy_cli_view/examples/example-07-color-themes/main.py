#!/usr/bin/env python3
"""
Example 07: Color Themes

This example shows different color themes and the new ThemeMode enum.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "../../src")

from logxpy_cli_view import ThemeMode, get_theme, render_tasks, tasks_from_iterable


def main() -> None:
    log_file = Path("with_errors.log")

    with open(log_file) as f:
        log_entries = [line.strip() for line in f if line.strip()]

    # Parse JSON for tasks_from_iterable
    parsed_logs = [json.loads(line) for line in log_entries]

    print("=" * 70)
    print("Example 07a: Dark Theme (using ThemeMode enum)")
    print("=" * 70)
    tasks = tasks_from_iterable(parsed_logs)
    theme = get_theme(ThemeMode.DARK)
    render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50, theme=theme)

    print("\n" + "=" * 70)
    print("Example 07b: Light Theme (using ThemeMode enum)")
    print("=" * 70)
    tasks = tasks_from_iterable(parsed_logs)
    theme = get_theme(ThemeMode.LIGHT)
    render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50, theme=theme)

    print("\n" + "=" * 70)
    print("Example 07c: Auto Theme (detects terminal)")
    print("=" * 70)
    tasks = tasks_from_iterable(parsed_logs)
    theme = get_theme(ThemeMode.AUTO)
    render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50, theme=theme)

    print("\n" + "=" * 70)
    print("Example 07d: ASCII mode (no Unicode)")
    print("=" * 70)
    tasks = tasks_from_iterable(parsed_logs)
    render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50, ascii=True)

    print("\n" + "=" * 70)
    print("Example 07e: No colors + ASCII (plain text)")
    print("=" * 70)
    tasks = tasks_from_iterable(parsed_logs)
    theme = get_theme(ThemeMode.DARK)  # Theme without colorize
    render_tasks(
        write=sys.stdout.write,
        tasks=tasks,
        field_limit=50,
        ascii=True,
        theme=theme,
    )


if __name__ == "__main__":
    main()
