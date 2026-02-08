#!/usr/bin/env python3
"""
Example 03: Error Handling
Create logs with errors and exceptions
"""

import sys
from pathlib import Path

# Add logxpy to path
sys.path.insert(0, str(Path(__file__).parent.parent / "logxpy"))

from logxpy import Message, start_action, to_file

# Setup logging to file
log_file = Path(__file__).parent / "example_03_errors.log"
to_file(open(log_file, "w"))

# Successful operation
with start_action(action_type="database:query", query="SELECT * FROM users"):
    Message.log(message_type="db:execute", rows=150)
    Message.log(message_type="db:success", duration_ms=45)

# Failed operation
try:
    with start_action(action_type="database:query", query="SELECT * FROM orders"):
        Message.log(message_type="db:execute")
        raise ConnectionError("Database connection lost")
except ConnectionError as e:
    Message.log(message_type="db:error", error=str(e), retry_recommended=True)

# Recovery attempt
with start_action(action_type="database:reconnect"):
    Message.log(message_type="db:connecting", host="localhost", port=5432)
    Message.log(message_type="db:connected", status="success")

print(f"✓ Log created: {log_file}")
print("\nView with: python view_tree.py example_03_errors.log")
