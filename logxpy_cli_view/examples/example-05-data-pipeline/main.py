#!/usr/bin/env python3
"""
Example 05: Data Pipeline (ETL)

This example shows a complete ETL pipeline with export to different formats
and time series analysis.
"""

from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, "../../src")

from logxpy_cli_view import (
    ExportOptions,
    calculate_statistics,
    create_time_series,
    export_tasks,
    render_tasks,
    tasks_from_iterable,
)


def main() -> None:
    log_file = Path("data_pipeline.log")

    with open(log_file) as f:
        log_entries = [line.strip() for line in f if line.strip()]

    parsed_logs = [json.loads(line) for line in log_entries]

    print("=" * 70)
    print("Example 05: ETL Pipeline (Extract, Transform, Load)")
    print("=" * 70)
    tasks = tasks_from_iterable(parsed_logs)
    import sys
    render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50, human_readable=True)

    # NEW: Statistics
    print("\n" + "=" * 70)
    print("📊 Pipeline Statistics")
    print("=" * 70)

    stats = calculate_statistics(parsed_logs)
    print(f"Total stages: {stats.total_tasks}")
    print(f"Successful: {stats.successful_tasks}")
    print(f"Failed: {stats.failed_tasks}")

    if stats.time_span:
        print(f"Total time: {stats.time_span}")

    if stats.duration_stats["count"] > 0:
        print(f"Avg stage duration: {stats.duration_stats['mean']:.3f}s")
        print(f"Max stage duration: {stats.duration_stats['max']:.3f}s")

    # NEW: Time series analysis
    print("\n" + "=" * 70)
    print("📈 Time Series Analysis")
    print("=" * 70)

    ts = create_time_series(parsed_logs, bucket_size=timedelta(minutes=1))
    data = ts.to_list()

    print(f"\nGenerated {len(data)} time buckets:")
    for point in data[:5]:  # Show first 5
        print(f"  {point['timestamp']}: {point['count']} tasks, "
              f"{point['errors']} errors")

    # NEW: Export to all formats
    print("\n" + "=" * 70)
    print("📁 Exporting Pipeline Data")
    print("=" * 70)

    tasks = tasks_from_iterable(parsed_logs)
    export_tasks(
        tasks,
        "/tmp/pipeline.json",
        format="json",
        options=ExportOptions(indent=2),
    )
    print("✓ Exported to /tmp/pipeline.json")

    tasks = tasks_from_iterable(parsed_logs)
    export_tasks(tasks, "/tmp/pipeline.csv", format="csv")
    print("✓ Exported to /tmp/pipeline.csv")

    tasks = tasks_from_iterable(parsed_logs)
    export_tasks(
        tasks,
        "/tmp/pipeline.html",
        format="html",
        title="ETL Pipeline Report",
    )
    print("✓ Exported to /tmp/pipeline.html")
    print("\nOpen /tmp/pipeline.html to see the interactive report!")


if __name__ == "__main__":
    main()
