#!/usr/bin/env python3
"""
16_complete_reference.py - Complete Feature Reference

Comprehensive demonstration of ALL logxy-log-parser features:
- Simple One-Line API (check, parse, count_by, types)
- Indexing System (fast lookups)
- Powerful Filtering (by level, time, action type, field values)
- Time Series Analysis (anomaly detection, heatmaps, burst detection)
- Aggregation (multi-file analysis)
- Analysis (performance stats, error summaries, task trees)
- Export (JSON, CSV, HTML, Markdown, DataFrame)
- Real-time Monitoring (watch logs as they grow)
"""
from __future__ import annotations

import tempfile
from pathlib import Path

# Create sample log first
from logxpy import log, to_file, start_action


def create_comprehensive_sample_log() -> Path:
    """Create a comprehensive sample log file with all features."""
    log_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log")
    log_path = Path(log_file.name)

    if log_path.exists():
        log_path.unlink()
    with open(log_path, "w", encoding="utf-8") as f:
        to_file(f)

    # Generate diverse log entries demonstrating all features
    log.info("=== APPLICATION STARTUP ===")

    # Task 1: Database operations
    with start_action("database:connect", host="localhost", port=5432):
        log.info("Connecting to database")
        log.success("Connected to database")

    with start_action("database:query", table="users"):
        log.info("Executing query")
        log.debug("Query plan: Index Scan on users_pkey")
        log.success("Query completed", rows=150, duration_ms=23)

    # Task 2: API request with error
    with start_action("api:request", endpoint="/api/users", method="GET"):
        log.info("Processing API request")
        log.error("User not found", user_id=999, error_code="404")
        log.warning("Request completed with errors")

    # Task 3: Data processing pipeline
    with start_action("pipeline:etl", pipeline_id="daily"):
        log.info("Starting ETL pipeline")

        with start_action("pipeline:extract", source="database"):
            log.info("Extracting data")
            log.success("Extraction complete", records=5000)

        with start_action("pipeline:transform"):
            log.info("Transforming data")
            log.debug("Applying business rules")
            log.success("Transformation complete")

        with start_action("pipeline:load", destination="warehouse"):
            log.info("Loading to warehouse")
            log.success("Load complete")

    # Task 4: Error handling
    log.critical("Database connection pool exhausted", pool_size=10, active=15)
    log.error("Failed to process payment", order_id="ORD-12345", amount=99.99)

    # Task 5: Performance metrics
    with start_action("performance:scan"):
        log.info("Scanning for performance issues")
        log.warning("Slow query detected", query="SELECT * FROM logs", duration_ms=2500)
        log.note("Performance scan complete")

    log.info("=== APPLICATION SHUTDOWN ===")

    return log_path


def main():
    """Comprehensive demonstration of all features."""
    print("=" * 70)
    print("LOGXY LOG PARSER - COMPLETE FEATURE REFERENCE")
    print("=" * 70)

    # Create comprehensive sample log
    log_path = create_comprehensive_sample_log()
    print(f"\nCreated comprehensive sample log: {log_path}")

    # ========================================
    # 1. SIMPLE ONE-LINE API
    # ========================================
    print("\n" + "=" * 70)
    print("1. SIMPLE ONE-LINE API")
    print("=" * 70)

    from logxy_log_parser import check_log, parse_log, count_by, types

    # Quick check in one line
    result = check_log(log_path)
    print(f"check_log(): {len(result._entries)} entries parsed")

    # Parse entire file in one line
    entries = parse_log(log_path)
    print(f"parse_log(): {len(entries)} entries returned")

    # Count by level
    level_counts = count_by(entries, key="level")
    print(f"count_by(level): {dict(level_counts)}")

    # Get entry types
    entry_types = types(entries)
    print(f"types(): {len(set(e.message_type for e in entries))} unique types")

    # ========================================
    # 2. INDEXING SYSTEM
    # ========================================
    print("\n" + "=" * 70)
    print("2. INDEXING SYSTEM - Fast Lookups")
    print("=" * 70)

    from logxy_log_parser import LogIndex, IndexedLogParser

    index = LogIndex.build(log_path)
    print(f"LogIndex.build(): Index created with {len(index._entries)} entries")

    # Fast lookups
    errors = index.find_by_level("error")
    print(f"find_by_level('error'): {len(errors)} entries")

    if index._entries:
        first_task = index._entries[0].task_uuid
        task_entries = index.find_by_task(first_task)
        print(f"find_by_task(): {len(task_entries)} entries for {first_task}")

    # Indexed parser for queries
    parser = IndexedLogParser(log_path)
    query_result = parser.query(level="warning")
    print(f"IndexedLogParser.query(level='warning'): {len(query_result)} entries")

    # ========================================
    # 3. POWERFUL FILTERING
    # ========================================
    print("\n" + "=" * 70)
    print("3. POWERFUL FILTERING - Chainable Filters")
    print("=" * 70)

    from logxy_log_parser.filter import LogFilter

    f = LogFilter(entries)

    # Chain multiple filters
    results = (
        f.by_level("error", "critical")
         .by_action_type("database:*")
         .sort("timestamp", reverse=False)
         .limit(10)
    )
    print(f"Filtered (error/critical + database:*): {len(results)} entries")

    # By time range
    from datetime import datetime, timedelta

    if entries:
        first_ts = min(e.timestamp for e in entries)
        last_ts = max(e.timestamp for e in entries)
        time_results = f.by_time_range(first_ts, first_ts + (last_ts - first_ts) / 2)
        print(f"by_time_range(first half): {len(time_results)} entries")

    # By duration
    slow = f.slow_actions(threshold=0.001)
    print(f"slow_actions(>1ms): {len(slow)} entries")

    # ========================================
    # 4. TIME SERIES ANALYSIS
    # ========================================
    print("\n" + "=" * 70)
    print("4. TIME SERIES ANALYSIS")
    print("=" * 70)

    from logxy_log_parser import TimeSeriesAnalyzer

    ts_analyzer = TimeSeriesAnalyzer(entries)

    # Bucket by interval
    buckets = ts_analyzer.bucket_by_interval(interval_seconds=1)
    print(f"bucket_by_interval(1s): {len(buckets)} buckets created")

    # Detect anomalies
    anomalies = ts_analyzer.detect_anomalies(window_size=3, threshold=1.0)
    print(f"detect_anomalies(): {len(anomalies)} anomalies found")

    # Error rate trend
    error_trend = ts_analyzer.error_rate_trend(interval_seconds=1)
    print(f"error_rate_trend(): {len(error_trend)} data points")

    # Burst detection
    bursts = ts_analyzer.burst_detection(threshold=1.5, min_interval=0.5)
    print(f"burst_detection(): {len(bursts)} bursts detected")

    # Activity heatmap
    heatmap = ts_analyzer.activity_heatmap(hour_granularity=True)
    print(f"activity_heatmap(): {len(heatmap)} time periods analyzed")

    # ========================================
    # 5. AGGREGATION
    # ========================================
    print("\n" + "=" * 70)
    print("5. AGGREGATION - Multi-File Analysis")
    print("=" * 70)

    from logxy_log_parser.aggregation import MultiFileAnalyzer

    # Create additional log files for aggregation demo
    temp_dir = Path(tempfile.gettempdir())
    analyzer = MultiFileAnalyzer(temp_dir, pattern="*.log")

    log_files = list(temp_dir.glob("*.log"))[:3]  # Use first 3 log files
    if len(log_files) > 1:
        agg_analyzer = MultiFileAnalyzer(temp_dir, pattern=log_files[0].name.replace(str(temp_dir) + "/", "")[:8] + "*")
        print(f"MultiFileAnalyzer: Found {analyzer.file_count} log files")

        # Time series across files
        ts_data = analyzer.time_series_analysis(interval_seconds=3600)
        print(f"time_series_analysis(): {len(ts_data)} data points")

    # ========================================
    # 6. ANALYSIS
    # ========================================
    print("\n" + "=" * 70)
    print("6. ANALYSIS - Performance & Error Analysis")
    print("=" * 70)

    from logxy_log_parser import LogAnalyzer

    analyzer = LogAnalyzer(entries)

    # Performance stats
    slowest = analyzer.slowest_actions(n=3)
    print(f"slowest_actions(3): {[(s.action_type, s.mean_duration) for s in slowest]}")

    # Error summary
    error_summary = analyzer.error_summary()
    print(f"\nerror_summary():")
    print(f"  Total errors: {error_summary.total_count}")
    print(f"  Unique types: {error_summary.unique_types}")
    print(f"  Most common: {error_summary.most_common}")

    # Duration by action
    duration_by_action = analyzer.duration_by_action()
    print(f"\nduration_by_action(): {list(duration_by_action.keys())}")

    # Task analysis
    deepest = analyzer.deepest_nesting()
    print(f"\ndeepest_nesting(): {deepest} levels")

    # ========================================
    # 7. EXPORT
    # ========================================
    print("\n" + "=" * 70)
    print("7. EXPORT - Multiple Formats")
    print("=" * 70)

    from logxy_log_parser.filter import LogEntries

    log_entries = LogEntries(entries)
    output_dir = Path(tempfile.gettempdir()) / "logxy_exports"
    output_dir.mkdir(exist_ok=True)

    # JSON export
    log_entries.to_json(output_dir / "export.json")
    print(f"to_json(): Exported to {output_dir / 'export.json'}")

    # CSV export
    log_entries.to_csv(output_dir / "export.csv")
    print(f"to_csv(): Exported to {output_dir / 'export.csv'}")

    # HTML export
    log_entries.to_html(output_dir / "export.html")
    print(f"to_html(): Exported to {output_dir / 'export.html'}")

    # Markdown export
    log_entries.to_markdown(output_dir / "export.md")
    print(f"to_markdown(): Exported to {output_dir / 'export.md'}")

    # DataFrame export
    try:
        df = log_entries.to_dataframe()
        print(f"to_dataframe(): Created DataFrame with shape {df.shape}")
    except ImportError:
        print("to_dataframe(): pandas not installed")

    # ========================================
    # 8. REAL-TIME MONITORING
    # ========================================
    print("\n" + "=" * 70)
    print("8. REAL-TIME MONITORING - Watch Logs Grow")
    print("=" * 70)

    from logxy_log_parser.monitor import LogFile

    logfile = LogFile.open(log_path)
    print(f"LogFile.open(): Opened {log_path}")
    print(f"  entry_count: {logfile.entry_count}")
    print(f"  contains_error(): {logfile.contains_error()}")
    print(f"  find_first(level='error'): {logfile.find_first(level='error').message if logfile.find_first(level='error') else None}")

    # Get last N entries
    tail_entries = logfile.tail(3)
    print(f"tail(3): Last 3 entries retrieved")

    # ========================================
    # 9. TASK TREES
    # ========================================
    print("\n" + "=" * 70)
    print("9. TASK TREES - Hierarchical Visualization")
    print("=" * 70)

    from logxy_log_parser.tree import TaskTree

    tree = TaskTree.build(entries)
    print(f"TaskTree.build(): Built tree with {len(tree.nodes)} nodes")
    print(f"  Root tasks: {len(tree.roots)}")

    # Show tree structure
    if tree.roots:
        root = tree.roots[0]
        print(f"\nTree structure for {root.action_type}:")
        print(f"  Depth: {root.depth}")
        print(f"  Children: {len(root.children)}")
        for child in root.children:
            print(f"    - {child.action_type} ({child.level.value})")

    # ========================================
    # 10. GENERATE REPORTS
    # ========================================
    print("\n" + "=" * 70)
    print("10. GENERATE REPORTS - Summary Reports")
    print("=" * 70)

    # HTML report
    html_report = analyzer.generate_report("html")
    print(f"generate_report('html'): {len(html_report)} characters")

    # JSON report
    json_report = analyzer.generate_report("json")
    print(f"generate_report('json'): {len(json_report)} characters")

    # Text report
    text_report = analyzer.generate_report("text")
    print(f"generate_report('text'): {len(text_report)} characters")

    # Cleanup
    log_path.unlink()
    for export_file in output_dir.glob("*"):
        export_file.unlink()
    output_dir.rmdir()

    print("\n" + "=" * 70)
    print("COMPLETE FEATURE REFERENCE DEMONSTRATION FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    main()
