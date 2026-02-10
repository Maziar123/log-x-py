#!/usr/bin/env python3
"""Example 03: Error Handling - logs with errors and exceptions."""

from logxpy import log, start_action

# Successful operation
with start_action(action_type="database:query", query="SELECT * FROM users"):
    log.info("Executing query", rows=150)
    log.success("Query complete", duration_ms=45)

# Failed operation
try:
    with start_action(action_type="database:query", query="SELECT * FROM orders"):
        log.info("Executing query")
        raise ConnectionError("Database connection lost")
except ConnectionError as e:
    log.error("Database error", error=str(e), retry_recommended=True)

# Recovery attempt
with start_action(action_type="database:reconnect"):
    log.info("Reconnecting", host="localhost", port=5432)
    log.success("Connected")

print("✓ Log created: example_03_errors.log")
