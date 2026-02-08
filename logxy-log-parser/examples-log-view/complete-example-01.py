"""
LogXPy Log Parser - Complete Example
====================================

This example demonstrates all the features of logxy-log-parser
following the same structure as cross-lib1.html reference.

Each section shows:
1. Feature description
2. Code example
3. Expected output

Usage:
    python complete-example-01.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import logxy-log-parser
from logxy_log_parser import (
    LogParser,
    LogFilter,
    LogAnalyzer,
    LogFile,
    LogEntries,
    TaskTree,
    ActionStat,
    DurationStats,
    ErrorSummary,
)
from logxy_log_parser.types import Level, ActionStatus, TaskLevel


# ============================================================================
# 📨 SECTION 1: Basic Message Sending (Reading Logs)
# ============================================================================

def section_1_basic_reading():
    """Demonstrate basic log reading operations."""
    print("\n" + "=" * 60)
    print("📨 SECTION 1: Basic Log Reading")
    print("=" * 60)

    # Example 1.1: Parse log file
    print("\n1.1 Parse Log File")
    print("-" * 40)
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()
    print(f"Total entries: {len(logs)}")

    # Example 1.2: Get first entry
    print("\n1.2 First Entry")
    print("-" * 40)
    if logs:
        first = logs[0]
        print(f"Timestamp: {first.timestamp}")
        print(f"Level: {first.level.value}")
        print(f"Message: {first.message}")

    # Example 1.3: Stream parse (memory efficient)
    print("\n1.3 Stream Parse")
    print("-" * 40)
    count = 0
    for entry in parser.parse_stream():
        count += 1
    print(f"Streamed {count} entries")


# ============================================================================
# 🔍 SECTION 2: Filtering & Searching
# ============================================================================

def section_2_filtering():
    """Demonstrate filtering operations."""
    print("\n" + "=" * 60)
    print("🔍 SECTION 2: Filtering & Searching")
    print("=" * 60)

    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    # Example 2.1: Filter by level
    print("\n2.1 Filter by Level")
    print("-" * 40)
    info_logs = LogFilter(logs).info()
    print(f"Info entries: {len(info_logs)}")

    warning_logs = LogFilter(logs).warning()
    print(f"Warning entries: {len(warning_logs)}")

    error_logs = LogFilter(logs).error()
    print(f"Error entries: {len(error_logs)}")

    # Example 2.2: Filter by message content
    print("\n2.2 Filter by Message")
    print("-" * 40)
    db_logs = LogFilter(logs).by_message("database")
    print(f"Database-related: {len(db_logs)}")

    # Example 2.3: Filter by time range
    print("\n2.3 Filter by Time Range")
    print("-" * 40)
    recent = LogFilter(logs).after(1738332002.0)
    print(f"After timestamp: {len(recent)}")

    # Example 2.4: Filter by task UUID
    print("\n2.4 Filter by Task UUID")
    print("-" * 40)
    uuid = "550e8400-e29b-41d4-a716-446655440000"
    task_logs = LogFilter(logs).by_task_uuid(uuid)
    print(f"Task {uuid}: {len(task_logs)} entries")

    # Example 2.5: Filter by custom fields
    print("\n2.5 Filter by Custom Fields")
    print("-" * 40)
    user_logs = LogFilter(logs).by_field("user_id", 12345)
    print(f"User 12345 logs: {len(user_logs)}")

    # Example 2.6: Filter failed actions
    print("\n2.6 Filter Failed Actions")
    print("-" * 40)
    failed = LogFilter(logs).failed_actions()
    print(f"Failed actions: {len(failed)}")

    # Example 2.7: Filter by duration
    print("\n2.7 Filter by Duration")
    print("-" * 40)
    slow = LogFilter(logs).slow_actions(threshold=0.5)
    print(f"Slow actions (>0.5s): {len(slow)}")


# ============================================================================
# ⚠️ SECTION 3: Error Analysis
# ============================================================================

def section_3_error_analysis():
    """Demonstrate error analysis operations."""
    print("\n" + "=" * 60)
    print("⚠️ SECTION 3: Error Analysis")
    print("=" * 60)

    parser = LogParser("tests/fixtures/errors.log")
    logs = parser.parse()

    # Example 3.1: Get error summary
    print("\n3.1 Error Summary")
    print("-" * 40)
    analyzer = LogAnalyzer(logs)
    summary = analyzer.error_summary()
    print(f"Total errors: {summary.total_count}")
    print(f"Unique error types: {summary.unique_types}")
    print(f"Most common: {summary.most_common[0]} ({summary.most_common[1]}x)")

    # Example 3.2: Error patterns
    print("\n3.2 Error Patterns")
    print("-" * 40)
    patterns = analyzer.error_patterns()
    for pattern in patterns[:3]:
        print(f"  {pattern.error_type}: {pattern.count}x")
        if pattern.example_message:
            print(f"    Example: {pattern.example_message[:50]}...")

    # Example 3.3: Most common errors
    print("\n3.3 Most Common Errors")
    print("-" * 40)
    common = analyzer.most_common_errors(5)
    for msg, count in common:
        print(f"  {count}x: {msg[:50]}...")

    # Example 3.4: Failure rate by action
    print("\n3.4 Failure Rate by Action")
    print("-" * 40)
    rates = analyzer.failure_rate_by_action()
    for action, rate in rates.items():
        print(f"  {action}: {rate*100:.1f}% failure")


# ============================================================================
# 💻 SECTION 4: Performance & Duration Analysis
# ============================================================================

def section_4_performance():
    """Demonstrate performance analysis operations."""
    print("\n" + "=" * 60)
    print("💻 SECTION 4: Performance Analysis")
    print("=" * 60)

    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    # Example 4.1: Slowest actions
    print("\n4.1 Slowest Actions")
    print("-" * 40)
    analyzer = LogAnalyzer(logs)
    slowest = analyzer.slowest_actions(5)
    for action in slowest:
        print(f"  {action.action_type}: {action.mean_duration:.3f}s avg ({action.count} calls)")

    # Example 4.2: Duration statistics by action
    print("\n4.2 Duration Statistics")
    print("-" * 40)
    durations = analyzer.duration_by_action()
    for action_type, stats in durations.items():
        print(f"\n  {action_type}:")
        print(f"    Count: {stats.count}")
        print(f"    Mean:  {stats.mean:.4f}s")
        print(f"    Max:   {stats.max:.4f}s")
        print(f"    P95:   {stats.p95:.4f}s")

    # Example 4.3: Fastest actions
    print("\n4.3 Fastest Actions")
    print("-" * 40)
    fastest = analyzer.fastest_actions(5)
    for action in fastest:
        print(f"  {action.action_type}: {action.mean_duration:.3f}s")


# ============================================================================
# 📁 SECTION 5: LogFile - Real-time Monitoring
# ============================================================================

def section_5_logfile_monitoring():
    """Demonstrate LogFile monitoring operations."""
    print("\n" + "=" * 60)
    print("📁 SECTION 5: LogFile - Real-time Monitoring")
    print("=" * 60)

    # Example 5.1: Open and validate
    print("\n5.1 Open and Validate")
    print("-" * 40)
    logfile = LogFile.open("tests/fixtures/sample.log")
    if logfile:
        print(f"File: {logfile.path}")
        print(f"Valid: {logfile.is_valid}")
        print(f"Size: {logfile.size} bytes")
        print(f"Entries: {logfile.entry_count}")

    # Example 5.2: Contains checks
    print("\n5.2 Contains Checks")
    print("-" * 40)
    print(f"Contains error: {logfile.contains_error()}")
    print(f"Contains warning: {logfile.contains_level('warning')}")
    print(f"Contains 'started': {logfile.contains_message('started')}")

    # Example 5.3: Contains with criteria
    print("\n5.3 Contains with Criteria")
    print("-" * 40)
    print(f"Has user_id=12345: {logfile.contains(user_id=12345)}")
    print(f"Has timestamp>1738332002: {logfile.contains(timestamp__gt=1738332002)}")

    # Example 5.4: Find entries
    print("\n5.4 Find Entries")
    print("-" * 40)
    first_error = logfile.find_first(level="error")
    if first_error:
        print(f"First error: {first_error.message}")

    last_user = logfile.find_last(user_id=12345)
    if last_user:
        print(f"Last user 12345 activity: {last_user.message}")

    # Example 5.5: Tail (last n entries)
    print("\n5.5 Tail (Last 3 Entries)")
    print("-" * 40)
    recent = logfile.tail(3)
    for entry in recent:
        print(f"  {entry.timestamp}: {entry.message or entry.action_type}")

    # Example 5.6: Find all matching
    print("\n5.6 Find All Matching")
    print("-" * 40)
    warnings = logfile.find_all(level="warning")
    print(f"All warnings: {len(warnings)}")


# ============================================================================
# 📊 SECTION 6: Export Operations
# ============================================================================

def section_6_export():
    """Demonstrate export operations."""
    print("\n" + "=" * 60)
    print("📊 SECTION 6: Export Operations")
    print("=" * 60)

    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    # Example 6.1: Export to JSON
    print("\n6.1 Export to JSON")
    print("-" * 40)
    LogFilter(logs).to_json("/tmp/output.json")
    print("Exported to: /tmp/output.json")

    # Example 6.2: Export to CSV
    print("\n6.2 Export to CSV")
    print("-" * 40)
    LogFilter(logs).to_csv("/tmp/output.csv")
    print("Exported to: /tmp/output.csv")

    # Example 6.3: Export to HTML
    print("\n6.3 Export to HTML")
    print("-" * 40)
    LogFilter(logs).to_html("/tmp/output.html")
    print("Exported to: /tmp/output.html")

    # Example 6.4: Export to Markdown
    print("\n6.4 Export to Markdown")
    print("-" * 40)
    LogFilter(logs).to_markdown("/tmp/output.md")
    print("Exported to: /tmp/output.md")

    # Example 6.5: Export to DataFrame (if pandas available)
    print("\n6.5 Export to DataFrame")
    print("-" * 40)
    try:
        df = LogFilter(logs).to_dataframe()
        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns[:5])}...")
    except ImportError:
        print("pandas not available")


# ============================================================================
# 🔧 SECTION 7: Task Tree & Hierarchical Analysis
# ============================================================================

def section_7_task_tree():
    """Demonstrate task tree operations."""
    print("\n" + "=" * 60)
    print("🔧 SECTION 7: Task Tree & Hierarchical Analysis")
    print("=" * 60)

    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    if logs:
        # Example 7.1: Build task tree
        print("\n7.1 Build Task Tree")
        print("-" * 40)
        task_uuid = logs[0].task_uuid
        tree = TaskTree.from_entries(logs, task_uuid)
        print(f"Task UUID: {task_uuid}")
        print(f"Total duration: {tree.root.total_duration:.3f}s")
        print(f"Max depth: {tree.deepest_nesting()}")

        # Example 7.2: Visualize tree
        print("\n7.2 Tree Visualization")
        print("-" * 40)
        print(tree.visualize())

        # Example 7.3: Tree statistics
        print("\n7.3 Tree Statistics")
        print("-" * 40)
        stats = tree.get_stats()
        print(f"Total nodes: {stats['total_nodes']}")
        print(f"Completed: {stats['completed']}")
        print(f"Failed: {stats['failed']}")

        # Example 7.4: Execution path
        print("\n7.4 Execution Path")
        print("-" * 40)
        path = tree.get_execution_path()
        print("Path: " + " -> ".join(path))


# ============================================================================
# 🎯 SECTION 8: Aggregation & Grouping
# ============================================================================

def section_8_aggregation():
    """Demonstrate aggregation operations."""
    print("\n" + "=" * 60)
    print("🎯 SECTION 8: Aggregation & Grouping")
    print("=" * 60)

    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    # Example 8.1: Count by level
    print("\n8.1 Count by Level")
    print("-" * 40)
    level_counts = LogFilter(logs).count_by_level()
    for level, count in sorted(level_counts.items()):
        print(f"  {level}: {count}")

    # Example 8.2: Count by type
    print("\n8.2 Count by Action Type")
    print("-" * 40)
    type_counts = LogFilter(logs).count_by_type()
    for action_type, count in sorted(type_counts.items()):
        print(f"  {action_type}: {count}")

    # Example 8.3: Group by field
    print("\n8.3 Group by Task UUID")
    print("-" * 40)
    grouped = LogFilter(logs).group_by("task_uuid")
    for uuid, entries in grouped.items():
        print(f"  {uuid}: {len(entries)} entries")

    # Example 8.4: Widest tasks
    print("\n8.4 Widest Tasks")
    print("-" * 40)
    analyzer = LogAnalyzer(logs)
    widest = analyzer.widest_tasks()[:3]
    for uuid, count in widest:
        print(f"  {uuid}: {count} entries")


# ============================================================================
# 🚩 SECTION 9: LogEntries Collection Operations
# ============================================================================

def section_9_collection_ops():
    """Demonstrate LogEntries collection operations."""
    print("\n" + "=" * 60)
    print("🚩 SECTION 9: LogEntries Collection Operations")
    print("=" * 60)

    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    # Example 9.1: Sort entries
    print("\n9.1 Sort Entries")
    print("-" * 40)
    from logxy_log_parser import LogEntries

    entries = LogEntries(logs)
    sorted_desc = entries.sort("timestamp", reverse=True)
    print(f"Sorted (newest first): {sorted_desc[0].timestamp:.3f}")

    # Example 9.2: Limit entries
    print("\n9.2 Limit Entries")
    print("-" * 40)
    limited = entries.limit(3)
    print(f"Limited to 3: {len(limited)} entries")

    # Example 9.3: Unique entries
    print("\n9.3 Unique Entries")
    print("-" * 40)
    unique = entries.unique("task_uuid")
    print(f"Unique task UUIDs: {len(unique)}")

    # Example 9.4: Custom filter
    print("\n9.4 Custom Filter")
    print("-" * 40)
    long_messages = entries.filter(lambda e: e.message and len(e.message) > 20)
    print(f"Long messages: {len(long_messages)}")


# ============================================================================
# 📄 SECTION 10: Report Generation
# ============================================================================

def section_10_reports():
    """Demonstrate report generation."""
    print("\n" + "=" * 60)
    print("📄 SECTION 10: Report Generation")
    print("=" * 60)

    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    # Example 10.1: Text report
    print("\n10.1 Text Report")
    print("-" * 40)
    text_report = analyzer.generate_report("text")
    print(text_report[:300] + "...")

    # Example 10.2: JSON report
    print("\n10.2 JSON Report")
    print("-" * 40)
    import json

    json_report = analyzer.generate_report("json")
    data = json.loads(json_report)
    print(f"Total entries: {data['total_entries']}")

    # Example 10.3: HTML report
    print("\n10.3 HTML Report")
    print("-" * 40)
    html_report = analyzer.generate_report("html")
    analyzer.generate_report("html")
    with open("/tmp/report.html", "w") as f:
        f.write(html_report)
    print("HTML report saved to: /tmp/report.html")


# ============================================================================
# 🚀 SECTION 11: Advanced Features
# ============================================================================

def section_11_advanced():
    """Demonstrate advanced features."""
    print("\n" + "=" * 60)
    print("🚀 SECTION 11: Advanced Features")
    print("=" * 60)

    # Example 11.1: Timeline analysis
    print("\n11.1 Timeline Analysis")
    print("-" * 40)
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    timeline = analyzer.timeline(interval="1min")
    print(f"Time intervals: {len(timeline.intervals)}")

    # Example 11.2: Peak periods
    print("\n11.2 Peak Periods")
    print("-" * 40)
    peaks = analyzer.peak_periods(3)
    for period in peaks:
        print(f"  {period.start:.0f} - {period.end:.0f}: {period.entry_count} entries")

    # Example 11.3: Orphans detection
    print("\n11.3 Orphans (Unmatched Actions)")
    print("-" * 40)
    orphans = analyzer.orphans()
    print(f"Orphaned entries: {len(orphans)}")

    # Example 11.4: Deepest nesting
    print("\n11.4 Deepest Nesting")
    print("-" * 40)
    deepest = analyzer.deepest_nesting()
    print(f"Maximum depth: {deepest}")


# ============================================================================
# MAIN: Run All Examples
# ============================================================================

def main():
    """Run all example sections."""
    print("\n" + "#" * 60)
    print("# LogXPy Log Parser - Complete Example")
    print("#" * 60)

    # Check if sample log files exist
    sample_path = Path("tests/fixtures/sample.log")
    if not sample_path.exists():
        print("\n⚠️  Sample log files not found!")
        print("Please run from the logxy-log-parser directory.")
        return 1

    try:
        section_1_basic_reading()
        section_2_filtering()
        section_3_error_analysis()
        section_4_performance()
        section_5_logfile_monitoring()
        section_6_export()
        section_7_task_tree()
        section_8_aggregation()
        section_9_collection_ops()
        section_10_reports()
        section_11_advanced()

        print("\n" + "#" * 60)
        print("# All examples completed successfully!")
        print("#" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
