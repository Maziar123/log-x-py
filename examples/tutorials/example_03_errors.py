#!/usr/bin/env python3
"""Example 03: Error Handling"""

from pathlib import Path

from _setup_imports import log, start_action, to_file

log_file = Path(__file__).parent / "example_03_errors.log"
to_file(open(log_file, "w"))

print(f"Creating log: {log_file.name}")

# Successful operation
with start_action(action_type="user:process", user_id=1):
    log.info("Processing user", name="Alice")
    log.success("User processed")

# Failed operation
try:
    with start_action(action_type="user:process", user_id=2):
        log.info("Processing user", name="Bob")
        log.warning("Missing email field")
        raise ValueError("Email required")
except ValueError:
    log.error("User processing failed", user_id=2)

# Another successful operation
with start_action(action_type="user:process", user_id=3):
    log.info("Processing user", name="Charlie")
    log.success("User processed")

print(f"✓ Log created: {log_file}")
print(f"\nView with: python ../cli_view/complete-example-01/view_tree.py {log_file}")
