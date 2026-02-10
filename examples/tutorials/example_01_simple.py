#!/usr/bin/env python3
"""Example 01: Simple Logging - Create and View"""

from pathlib import Path

from _setup_imports import log, to_file

log_file = Path(__file__).parent / "example_01_simple.log"
to_file(open(log_file, "w"))

print(f"Creating log: {log_file.name}")

# Simple logs
log.info("Application started", version="1.0.0")
log.info("User logged in", user_id=123, username="alice")
log.success("Data processed", records=100)
log.warning("Memory usage high", usage="85%")
log.error("Connection failed", host="db.example.com")

print(f"✓ Log created: {log_file}")
print(f"\nView with: python ../cli_view/complete-example-01/view_tree.py {log_file}")
