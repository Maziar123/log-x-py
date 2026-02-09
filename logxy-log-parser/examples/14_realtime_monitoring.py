#!/usr/bin/env python3
"""
14_realtime_monitoring.py - Real-Time Monitoring Feature

Demonstrates real-time monitoring capabilities:
- LogFile: Monitor logs as they grow
- watch(): Iterate new entries
- wait_for_message(): Wait for specific message
- wait_for_error(): Detect errors in real-time
"""
from __future__ import annotations

import tempfile
import threading
import time
from pathlib import Path

# Create sample log first
from logxpy import log, to_file, start_action


def create_sample_log() -> Path:
    """Create a new sample log file."""
    log_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log")
    log_path = Path(log_file.name)

    if log_path.exists():
        log_path.unlink()
    with open(log_path, "w", encoding="utf-8") as f:
        to_file(f)

    return log_path


def simulate_log_growth(log_path: Path, stop_event: threading.Event):
    """Simulate log growth in background thread."""
    # Small delay to let monitoring start
    time.sleep(0.1)

    with open(log_path, "a", encoding="utf-8") as f:
        to_file(f)

        # Initial entries
        log.info("Application started")
        log.debug("Loading configuration")

        time.sleep(0.1)

        # Progress messages
        for i in range(3):
            log.info(f"Processing step {i}", step=i)
            time.sleep(0.05)

        # Warning
        log.warning("High memory usage detected")
        time.sleep(0.1)

        # Error
        log.error("API timeout occurred", endpoint="/api/users")
        time.sleep(0.1)

        # Recovery
        log.success("Service recovered")
        log.info("Processing complete")

    stop_event.set()


def main():
    """Demonstrate real-time monitoring functionality."""
    from logxy_log_parser.monitor import LogFile

    # Create sample log path
    log_path = create_sample_log()
    print(f"Created log path: {log_path}")

    # ========================================
    # 1. LOGFILE - Open and Validate
    # ========================================
    print("\n" + "=" * 60)
    print("1. LOGFILE - Open and Validate Log")
    print("=" * 60)

    logfile = LogFile.open(log_path)
    print(f"Log file opened: {log_path}")
    print(f"Entry count: {logfile.entry_count}")

    # ========================================
    # 2. CONTAINS - Quick Presence Check
    # ========================================
    print("\n" + "=" * 60)
    print("2. CONTAINS - Check for Specific Entries")
    print("=" * 60)

    # Check for errors (before growth)
    has_error = logfile.contains(level="error")
    print(f"Contains error: {has_error}")

    # Check for specific message
    has_started = logfile.contains(message_type="info", message="Application started")
    print(f"Contains startup message: {has_started}")

    # ========================================
    # 3. WATCH - Monitor New Entries
    # ========================================
    print("\n" + "=" * 60)
    print("3. WATCH - Real-Time Entry Monitoring")
    print("=" * 60)

    # Start log growth simulation in background
    stop_event = threading.Event()
    growth_thread = threading.Thread(
        target=simulate_log_growth,
        args=(log_path, stop_event)
    )
    growth_thread.start()

    # Watch for new entries (with timeout)
    print("Watching for new entries...")
    entry_count = 0
    start_time = time.time()
    timeout = 5  # 5 seconds timeout

    for entry in logfile.watch():
        entry_count += 1
        print(f"  New entry: [{entry.level.value}] {entry.message}")

        # Check timeout
        if time.time() - start_time > timeout:
            print("  Watch timeout reached")
            break

        # Stop if background thread finished
        if stop_event.is_set() and entry_count > 10:
            time.sleep(0.1)  # Small buffer for final entries
            break

    print(f"Total entries watched: {entry_count}")

    # Wait for background thread
    growth_thread.join()

    # ========================================
    # 4. WAIT FOR MESSAGE
    # ========================================
    print("\n" + "=" * 60)
    print("4. WAIT FOR MESSAGE - Block Until Message Appears")
    print("=" * 60)

    # This would block until message appears (with demo timeout)
    try:
        result = logfile.wait_for_message("Processing complete", timeout=2)
        if result:
            print(f"Found message: {result.message}")
        else:
            print("Message not found (timeout)")
    except TimeoutError:
        print("Timeout waiting for message")

    # ========================================
    # 5. WAIT FOR ERROR
    # ========================================
    print("\n" + "=" * 60)
    print("5. WAIT FOR ERROR - Detect Errors in Real-Time")
    print("=" * 60)

    # Check if any errors exist
    has_errors = logfile.contains_error()
    print(f"Log contains errors: {has_errors}")

    if has_errors:
        # Find first error
        first_error = logfile.find_first(level="error")
        if first_error:
            print(f"First error: {first_error.message}")

        # Find all errors
        all_errors = logfile.find_all(level="error")
        print(f"Total errors: {len(all_errors)}")

    # ========================================
    # 6. TAIL - Get Last N Entries
    # ========================================
    print("\n" + "=" * 60)
    print("6. TAIL - Get Last N Entries")
    print("=" * 60)

    tail_entries = logfile.tail(5)
    print(f"Last 5 entries:")
    for entry in tail_entries:
        print(f"  [{entry.level.value}] {entry.message}")

    # Cleanup
    log_path.unlink()

    print("\n" + "=" * 60)
    print("Real-time monitoring demonstration complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
