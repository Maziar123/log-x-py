#!/usr/bin/env python3
"""
10_check_presence.py - Check Presence Feature

Demonstrates the Simple One-Line API - Check presence:
Verify if specific entries exist (single or multiple log lines).

Features shown:
- check_log(): Parse and validate log in one line
- contains(): Check if specific entries exist
- count_by(): Count occurrences by level/type
- Quick validation without full parsing
"""
from __future__ import annotations

import tempfile
from pathlib import Path

# Create sample log first
from logxpy import log, to_file, start_action


def create_sample_log() -> Path:
    """Create a sample log file for demonstration."""
    log_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log")
    log_path = Path(log_file.name)

    # Delete if exists from previous run
    if log_path.exists():
        log_path.unlink()
    with open(log_path, "w", encoding="utf-8") as f:
        to_file(f)

    # Generate sample log entries
    log.info("Application started")

    with start_action("database:query"):
        log.info("Querying users table")
        log.success("Query completed", rows=42)

    with start_action("api:request", endpoint="/api/users"):
        log.info("Processing request")
        log.error("User not found", user_id=999)

    log.warning("High memory usage", memory_percent=85)
    log.critical("Database connection lost")

    with start_action("database:reconnect"):
        log.info("Attempting reconnection")
        log.success("Reconnected")

    return log_path


def main():
    """Demonstrate check presence functionality."""
    from logxy_log_parser import check_log, parse_log, count_by, types
    from logxy_log_parser.filter import LogFilter

    # Create sample log
    log_path = create_sample_log()
    print(f"Created sample log: {log_path}")

    # ========================================
    # 1. CHECK PRESENCE - Single Line API
    # ========================================
    print("\n" + "=" * 60)
    print("1. CHECK PRESENSE - Simple One-Line API")
    print("=" * 60)

    # Quick check: Does the log contain errors?
    result = check_log(log_path)
    has_errors = result.contains(level="error")
    print(f"Has errors: {has_errors}")

    # Check for critical entries
    has_critical = result.contains(level="critical")
    print(f"Has critical: {has_critical}")

    # Check for specific action type
    has_db_queries = result.contains(action_type="database:query")
    print(f"Has database queries: {has_db_queries}")

    # ========================================
    # 2. TYPE & COUNT - Identify and Count
    # ========================================
    print("\n" + "=" * 60)
    print("2. TYPE & COUNT - Identify Entry Types")
    print("=" * 60)

    # Parse log for detailed analysis
    entries = parse_log(log_path)

    # Count by log level
    level_counts = count_by(entries, key="level")
    print(f"Entries by level: {level_counts}")

    # Count by action type
    action_counts = count_by(entries, key="action_type")
    print(f"Entries by action type: {action_counts}")

    # Get unique entry types
    entry_types = types(entries)
    print(f"Unique message types: {len(set(e.message_type for e in entries))}")

    # ========================================
    # 3. PYTHON-NATIVE - Standard Operations
    # ========================================
    print("\n" + "=" * 60)
    print("3. PYTHON-NATIVE - Standard Operations")
    print("=" * 60)

    # Use standard Python list operations
    error_entries = [e for e in entries if e.is_error]
    print(f"Error entries (list comprehension): {len(error_entries)}")

    # Use any() for presence check
    has_api_requests = any(e.action_type == "api:request" for e in entries)
    print(f"Has API requests: {has_api_requests}")

    # Use filter() with LogFilter
    f = LogFilter(entries)
    warnings = f.by_level("warning")
    print(f"Warning count: {len(warnings)}")

    # ========================================
    # 4. PRODUCTIVE - Rich Ready-to-Use
    # ========================================
    print("\n" + "=" * 60)
    print("4. PRODUCTIVE - Rich, Ready-to-Use")
    print("=" * 60)

    # Quick summary with minimal boilerplate
    from logxy_log_parser import LogAnalyzer

    analyzer = LogAnalyzer(entries)
    error_summary = analyzer.error_summary()

    print(f"Total entries: {len(entries)}")
    print(f"Total errors: {error_summary.total_count}")
    print(f"Unique error types: {error_summary.unique_types}")
    print(f"Most common error: {error_summary.most_common[0]}")

    # Check for specific field values
    has_user_999 = any(
        e.fields.get("user_id") == 999
        for e in entries
        if e.fields
    )
    print(f"Contains user_id=999: {has_user_999}")

    # ========================================
    # 5. ADVANCED PRESENCE CHECKS
    # ========================================
    print("\n" + "=" * 60)
    print("5. ADVANCED PRESENCE CHECKS")
    print("=" * 60)

    # Check for entries with specific field
    has_rows_field = any(
        "rows" in e.fields
        for e in entries
        if e.fields
    )
    print(f"Has 'rows' field: {has_rows_field}")

    # Check for duration threshold
    slow_entries = [
        e for e in entries
        if e.duration and e.duration > 0.001
    ]
    print(f"Slow entries (>1ms): {len(slow_entries)}")

    # Check for specific message content
    has_reconnect = any(
        e.message and "reconnect" in e.message.lower()
        for e in entries
    )
    print(f"Contains 'reconnect': {has_reconnect}")

    # Cleanup
    log_path.unlink()

    print("\n" + "=" * 60)
    print("Check presence demonstration complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
