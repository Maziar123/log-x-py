"""Filtering examples for logxy-log-parser.

Demonstrates various filtering techniques using LogFilter.
"""

from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "logxpy"))

from logxpy import log, start_action, to_file
from logxy_log_parser import parse_log, LogFilter


def create_sample_log():
    """Create a sample log file with various log levels."""
    log_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
    log_path = Path(log_file.name)

    to_file(open(log_path, 'w'))

    # Info logs
    log("Server starting", port=8080)
    log("Database connected", host="localhost", port=5432)

    # Debug logs
    log.debug("Processing request", path="/api/users", method="GET")

    # Success action
    with start_action("http:get", endpoint="/api/users"):
        log("User data retrieved")

    # Warning
    log.warning("Slow query detected", duration_ms=2500)

    # Error
    log.error("Connection failed", host="api.external.com", error="timeout")

    # Critical
    log.critical("Database connection lost")

    # More actions
    with start_action("cache:set", key="user:123"):
        log("Cached user data")

    with start_action("http:post", endpoint="/api/login"):
        log("User login attempt")

    log("Server shutting down")

    return log_path


def main():
    log_path = create_sample_log()
    print(f"Created sample log: {log_path.name}\n")

    try:
        entries = parse_log(log_path)
        logs = LogFilter(entries)

        # Filter by level
        print("=== Filter by Level ===")
        errors = logs.error()
        warnings = logs.warning()
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")

        # Filter by action type
        print("\n=== Filter by Action Type ===")
        http_logs = logs.by_action_type("http:get", "http:post")
        print(f"HTTP actions: {len(http_logs)}")

        # Filter by message
        print("\n=== Filter by Message ===")
        db_logs = logs.by_message("database")
        print(f"Database-related: {len(db_logs)}")

        # Chain filters
        print("\n=== Chain Filters ===")
        result = LogFilter(entries).by_level("error", "critical").by_action_type("cache:set")
        print(f"Cache errors: {len(result)}")

        # Filter by duration
        print("\n=== Filter by Duration ===")
        slow = logs.slow_actions(threshold=0.001)
        print(f"Slow actions (>1ms): {len(slow)}")

        # Sort and limit
        print("\n=== Sort & Limit ===")
        sorted_logs = logs.sort("timestamp", reverse=True)
        recent = sorted_logs.limit(3)
        print(f"Last 3 entries:")
        for entry in recent:
            print(f"  {entry.message or entry.action_type}")

        # Export filtered results
        print("\n=== Export ===")
        errors.to_json("filtered_errors.json")
        errors.to_csv("filtered_errors.csv")
        print("Exported errors to filtered_errors.json and filtered_errors.csv")

    finally:
        log_path.unlink()
        Path("filtered_errors.json").unlink(missing_ok=True)
        Path("filtered_errors.csv").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
