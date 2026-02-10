"""
Filtering Examples for logxy-log-parser.

This script demonstrates various filtering capabilities:
1. Filter by log level
2. Filter by message content
3. Chain multiple filters
4. Filter by time range
5. Filter by custom fields
6. Filter by action type
"""

from logxy_log_parser import LogParser, LogFilter


def example_filter_by_level():
    """Filter logs by severity level."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    print("=== Filter by Level ===")

    # Get only debug logs
    debug_logs = LogFilter(logs).debug()
    print(f"Debug logs: {len(debug_logs)}")

    # Get info logs
    info_logs = LogFilter(logs).info()
    print(f"Info logs: {len(info_logs)}")

    # Get warning logs
    warning_logs = LogFilter(logs).warning()
    print(f"Warning logs: {len(warning_logs)}")

    # Get error logs (includes critical)
    error_logs = LogFilter(logs).error()
    print(f"Error logs: {len(error_logs)}")

    # Get critical logs only
    critical_logs = LogFilter(logs).critical()
    print(f"Critical logs: {len(critical_logs)}")


def example_filter_by_message():
    """Filter logs by message content."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    print("\n=== Filter by Message ===")

    # Find logs containing 'database'
    db_logs = LogFilter(logs).by_message("database")
    print(f"Logs mentioning 'database': {len(db_logs)}")

    # Find logs containing 'payment'
    payment_logs = LogFilter(logs).by_message("payment")
    print(f"Logs mentioning 'payment': {len(payment_logs)}")

    # Use regex for pattern matching
    pattern_logs = LogFilter(logs).by_message(r"started|completed", regex=True)
    print(f"Logs matching pattern 'started|completed': {len(pattern_logs)}")


def example_filter_by_action_type():
    """Filter logs by action type."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("\n=== Filter by Action Type ===")

    # Find all database queries
    queries = LogFilter(logs).by_action_type("database:query")
    print(f"Database queries: {len(queries)}")

    # Find all database operations (multiple types)
    db_ops = LogFilter(logs).by_action_type("database:connect", "database:query", "database:load")
    print(f"Database operations: {len(db_ops)}")

    # Find ETL operations
    etl_ops = LogFilter(logs).by_action_type("etl:extract", "etl:transform", "etl:load")
    print(f"ETL operations: {len(etl_ops)}")


def example_filter_by_custom_field():
    """Filter logs by custom fields."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    print("\n=== Filter by Custom Field ===")

    # Find logs for specific user
    user_logs = LogFilter(logs).by_field("user_id", 12345)
    print(f"Logs for user_id=12345: {len(user_logs)}")

    # Find logs with specific request_id
    request_logs = LogFilter(logs).by_field("request_id", "req-001")
    print(f"Logs for request_id='req-001': {len(request_logs)}")

    # Find logs with specific payment_id
    payment_logs = LogFilter(logs).by_field("payment_id", "pay-123")
    print(f"Logs for payment_id='pay-123': {len(payment_logs)}")


def example_filter_by_field_contains():
    """Filter logs by field containing a value."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    print("\n=== Filter by Field Contains ===")

    # Find logs where request_id contains 'req'
    req_logs = LogFilter(logs).by_field_contains("request_id", "req")
    print(f"Logs with request_id containing 'req': {len(req_logs)}")


def example_filter_by_time_range():
    """Filter logs by time range."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    print("\n=== Filter by Time Range ===")

    # Convert timestamps to datetime
    from datetime import datetime

    start_ts = 1738332000.0
    end_ts = 1738332003.0

    # Filter by time range using timestamps
    recent_logs = LogFilter(logs).by_time_range(start_ts, end_ts)
    print(f"Logs between {start_ts} and {end_ts}: {len(recent_logs)}")

    # Filter using datetime objects
    start_dt = datetime.fromtimestamp(start_ts)
    end_dt = datetime.fromtimestamp(end_ts)
    dt_logs = LogFilter(logs).by_time_range(start_dt, end_dt)
    print(f"Logs between {start_dt} and {end_dt}: {len(dt_logs)}")


def example_filter_by_date():
    """Filter logs by specific date."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    print("\n=== Filter by Date ===")

    # Filter by date string (YYYY-MM-DD)
    date_logs = LogFilter(logs).by_date("2025-02-01")
    print(f"Logs on 2025-02-01: {len(date_logs)}")


def example_filter_after_before():
    """Filter logs after or before a timestamp."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    print("\n=== Filter After/Before ===")

    # Get logs after a timestamp
    after_logs = LogFilter(logs).after(1738332002.0)
    print(f"Logs after 1738332002.0: {len(after_logs)}")

    # Get logs before a timestamp
    before_logs = LogFilter(logs).before(1738332002.0)
    print(f"Logs before 1738332002.0: {len(before_logs)}")


def example_filter_by_task_uuid():
    """Filter logs by task UUID."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    print("\n=== Filter by Task UUID ===")

    # Filter by specific task UUID
    task_logs = LogFilter(logs).by_task_uuid("550e8400-e29b-41d4-a716-446655440000")
    print(f"Logs for task 550e8400-e29b-41d4-a716-446655440000: {len(task_logs)}")


def example_filter_by_nesting_level():
    """Filter logs by nesting depth."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("\n=== Filter by Nesting Level ===")

    # Get top-level actions (depth 1)
    top_level = LogFilter(logs).by_nesting_level(min_depth=1, max_depth=1)
    print(f"Top-level actions: {len(top_level)}")

    # Get nested actions (depth 2-3)
    nested = LogFilter(logs).by_nesting_level(min_depth=2, max_depth=3)
    print(f"Nested actions (depth 2-3): {len(nested)}")

    # Get deeply nested actions (depth 4+)
    deep = LogFilter(logs).by_nesting_level(min_depth=4, max_depth=99)
    print(f"Deeply nested actions (depth 4+): {len(deep)}")


def example_filter_by_duration():
    """Filter logs by duration."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("\n=== Filter by Duration ===")

    # Get actions that took more than 1 second
    slow_actions = LogFilter(logs).by_duration(min_duration=1.0)
    print(f"Actions > 1 second: {len(slow_actions)}")

    # Get actions that took less than 0.5 seconds
    fast_actions = LogFilter(logs).by_duration(max_duration=0.5)
    print(f"Actions < 0.5 seconds: {len(fast_actions)}")

    # Get actions between 0.5 and 2 seconds
    medium_actions = LogFilter(logs).by_duration(min_duration=0.5, max_duration=2.0)
    print(f"Actions 0.5-2 seconds: {len(medium_actions)}")


def example_filter_slow_fast_actions():
    """Filter slow and fast actions."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("\n=== Filter Slow/Fast Actions ===")

    # Get slow actions (> 1 second)
    slow = LogFilter(logs).slow_actions(threshold=1.0)
    print(f"Slow actions (>1s): {len(slow)}")
    for log in slow.limit(3):
        print(f"  - {log.message}: {log.duration}s")

    # Get fast actions (< 0.1 seconds)
    fast = LogFilter(logs).fast_actions(threshold=0.1)
    print(f"Fast actions (<0.1s): {len(fast)}")


def example_filter_by_status():
    """Filter logs by action status."""
    parser = LogParser("tests/fixtures/errors.log")
    logs = parser.parse()

    print("\n=== Filter by Status ===")

    # Get failed actions
    failed = LogFilter(logs).failed_actions()
    print(f"Failed actions: {len(failed)}")

    # Get succeeded actions
    succeeded = LogFilter(logs).succeeded_actions()
    print(f"Succeeded actions: {len(succeeded)}")

    # Get started actions
    started = LogFilter(logs).started_actions()
    print(f"Started actions: {len(started)}")


def example_filter_with_traceback():
    """Filter logs with traceback information."""
    parser = LogParser("tests/fixtures/errors.log")
    logs = parser.parse()

    print("\n=== Filter with Traceback ===")

    # Get logs with traceback
    traceback_logs = LogFilter(logs).with_traceback()
    print(f"Logs with traceback: {len(traceback_logs)}")
    for log in traceback_logs:
        print(f"  - {log.message}")


def example_chain_filters():
    """Chain multiple filters together."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("\n=== Chain Filters ===")

    # Chain: info level AND database query AND duration > 0.5s
    result = (
        LogFilter(logs)
        .info()
        .filter(lambda e: e.action_type == "database:query" and e.duration and e.duration > 0.5)
    )
    print(f"Info-level database queries > 0.5s: {len(result)}")

    # Chain: success level AND message contains 'completed'
    completed = (
        LogFilter(logs)
        .by_level("success")
        .filter(lambda e: e.message and "completed" in e.message.lower())
    )
    print(f"Success logs with 'completed': {len(completed)}")


def example_sort_and_limit():
    """Sort and limit results."""
    from logxy_log_parser import LogEntries

    parser = LogParser("tests/fixtures/complex.log")
    logs = LogEntries(parser.parse())

    print("\n=== Sort and Limit ===")

    # Sort by duration (slowest first)
    slowest = logs.sort(key="duration", reverse=True).limit(5)
    print("5 slowest actions:")
    for log in slowest:
        print(f"  - {log.message}: {log.duration}s")

    # Sort by timestamp (newest first)
    newest = logs.sort(key="timestamp", reverse=True).limit(3)
    print("\n3 newest logs:")
    for log in newest:
        print(f"  - {log.message}")


def example_unique_entries():
    """Get unique entries by a field."""
    from logxy_log_parser import LogEntries

    parser = LogParser("tests/fixtures/complex.log")
    logs = LogEntries(parser.parse())

    print("\n=== Unique Entries ===")

    # Get unique action types
    unique_types = logs.unique(key="action_type")
    print(f"Unique action types: {len(unique_types)}")

    # Get unique levels
    unique_levels = logs.unique(key="level")
    print(f"Unique levels: {len(unique_levels)}")


def example_count_by():
    """Count entries by field."""
    from logxy_log_parser import LogEntries

    parser = LogParser("tests/fixtures/sample.log")
    logs = LogEntries(parser.parse())

    print("\n=== Count By ===")

    # Count by level
    level_counts = logs.count_by_level()
    print("Count by level:")
    for level, count in level_counts.items():
        print(f"  {level}: {count}")

    # Count by message type
    type_counts = logs.count_by_type()
    print("\nCount by message type:")
    for msg_type, count in type_counts.items():
        print(f"  {msg_type}: {count}")


def example_group_by():
    """Group entries by a field."""
    from logxy_log_parser import LogEntries

    parser = LogParser("tests/fixtures/complex.log")
    logs = LogEntries(parser.parse())

    print("\n=== Group By ===")

    # Group by action type
    grouped = logs.group_by("action_type")
    print("Groups by action type:")
    for action_type, entries in grouped.items():
        print(f"  {action_type}: {len(entries)} entries")


def main():
    """Run all examples."""
    example_filter_by_level()
    example_filter_by_message()
    example_filter_by_action_type()
    example_filter_by_custom_field()
    example_filter_by_field_contains()
    example_filter_by_time_range()
    example_filter_by_date()
    example_filter_after_before()
    example_filter_by_task_uuid()
    example_filter_by_nesting_level()
    example_filter_by_duration()
    example_filter_slow_fast_actions()
    example_filter_by_status()
    example_filter_with_traceback()
    example_chain_filters()
    example_sort_and_limit()
    example_unique_entries()
    example_count_by()
    example_group_by()


if __name__ == "__main__":
    main()
