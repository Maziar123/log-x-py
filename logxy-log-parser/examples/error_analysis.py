"""
Error Analysis Examples for logxy-log-parser.

This script demonstrates error analysis capabilities:
1. Get error summary
2. Find error patterns
3. Calculate failure rates by action
4. Find most common errors
5. Find orphaned entries
"""

from logxy_log_parser import LogParser, LogFilter, LogAnalyzer


def example_error_summary():
    """Get a summary of all errors in the log."""
    parser = LogParser("tests/fixtures/errors.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("=== Error Summary ===")

    summary = analyzer.error_summary()
    print(f"Total error count: {summary.total_count}")
    print(f"Unique error types: {summary.unique_types}")
    print(f"Most common error: {summary.most_common[0]} ({summary.most_common[1]} occurrences)")

    print("\nErrors by level:")
    for level, count in summary.by_level.items():
        print(f"  {level}: {count}")

    print("\nErrors by action:")
    for action, count in summary.by_action.items():
        print(f"  {action}: {count}")


def example_error_patterns():
    """Find common error patterns."""
    parser = LogParser("tests/fixtures/errors.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Error Patterns ===")

    patterns = analyzer.error_patterns()
    print(f"Found {len(patterns)} error patterns:")
    for i, pattern in enumerate(patterns, 1):
        print(f"\n{i}. {pattern.message}")
        print(f"   Count: {pattern.count}")
        print(f"   First occurrence: {pattern.first_occurrence}")
        print(f"   Last occurrence: {pattern.last_occurrence}")


def example_failure_rate_by_action():
    """Calculate failure rates for each action type."""
    parser = LogParser("tests/fixtures/errors.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Failure Rate by Action ===")

    rates = analyzer.failure_rate_by_action()
    print("Failure rates:")
    for action, rate in sorted(rates.items(), key=lambda x: x[1], reverse=True):
        print(f"  {action}: {rate * 100:.1f}%")


def example_most_common_errors():
    """Find the most common error messages."""
    parser = LogParser("tests/fixtures/errors.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Most Common Errors ===")

    common = analyzer.most_common_errors(n=5)
    print(f"Top {len(common)} most common errors:")
    for i, (message, count) in enumerate(common, 1):
        print(f"  {i}. {message} ({count} occurrences)")


def example_orphans():
    """Find orphaned log entries (entries without parent/child relationships)."""
    parser = LogParser("tests/fixtures/errors.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Orphaned Entries ===")

    orphans = analyzer.orphans()
    print(f"Found {len(orphans)} orphaned entries:")
    for entry in orphans:
        print(f"  - {entry.message} (level: {entry.level.value})")


def example_filter_errors():
    """Filter logs to get only errors."""
    parser = LogParser("tests/fixtures/errors.log")
    logs = parser.parse()

    print("\n=== Filter Errors ===")

    # Get all error-level logs
    errors = LogFilter(logs).error()
    print(f"Error-level logs: {len(errors)}")

    # Get all critical-level logs
    critical = LogFilter(logs).critical()
    print(f"Critical-level logs: {len(critical)}")

    # Get all failed actions
    failed = LogFilter(logs).failed_actions()
    print(f"Failed actions: {len(failed)}")

    # Get logs with traceback
    with_traceback = LogFilter(logs).with_traceback()
    print(f"Logs with traceback: {len(with_traceback)}")


def example_error_details():
    """Get detailed information about errors."""
    parser = LogParser("tests/fixtures/errors.log")
    logs = parser.parse()

    print("\n=== Error Details ===")

    errors = LogFilter(logs).error()
    for entry in errors:
        print(f"\nMessage: {entry.message}")
        print(f"Level: {entry.level.value}")
        print(f"Status: {entry.action_status}")
        if entry.duration:
            print(f"Duration: {entry.duration}s")
        if entry.get("error_code"):
            print(f"Error Code: {entry.get('error_code')}")
        if entry.get("traceback"):
            print(f"Traceback: {entry.get('traceback')[:50]}...")


def example_combined_error_analysis():
    """Combine multiple error analysis methods."""
    parser = LogParser("tests/fixtures/errors.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Combined Error Analysis ===")

    # Get error summary
    summary = analyzer.error_summary()
    print(f"Total errors: {summary.total_count}")

    # Get most common errors
    common = analyzer.most_common_errors(n=3)
    print("\nMost common errors:")
    for message, count in common:
        print(f"  - {message}: {count}")

    # Get failure rates
    rates = analyzer.failure_rate_by_action()
    print("\nActions with highest failure rates:")
    for action, rate in sorted(rates.items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"  - {action}: {rate * 100:.1f}%")


def example_export_errors():
    """Export error logs to various formats."""
    parser = LogParser("tests/fixtures/errors.log")
    logs = parser.parse()

    print("\n=== Export Errors ===")

    errors = LogFilter(logs).error()

    # Export to JSON
    errors.to_json("errors.json")
    print("Exported errors to errors.json")

    # Export to CSV
    errors.to_csv("errors.csv")
    print("Exported errors to errors.csv")

    # Export to HTML
    errors.to_html("errors.html")
    print("Exported errors to errors.html")

    # Export to Markdown
    errors.to_markdown("errors.md")
    print("Exported errors to errors.md")


def main():
    """Run all examples."""
    example_error_summary()
    example_error_patterns()
    example_failure_rate_by_action()
    example_most_common_errors()
    example_orphans()
    example_filter_errors()
    example_error_details()
    example_combined_error_analysis()
    example_export_errors()


if __name__ == "__main__":
    main()
