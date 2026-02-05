#!/usr/bin/env python3
"""
Modern demo showing tree rendering with logxpy_cli_view using Python 3.12+.

Demonstrates tree rendering capabilities without package installation.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

type LogEntry = dict[str, Any]

# Add logxpy_cli_view to path
sys.path.insert(0, str(Path(__file__).parent / "logxpy_cli_view" / "src"))


# Sample Eliot log data
SAMPLE_LOGS: list[LogEntry] = [
    {
        "task_uuid": "f3a32bb3-ea6b-457c-aa99-08a3d0491ab4",
        "action_type": "app:soap:client:request",
        "action_status": "started",
        "timestamp": 1425356936.278875,
        "task_level": [1],
        "dump": "/home/user/dump_files/20150303/1425356936.28_Client_req.xml",
        "uri": "http://example.org/soap",
        "soapAction": "a_soap_action",
    },
    {
        "timestamp": 1425356937.516579,
        "task_uuid": "f3a32bb3-ea6b-457c-aa99-08a3d0491ab4",
        "action_type": "app:soap:client:success",
        "action_status": "started",
        "task_level": [2, 1],
    },
    {
        "task_uuid": "f3a32bb3-ea6b-457c-aa99-08a3d0491ab4",
        "action_type": "app:soap:client:success",
        "dump": "/home/user/dump_files/20150303/1425356937.52_Client_res.xml",
        "timestamp": 1425356937.517077,
        "action_status": "succeeded",
        "task_level": [2, 2],
    },
    {
        "status": 200,
        "task_uuid": "f3a32bb3-ea6b-457c-aa99-08a3d0491ab4",
        "task_level": [3],
        "action_type": "app:soap:client:request",
        "timestamp": 1425356937.517161,
        "action_status": "succeeded",
    },
]


def print_section(title: str, width: int = 70) -> None:
    """Print formatted section header."""
    print(f"\n{'=' * width}")
    print(title)
    print(f"{'=' * width}\n")


def demo_tree_rendering() -> None:
    """Run tree rendering demos with modern Python 3.12+ features."""
    try:
        from logxpy_cli_view import ThemeMode, get_theme, render_tasks, tasks_from_iterable

        # Demo 1: Dark Theme with Unicode
        print_section("DEMO: Tree Rendering with Dark Theme (Unicode)")

        tasks = tasks_from_iterable(SAMPLE_LOGS)
        theme = get_theme(ThemeMode.DARK)
        render_tasks(
            write=sys.stdout.write,
            tasks=tasks,
            field_limit=100,
            theme=theme,
            colorize_tree=True,
        )

        # Demo 2: ASCII Mode
        print_section("DEMO: Tree Rendering with ASCII mode (no Unicode)")

        tasks = tasks_from_iterable(SAMPLE_LOGS)
        render_tasks(
            write=sys.stdout.write,
            tasks=tasks,
            field_limit=100,
            ascii=True,
        )

        # Success message
        print_section("SUCCESS: Tree rendering is working!")

        features = [
            "Tree structure with Unicode box-drawing characters",
            "Rich colored output (Dark/Light themes)",
            "ASCII-only mode for plain terminals",
            "Task hierarchies and nesting",
            "Timestamps and duration indicators",
            "Status indicators (started/succeeded/failed)",
        ]

        print("Features available:")
        for feature in features:
            print(f"  ✓ {feature}")
        print()

    except ImportError as e:
        print(f"Error: Missing dependencies - {e}\n")
        print("To see tree rendering in action, install dependencies:\n")

        instructions = [
            "1. Create a virtual environment:",
            "   python -m venv venv",
            "   source venv/bin/activate",
            "",
            "2. Install the package:",
            "   cd logxpy_cli_view",
            "   pip install -e .",
            "",
            "3. Run this demo again:",
            "   python demo_tree_render.py",
        ]

        for instruction in instructions:
            print(instruction)

        sys.exit(1)


if __name__ == "__main__":
    demo_tree_rendering()
