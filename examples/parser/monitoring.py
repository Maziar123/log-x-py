"""
LogFile Monitoring Examples

Examples for real-time log file monitoring and validation.
"""

from logxy_log_parser import LogFile, LogFilter
import time


# Example 1: Open and validate log file
def example_open_and_validate():
    """Safely open and validate a log file."""
    # Returns None if file doesn't exist or is invalid
    logfile = LogFile.open("tests/fixtures/sample.log")

    if logfile is None:
        print("File not found or invalid")
        return

    print(f"File: {logfile.path}")
    print(f"Valid LogXPy log: {logfile.is_valid}")
    print(f"Size: {logfile.size} bytes")
    print(f"Entries: {logfile.entry_count}")


# Example 2: Real-time entry count
def example_real_time_count():
    """Get entry count that updates as file grows."""
    logfile = LogFile("tests/fixtures/sample.log")

    print(f"Current entries: {logfile.entry_count}")

    # Simulate waiting for logs to be written
    time.sleep(5)

    # Refresh to get updated count
    new_count = logfile.refresh()
    print(f"Updated entries: {new_count}")


# Example 3: Check if log contains specific content
def example_contains_checks():
    """Check for specific log content without full parsing."""
    logfile = LogFile("tests/fixtures/sample.log")

    # Check for errors
    if logfile.contains_error():
        print("Log file contains errors!")

    # Check for specific message
    if logfile.contains_message("database connection"):
        print("Database connection issue found")

    # Check for specific log level
    if logfile.contains_level("critical"):
        print("Critical issues present!")

    # Check with custom criteria
    if logfile.contains(action_type="payment.process"):
        print("Payment processing logs found")

    if logfile.contains(user_id=12345):
        print("User 12345 activity found")

    # Substring search
    if logfile.contains(message__contains="timeout"):
        print("Timeout messages found")

    # Comparison searches
    if logfile.contains(timestamp__gt=1738332000):
        print("Logs after timestamp found")


# Example 4: Find specific entries
def example_find_entries():
    """Find specific log entries."""
    logfile = LogFile("tests/fixtures/sample.log")

    # Find first error
    first_error = logfile.find_first(level="error")
    if first_error:
        print(f"First error: {first_error.message}")

    # Find last entry for specific user
    last_user = logfile.find_last(user_id=12345)
    if last_user:
        print(f"Last activity: {last_user.message}")

    # Find all database query entries
    db_entries = logfile.find_all(action_type="database.query")
    print(f"Found {len(db_entries)} database queries")

    # Get last 10 entries (tail)
    recent = logfile.tail(10)
    for entry in recent:
        print(f"{entry.timestamp}: {entry.message}")


# Example 5: Real-time monitoring with watch()
def example_watch_monitoring():
    """Monitor file for new entries using iterator."""
    logfile = LogFile("app.log")

    print("Monitoring for errors...")
    try:
        for entry in logfile.watch(interval=0.5):
            if entry.level == "error":
                print(f"[{entry.timestamp}] {entry.message}")

                # Can break on condition
                if "critical" in entry.message.lower():
                    print("Critical error found, stopping!")
                    break
    except KeyboardInterrupt:
        print("\nStopped monitoring")


# Example 6: Real-time monitoring with follow()
def example_follow_monitoring():
    """Monitor file using callback function."""
    logfile = LogFile("app.log")

    def on_new_log(entry):
        if entry.level == "error":
            print(f"🔴 ERROR: {entry.message}")
        elif entry.level == "warning":
            print(f"🟡 WARNING: {entry.message}")
        else:
            print(f"📌 {entry.message}")

    # Monitor file - blocks until Ctrl+C
    try:
        logfile.follow(on_new_log, interval=0.5)
    except KeyboardInterrupt:
        print("\nStopped monitoring")


# Example 7: Wait for specific events
def example_wait_for_events():
    """Wait for specific log events to occur."""
    logfile = LogFile("app.log")

    # Wait for specific message
    entry = logfile.wait_for_message("Application started", timeout=30.0)
    if entry:
        print("Application has started!")
    else:
        print("Timeout waiting for start message")

    # Wait for any error
    error_entry = logfile.wait_for_error(timeout=60.0)
    if error_entry:
        print(f"Error detected: {error_entry.message}")

    # Wait for specific criteria
    entry = logfile.wait_for(
        action_type="payment.process",
        action_status="succeeded",
        timeout=120.0
    )
    if entry:
        print("Payment completed successfully!")


# Example 8: Integration with full parser
def example_parser_integration():
    """Use LogFile to validate, then full parser for analysis."""
    # Use LogFile to validate and monitor
    logfile = LogFile.open("app.log")

    if logfile is None or not logfile.is_valid:
        print("Invalid log file")
        return

    # Quick check if we need full parsing
    if not logfile.contains_error():
        print("No errors found, skipping detailed analysis")
        return

    # Get full parser for analysis
    parser = logfile.get_parser()
    logs = parser.parse()

    # Use all filtering capabilities
    errors = LogFilter(logs).by_level("error")
    print(f"Found {len(errors)} errors")

    # Export filtered results
    errors.to_html("errors.html")


# Example 9: Simple monitoring dashboard
def example_monitoring_dashboard():
    """Print a simple monitoring dashboard that updates."""
    from datetime import datetime

    def print_dashboard(logfile: LogFile):
        """Print a simple monitoring dashboard."""
        logfile.refresh()

        print(f"\n{'='*60}")
        print(f"Log Monitor: {logfile.path}")
        print(f"{'='*60}")
        print(f"Total Entries: {logfile.entry_count:,}")
        print(f"File Size: {logfile.size / 1024:.1f} KB")
        print(f"Has Errors: {logfile.contains_error()}")
        print(f"Has Warnings: {logfile.contains_level('warning')}")

        if logfile.entry_count > 0:
            last_entry = logfile.tail(1)[0]
            print(f"Last Entry: {last_entry.message}")

        print(f"{'='*60}\n")

    logfile = LogFile("app.log")

    # Update dashboard every 5 seconds
    try:
        while True:
            print_dashboard(logfile)
            time.sleep(5)
    except KeyboardInterrupt:
        print("Monitoring stopped")


# Example 10: Conditional alerting
def example_alerting():
    """Monitor and alert on specific conditions."""
    import sys

    logfile = LogFile("app.log")

    def alert_on_error(entry):
        """Send alert when error is detected."""
        print(f"\n🚨 ALERT: {entry.level.upper()} detected!")
        print(f"   Message: {entry.message}")
        print(f"   Timestamp: {entry.timestamp}")

        # Could send email, Slack message, etc.
        # send_alert(entry)

    # Monitor only for errors and critical
    print("Monitoring for errors and critical issues...")
    try:
        for entry in logfile.watch(interval=0.5):
            if entry.level in ("error", "critical"):
                alert_on_error(entry)

                # Exit on critical error
                if entry.level == "critical":
                    print("Critical error - exiting!")
                    sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopped monitoring")


if __name__ == "__main__":
    print("LogFile Monitoring Examples")
    print("=" * 50)
    print("\nNote: Update 'app.log' to point to your actual log file")
