#!/usr/bin/env python3
"""
15_aggregation.py - Aggregation Feature

Demonstrates aggregation capabilities:
- LogAggregator: Multi-file analysis
- MultiFileAnalyzer: Cross-file analysis
- Time series across files
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from datetime import datetime

# Create sample logs first
from logxpy import log, to_file, start_action


def create_sample_logs() -> list[Path]:
    """Create multiple sample log files."""
    log_files = []

    # Create 3 log files simulating different servers
    for server_id in [1, 2, 3]:
        log_file = tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            suffix=f"_server{server_id}.log"
        )
        log_path = Path(log_file.name)

        if log_path.exists():
            log_path.unlink()
        with open(log_path, "w", encoding="utf-8") as f:
            to_file(f)

        # Generate entries for each server
        log.info(f"Server {server_id} started")

        with start_action("process_request", server=server_id):
            log.info(f"Handling request on server {server_id}")
            if server_id == 2:
                log.error(f"Server {server_id} overload")
            else:
                log.success(f"Request completed on server {server_id}")

        log.warning(f"Server {server_id} high CPU", cpu_percent=80 + server_id * 5)
        log.info(f"Server {server_id} shutting down")

        log_files.append(log_path)

    return log_files


def main():
    """Demonstrate aggregation functionality."""
    from logxy_log_parser.aggregation import LogAggregator, MultiFileAnalyzer
    from logxy_log_parser import TimeSeriesAnalyzer, LogAnalyzer

    # Create sample logs
    log_paths = create_sample_logs()
    print(f"Created {len(log_paths)} sample log files")
    for p in log_paths:
        print(f"  - {p.name}")

    # ========================================
    # 1. LOG AGGREGATOR - Multi-File Analysis
    # ========================================
    print("\n" + "=" * 60)
    print("1. LOG AGGREGATOR - Combine Multiple Log Files")
    print("=" * 60)

    aggregator = LogAggregator(log_paths)

    # Aggregate all entries
    def progress_callback(current: int, total: int):
        print(f"  Processing file {current}/{total}...")

    entries = aggregator.aggregate(progress_callback=progress_callback)
    print(f"Aggregated {len(entries)} total entries")

    # Show aggregation stats
    stats = aggregator.stats
    print(f"\nAggregation Statistics:")
    print(f"  Total entries: {stats.total_entries}")
    print(f"  Total files: {stats.total_files}")
    print(f"  Unique tasks: {stats.unique_tasks}")

    # Show level counts
    print(f"\nLevel distribution:")
    for level, count in stats.level_counts.items():
        print(f"  {level}: {count}")

    # ========================================
    # 2. MULTI-FILE ANALYZER - Cross-File Analysis
    # ========================================
    print("\n" + "=" * 60)
    print("2. MULTI-FILE ANALYZER - Comprehensive Cross-File Analysis")
    print("=" * 60)

    analyzer = MultiFileAnalyzer(
        directory=tempfile.gettempdir(),
        pattern="*_server*.log"
    )

    print(f"Files found: {analyzer.file_count}")
    analysis = analyzer.analyze_all()

    print(f"\nCross-File Analysis:")
    print(f"  Directory: {analysis['directory']}")
    print(f"  Files analyzed: {len(analysis['files'])}")

    agg_stats = analysis["aggregation_stats"]
    print(f"\n  Total entries: {agg_stats['total_entries']}")
    print(f"  Level distribution:")
    for level, count in agg_stats["level_counts"].items():
        print(f"    {level}: {count}")

    error_summary = analysis["error_summary"]
    print(f"\n  Error summary:")
    print(f"    Total errors: {error_summary['total_count']}")
    print(f"    Unique error types: {error_summary['unique_types']}")

    print(f"\n  Slowest actions:")
    for action, duration in analysis["slowest_actions"][:3]:
        print(f"    {action}: {duration:.3f}s")

    # ========================================
    # 3. TIME SERIES ACROSS FILES
    # ========================================
    print("\n" + "=" * 60)
    print("3. TIME SERIES ACROSS FILES - Temporal Analysis")
    print("=" * 60)

    ts_data = analyzer.time_series_analysis(interval_seconds=3600)
    print(f"Time series data points: {len(ts_data)}")

    for point in ts_data[:5]:
        print(f"  {point['timestamp']:.2f}: "
              f"{point['count']} entries, "
              f"{point['error_count']} errors, "
              f"error_rate={point['error_rate']:.2%}")

    # ========================================
    # 4. PER-FILE STATISTICS
    # ========================================
    print("\n" + "=" * 60)
    print("4. PER-FILE STATISTICS - Individual File Analysis")
    print("=" * 60)

    for file_path, file_stats in stats.file_stats.items():
        file_name = Path(file_path).name
        print(f"\n  File: {file_name}")
        print(f"    Entries: {file_stats['entries']}")
        print(f"    Level counts:")
        for level, count in file_stats["level_counts"].items():
            print(f"      {level}: {count}")

    # ========================================
    # 5. COMBINED ANALYZER - Full Analysis on Aggregated Data
    # ========================================
    print("\n" + "=" * 60)
    print("5. COMBINED ANALYZER - Full Analysis on Aggregated Entries")
    print("=" * 60)

    combined_analyzer = LogAnalyzer(entries)
    error_summary = combined_analyzer.error_summary()

    print(f"\nCombined Error Analysis:")
    print(f"  Total errors: {error_summary.total_count}")
    print(f"  Unique types: {error_summary.unique_types}")
    print(f"  Most common: {error_summary.most_common[0]}")

    print(f"\nError Breakdown:")
    print(f"  By level:")
    for level, count in error_summary.by_level.items():
        print(f"    {level}: {count}")
    print(f"  By action:")
    for action, count in error_summary.by_action.items():
        print(f"    {action}: {count}")

    # ========================================
    # 6. DEEPEST NESTING ACROSS FILES
    # ========================================
    print("\n" + "=" * 60)
    print("6. DEEPEST NESTING - Find Maximum Depth")
    print("=" * 60)

    deepest = combined_analyzer.deepest_nesting()
    print(f"Deepest nesting level: {deepest}")

    widest = combined_analyzer.widest_tasks()
    print(f"\nWidest tasks (top 3):")
    for task_uuid, count in widest[:3]:
        print(f"  {task_uuid}: {count} entries")

    # Cleanup
    for log_path in log_paths:
        log_path.unlink()

    print("\n" + "=" * 60)
    print("Aggregation demonstration complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
