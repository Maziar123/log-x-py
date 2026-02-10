#!/usr/bin/env python3
"""
Example 09: Generating Eliot Logs

This example shows how to generate Eliot logs programmatically
and demonstrates the new export and statistics features.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def generate_log_entry(
    task_uuid: str,
    action_type: str,
    action_status: str,  # "started", "succeeded", "failed"
    task_level: list[int],
    message: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """Generate a single Eliot log entry with proper action_status."""
    entry = {
        "task_uuid": task_uuid,
        "action_type": action_type,
        "action_status": action_status,
        "timestamp": datetime.now(timezone.utc).timestamp(),
        "task_level": task_level,
    }
    if message:
        entry["message"] = message
    entry.update(extra)
    return entry


def create_sample_workflow() -> list[dict[str, Any]]:
    """Generate a sample workflow with nested tasks."""
    parent_uuid = str(uuid.uuid4())
    logs = []

    # Parent task start
    logs.append(generate_log_entry(
        parent_uuid,
        "workflow:start",
        "started",
        [1],
        message="Starting data processing workflow",
        workflow_name="daily_sync",
        source_system="external_api",
    ))

    # Child task 1: Fetch data
    child1_uuid = str(uuid.uuid4())
    logs.append(generate_log_entry(
        child1_uuid,
        "fetch_data",
        "started",
        [1, 1],
        message="Fetching data from external API",
        endpoint="https://api.example.com/data",
    ))
    logs.append(generate_log_entry(
        child1_uuid,
        "fetch_data",
        "succeeded",
        [1, 2],
        message="Data fetched successfully",
        records_received=500,
        duration=2.5,
    ))

    # Child task 2: Process data
    child2_uuid = str(uuid.uuid4())
    logs.append(generate_log_entry(
        child2_uuid,
        "process_data",
        "started",
        [1, 1],
        message="Processing fetched data",
        processing_mode="batch",
    ))

    # Grandchild: Validate
    grandchild_uuid = str(uuid.uuid4())
    logs.append(generate_log_entry(
        grandchild_uuid,
        "validate",
        "started",
        [1, 1, 1],
        message="Validating data structure",
    ))
    logs.append(generate_log_entry(
        grandchild_uuid,
        "validate",
        "succeeded",
        [1, 1, 2],
        message="Validation complete",
        validation_errors=0,
        duration=0.5,
    ))

    logs.append(generate_log_entry(
        child2_uuid,
        "process_data",
        "succeeded",
        [1, 2],
        message="Data processing complete",
        records_processed=500,
        duration=5.0,
    ))

    # End parent task
    logs.append(generate_log_entry(
        parent_uuid,
        "workflow:start",
        "succeeded",
        [2],
        message="Workflow completed successfully",
        duration=8.0,
    ))

    return logs


def main() -> None:
    """Generate and write sample logs."""
    # Use logxpy_cli_view instead of eliottree2
    from logxpy_cli_view import (
        calculate_statistics,
        export_tasks,
        print_statistics,
        render_tasks,
        tasks_from_iterable,
    )
    import sys

    logs = create_sample_workflow()

    output_file = Path("generated_sample.log")
    with open(output_file, "w") as f:
        for log in logs:
            f.write(json.dumps(log) + "\n")

    print("=" * 70)
    print("Example 09: Generated Eliot Logs")
    print("=" * 70)
    print(f"\nGenerated {len(logs)} log entries")
    print(f"Output: {output_file}")

    # NEW: Show statistics
    print("\n" + "=" * 70)
    print("📊 Generated Log Statistics")
    print("=" * 70)
    stats = calculate_statistics(logs)
    print_statistics(stats)

    # NEW: Render the generated logs
    print("\n" + "=" * 70)
    print("🌲 Rendering Generated Logs")
    print("=" * 70)
    with open(output_file) as f:
        entries = [json.loads(line.strip()) for line in f if line.strip()]
    tasks = tasks_from_iterable(entries)
    render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50, human_readable=True)

    # NEW: Export to HTML
    print("\n" + "=" * 70)
    print("📁 Exporting to HTML")
    print("=" * 70)
    # Re-parse entries for export
    with open(output_file) as f:
        entries = [json.loads(line.strip()) for line in f if line.strip()]
    tasks = tasks_from_iterable(entries)
    export_tasks(
        tasks,
        "/tmp/generated_sample.html",
        format="html",
        title="Generated Workflow Report",
    )
    print("✓ Exported to /tmp/generated_sample.html")

    print("\n" + "=" * 70)
    print("To view the generated logs:")
    print(f"  logxpy-view render {output_file}")
    print(f"  logxpy-view stats {output_file}")
    print(f"  logxpy-view export -f html -o report.html {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
