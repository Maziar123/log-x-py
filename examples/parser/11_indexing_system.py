#!/usr/bin/env python3
"""
11_indexing_system.py - Indexing System Feature

Demonstrates the Indexing System for fast lookups in large log files.

Features shown:
- LogIndex.build(): Build index for fast lookups
- find_by_task(): Find entries by task UUID
- find_by_level(): Find entries by log level
- find_by_time_range(): Find entries within time range
- IndexedLogParser: Query with index support
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Create sample log first
from logxpy import log, to_file, start_action


def create_sample_log() -> Path:
    """Create a sample log file with multiple entries."""
    log_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log")
    log_path = Path(log_file.name)

    if log_path.exists():
        log_path.unlink()
    with open(log_path, "w", encoding="utf-8") as f:
        to_file(f)

    # Generate multiple entries with different task IDs
    with start_action("task:process", task_id="task-001"):
        log.info("Processing user data", user_id=1)
        log.warning("High memory usage")
        log.success("Task completed")

    with start_action("task:process", task_id="task-002"):
        log.info("Processing order data", order_id=101)
        log.error("Payment failed", amount=99.99)

    with start_action("task:process", task_id="task-003"):
        log.info("Processing product data", product_id=201)
        log.debug("Fetching from database")
        log.success("Task completed")

    log.info("Application shutdown")

    return log_path


def main():
    """Demonstrate indexing system functionality."""
    from logxy_log_parser import LogIndex, IndexedLogParser

    # Create sample log
    log_path = create_sample_log()
    print(f"Created sample log: {log_path}")

    # ========================================
    # 1. BUILD INDEX
    # ========================================
    print("\n" + "=" * 60)
    print("1. BUILD INDEX - Fast Lookups for Large Logs")
    print("=" * 60)

    index = LogIndex.build(log_path)
    print(f"Index built: {len(index._entries)} entries indexed")

    # ========================================
    # 2. FIND BY TASK UUID
    # ========================================
    print("\n" + "=" * 60)
    print("2. FIND BY TASK - Locate All Entries for a Task")
    print("=" * 60)

    # Find all entries for task-001
    task_entries = index.find_by_task("task-001")
    print(f"Entries for task-001: {len(task_entries)}")
    for entry in task_entries:
        print(f"  - {entry.message_type}: {entry.message}")

    # ========================================
    # 3. FIND BY LEVEL
    # ========================================
    print("\n" + "=" * 60)
    print("3. FIND BY LEVEL - Filter by Log Level")
    print("=" * 60)

    # Find all error entries
    errors = index.find_by_level("error")
    print(f"Error entries: {len(errors)}")
    for entry in errors:
        print(f"  - {entry.message}: {entry.message}")

    # Find all warning entries
    warnings = index.find_by_level("warning")
    print(f"Warning entries: {len(warnings)}")
    for entry in warnings:
        print(f"  - {entry.message}")

    # ========================================
    # 4. FIND BY TIME RANGE
    # ========================================
    print("\n" + "=" * 60)
    print("4. FIND BY TIME RANGE - Time-Based Queries")
    print("=" * 60)

    # Get time range from index
    if index._entries:
        start_time = min(e.timestamp for e in index._entries)
        end_time = max(e.timestamp for e in index._entries)

        # Find entries in first half of time range
        mid_time = start_time + (end_time - start_time) / 2
        early_entries = index.find_by_time_range(start_time, mid_time)
        print(f"Entries in first half: {len(early_entries)}")

    # ========================================
    # 5. INDEXED PARSER - Query with Index
    # ========================================
    print("\n" + "=" * 60)
    print("5. INDEXED PARSER - Query with Index Support")
    print("=" * 60)

    parser = IndexedLogParser(log_path)

    # Query by task UUID
    task_results = parser.query(task_uuid="task-002")
    print(f"Query result for task-002: {len(task_results)} entries")
    for entry in task_results:
        print(f"  - [{entry.level.value}] {entry.message}")

    # Query by level
    debug_results = parser.query(level="debug")
    print(f"Query result for debug: {len(debug_results)} entries")

    # ========================================
    # 6. PERFORMANCE COMPARISON
    # ========================================
    print("\n" + "=" * 60)
    print("6. PERFORMANCE - Index vs Linear Scan")
    print("=" * 60)

    import time

    # Linear scan (for comparison)
    from logxy_log_parser import parse_log

    start = time.time()
    entries = parse_log(log_path)
    linear_result = [e for e in entries if e.task_uuid == "task-003"]
    linear_time = time.time() - start

    # Indexed lookup
    start = time.time()
    indexed_result = index.find_by_task("task-003")
    indexed_time = time.time() - start

    print(f"Linear scan: {len(entries)} entries in {linear_time*1000:.2f}ms")
    print(f"Indexed lookup: {len(indexed_result)} entries in {indexed_time*1000:.2f}ms")

    # Cleanup
    log_path.unlink()

    print("\n" + "=" * 60)
    print("Indexing system demonstration complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
