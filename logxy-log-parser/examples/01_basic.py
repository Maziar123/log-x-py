"""Basic usage example for logxy-log-parser.

This script demonstrates:
1. Creating a sample log file using logxpy
2. Parsing the log with the simple one-line API
3. Using CheckResult for presence checks
4. Using helper functions for counting and grouping
"""

from pathlib import Path
import tempfile

# Import logxpy for creating logs
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "logxpy"))

from logxpy import log, start_action, to_file
from logxy_log_parser import parse_log, check_log, count_by, group_by


def create_sample_log():
    """Create a sample log file for testing."""
    log_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
    log_path = Path(log_file.name)

    # Initialize logxpy to write to our file
    to_file(open(log_path, 'w'))

    # Create sample log entries
    log("Application starting")

    with start_action("http:request", url="/api/users"):
        log("Fetching users")

    with start_action("db:query", query="SELECT * FROM users"):
        log("Querying database")

    with start_action("cache:get", key="users:all"):
        log("Checking cache")

    with start_action("http:request", url="/api/products"):
        log("Fetching products")

    with start_action("db:query", query="SELECT * FROM products"):
        log("Querying database")

    log.warning("High memory usage detected", usage_mb=512)

    with start_action("http:request", url="/api/orders"):
        log("Fetching orders")

    with start_action("db:query", query="SELECT * FROM orders"):
        log("Querying database")

    with start_action("payment:charge", amount=99.99):
        log.error("Payment failed", error="insufficient_funds", code="CARD_DECLINED")

    log("Application shutdown")

    return log_path


def main():
    # Create sample log
    log_path = create_sample_log()
    print(f"Created sample log: {log_path.name}\n")

    try:
        # 1. Parse with one-line API
        print("=== 1. Parse Log ===")
        entries = parse_log(log_path)
        print(f"Total entries: {len(entries)}")

        # 2. Check with presence checks
        print("\n=== 2. Check Presence ===")
        result = check_log(log_path)
        print(f"Has errors: {result.has_error}")
        print(f"Has warnings: {result.has_level('warning')}")
        print(f"Contains database queries: {result.contains(action_type='db:query')}")

        # 3. Count by criteria
        print("\n=== 3. Count By ===")
        errors = count_by(entries, level='error')
        print(f"Errors: {errors}")
        warnings = count_by(entries, level='warning')
        print(f"Warnings: {warnings}")

        # 4. Group by action type
        print("\n=== 4. Group By ===")
        by_action = group_by(entries, 'action_type')
        for action, items in sorted(by_action.items()):
            print(f"  {action}: {len(items)} entries")

        # 5. Filter with LogFilter
        print("\n=== 5. Filter ===")
        from logxy_log_parser import LogFilter

        logs = parse_log(log_path)
        filtered = LogFilter(logs).by_action_type('db:query')
        print(f"Database queries: {len(filtered)}")
        for entry in filtered:
            print(f"  {entry.message}")

        # 6. Analyze with LogAnalyzer
        print("\n=== 6. Analyze ===")
        from logxy_log_parser import LogAnalyzer

        analyzer = LogAnalyzer(logs)
        for stat in analyzer.slowest_actions(3):
            print(f"  {stat.action_type}: {stat.mean_duration*1000:.2f}ms")

    finally:
        # Clean up
        log_path.unlink()


if __name__ == "__main__":
    main()
