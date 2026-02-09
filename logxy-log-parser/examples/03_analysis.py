"""Analysis examples for logxy-log-parser.

Demonstrates performance analysis, error tracking, and statistics.
"""

from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "logxpy"))

from logxpy import log, start_action, to_file
from logxy_log_parser import parse_log, LogAnalyzer, analyze_log


def create_sample_log():
    """Create a sample log with performance data."""
    log_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
    log_path = Path(log_file.name)

    to_file(open(log_path, 'w'))

    # Simulate a web request with various operations
    with start_action("http:request", endpoint="/api/products"):
        log("Received request")

        with start_action("auth:validate", token="abc123"):
            log("Token validated")

        with start_action("db:query", query="SELECT * FROM products"):
            log("Retrieved products")

        with start_action("cache:set", key="products:all"):
            log("Cached products")

        log.info("Returning 200 OK", status_code=200)

    # Fast action
    with start_action("cache:get", key="products:all"):
        log("Cache hit")

    # Slow database query
    import time
    with start_action("db:query", query="SELECT * FROM orders WHERE status='pending'"):
        log("Retrieving pending orders")
        time.sleep(0.001)  # Simulate slow query

    # Error case
    with start_action("payment:charge", amount=199.99):
        log.error("Payment declined", card_last_4="1234", reason="insufficient_funds")

    # Another slow action
    with start_action("api:call", service="inventory"):
        log("Checking stock levels")
        time.sleep(0.002)

    # Multiple successful actions
    for i in range(3):
        with start_action("db:query", query=f"SELECT * FROM users LIMIT 10 OFFSET {i*10}"):
            log(f"Retrieved users page {i+1}")

    return log_path


def main():
    log_path = create_sample_log()
    print(f"Created sample log: {log_path.name}\n")

    try:
        # Method 1: Using analyze_log (one-line comprehensive analysis)
        print("=== One-Line Analysis ===")
        report = analyze_log(log_path)
        report.print_summary()

        # Method 2: Using LogAnalyzer for detailed analysis
        print("\n\n=== Detailed Analysis ===")
        entries = parse_log(log_path)
        analyzer = LogAnalyzer(entries)

        # Slowest actions
        print("\nSlowest Actions:")
        for stat in analyzer.slowest_actions(5):
            print(f"  {stat.action_type}: {stat.mean_duration*1000:.2f}ms")

        # Error summary
        print("\nError Summary:")
        summary = analyzer.error_summary()
        print(f"  Total: {summary.total_count}")
        print(f"  Most common: {summary.most_common[0]}")

        # Duration statistics
        print("\nDuration Statistics:")
        for action, stats in analyzer.duration_by_action().items():
            print(f"  {action}:")
            print(f"    Count: {stats.count}")
            print(f"    Mean: {stats.mean*1000:.2f}ms")
            print(f"    P95:  {stats.p95*1000:.2f}ms")

        # Task tracing
        print("\nTask Tracing:")
        from logxy_log_parser import TaskTree

        if entries:
            task_uuid = entries[0].task_uuid
            task_logs = [e for e in entries if e.task_uuid == task_uuid]
            if task_logs:
                tree = TaskTree.from_entries(entries, task_uuid)
                print(f"  Task: {task_uuid}")
                print(f"  Total duration: {tree.root.total_duration:.3f}s")
                print(f"  Max depth: {tree.deepest_nesting()}")

    finally:
        log_path.unlink()


if __name__ == "__main__":
    main()
