"""
Basic usage examples for logxy-log-parser.

This script demonstrates:
1. Loading and parsing log files
2. Filtering logs by various criteria
3. Exporting filtered results
"""

from logxy_log_parser import LogParser, LogFilter, LogAnalyzer, TaskTree


# Example 1: Basic parsing
def example_basic_parsing():
    """Load a log file and parse all entries."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    print(f"Total log entries: {len(logs)}")

    # Print first entry
    if logs:
        print("\nFirst entry:")
        print(f"  Timestamp: {logs[0].timestamp}")
        print(f"  Level: {logs[0].level.value}")
        print(f"  Message: {logs[0].message}")


# Example 2: Filtering by log level
def example_filter_by_level():
    """Filter logs by severity level."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    # Get only errors
    errors = LogFilter(logs).error()
    print(f"Found {len(errors)} errors")

    # Get warnings
    warnings = LogFilter(logs).warning()
    print(f"Found {len(warnings)} warnings")


# Example 3: Filtering by message content
def example_filter_by_message():
    """Filter logs by message content."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    # Find logs containing 'database'
    db_logs = LogFilter(logs).by_message("database")
    print(f"Found {len(db_logs)} database-related logs")

    # Regex pattern matching
    api_logs = LogFilter(logs).by_message(r"payment", regex=True)
    print(f"Found {len(api_logs)} payment-related logs")


# Example 4: Chaining filters
def example_chaining_filters():
    """Chain multiple filters together."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    # Find database and payment actions
    db_payment = LogFilter(logs).by_action_type("database.query", "payment.charge")

    print(f"Found {len(db_payment)} database/payment actions")
    for entry in db_payment:
        print(f"  {entry.action_type}: {entry.message or entry.action_status}")


# Example 5: Time-based filtering
def example_time_filtering():
    """Filter logs by time range."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    # Get logs after a timestamp
    recent_logs = LogFilter(logs).after(1738332001.5)
    print(f"Logs after timestamp: {len(recent_logs)}")

    # Get logs before a timestamp
    early_logs = LogFilter(logs).before(1738332001.5)
    print(f"Logs before timestamp: {len(early_logs)}")


# Example 6: Performance analysis
def example_performance_analysis():
    """Analyze performance metrics from logs."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    analyzer = LogAnalyzer(logs)

    # Get slowest actions
    print("\n=== Slowest Actions ===")
    for action in analyzer.slowest_actions(5):
        print(f"  {action.action_type}: {action.mean_duration:.3f}s "
              f"(avg of {action.count} calls)")

    # Get duration statistics by action type
    print("\n=== Duration Statistics ===")
    for action_type, stats in analyzer.duration_by_action().items():
        print(f"  {action_type}:")
        print(f"    Count: {stats.count}")
        print(f"    Mean: {stats.mean:.4f}s")
        print(f"    Max:  {stats.max:.4f}s")
        print(f"    P95:  {stats.p95:.4f}s")


# Example 7: Error analysis
def example_error_analysis():
    """Analyze errors in logs."""
    parser = LogParser("tests/fixtures/errors.log")
    logs = parser.parse()

    analyzer = LogAnalyzer(logs)

    # Get error summary
    summary = analyzer.error_summary()
    print("\n=== Error Summary ===")
    print(f"Total errors: {summary.total_count}")
    print(f"Unique error types: {summary.unique_types}")
    print(f"Most common error: {summary.most_common[0]} ({summary.most_common[1]} occurrences)")

    # Find failed actions
    failed = LogFilter(logs).by_action_type("payment.charge", "payment.gateway")
    print("\n=== Failed Actions ===")
    for entry in failed:
        print(f"  {entry.action_type}: {entry.fields.get('error', 'unknown')}")


# Example 8: Export results
def example_export():
    """Export filtered logs to various formats."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    errors = LogFilter(logs).error()

    # Export to different formats
    errors.to_json("errors.json")
    errors.to_csv("errors.csv")
    errors.to_html("errors.html")
    errors.to_markdown("errors.md")

    print("Exported errors to: errors.json, errors.csv, errors.html, errors.md")

    # Export to DataFrame (requires pandas)
    try:
        df = errors.to_dataframe()
        print(f"\nDataFrame shape: {df.shape}")
        print(df.head())
    except ImportError:
        print("pandas not available for DataFrame export")


# Example 9: Task tracing
def example_task_tracing():
    """Trace a complete task by UUID."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    # Get a specific task UUID from your logs
    if not logs:
        print("No logs found")
        return

    task_uuid = logs[0].task_uuid

    # Get all logs for this task
    task_logs = LogFilter(logs).by_task_uuid(task_uuid)

    print(f"\n=== Task: {task_uuid} ===")
    print(f"Total entries: {len(task_logs)}")

    # Build task tree
    tree = TaskTree.from_entries(logs, task_uuid)

    print(f"Total duration: {tree.root.total_duration:.3f}s")
    print(f"Max nesting depth: {tree.deepest_nesting()}")

    # Visualize as tree
    print("\nTask Tree:")
    print(tree.visualize())


# Example 10: Using LogFile for monitoring
def example_logfile_usage():
    """Demonstrate LogFile usage."""
    from logxy_log_parser import LogFile

    logfile = LogFile("tests/fixtures/sample.log")

    print("\n=== Log File Info ===")
    print(f"File: {logfile.path}")
    print(f"Valid: {logfile.is_valid}")
    print(f"Size: {logfile.size} bytes")
    print(f"Entries: {logfile.entry_count}")

    # Check for errors
    if logfile.contains_error():
        print("\nFile contains errors!")
    else:
        print("\nNo errors found")

    # Get last 5 entries
    recent = logfile.tail(5)
    print("\nLast 5 entries:")
    for entry in recent:
        print(f"  {entry.message or entry.action_type}")


if __name__ == "__main__":
    # Run examples
    print("LogXPy Log Parser - Basic Usage Examples")
    print("=" * 50)

    example_basic_parsing()
    print("\n" + "-" * 50 + "\n")

    example_filter_by_level()
    print("\n" + "-" * 50 + "\n")

    example_filter_by_message()
    print("\n" + "-" * 50 + "\n")

    example_chaining_filters()
    print("\n" + "-" * 50 + "\n")

    example_time_filtering()
    print("\n" + "-" * 50 + "\n")

    example_performance_analysis()
    print("\n" + "-" * 50 + "\n")

    example_error_analysis()
    print("\n" + "-" * 50 + "\n")

    example_export()
    print("\n" + "-" * 50 + "\n")

    example_task_tracing()
    print("\n" + "-" * 50 + "\n")

    example_logfile_usage()
