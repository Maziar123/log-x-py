#!/usr/bin/env python3
"""Example 02: Actions and Nested Operations"""

import time
from pathlib import Path

from _setup_imports import log, start_action, to_file

log_file = Path(__file__).parent / "example_02_actions.log"
to_file(open(log_file, "w"))

print(f"Creating log: {log_file.name}")

# Action with nested operations
with start_action(action_type="order:process", order_id="ORD-12345"):
    log.info("Order received", amount=99.99)

    with start_action(action_type="payment:charge"):
        log.info("Charging card", last_four="4242")
        time.sleep(0.1)
        log.success("Payment successful", transaction_id="txn_abc123")

    with start_action(action_type="inventory:reserve"):
        log.info("Checking inventory")
        time.sleep(0.05)
        log.success("Items reserved", count=3)

    log.success("Order completed")

print(f"✓ Log created: {log_file}")
print(f"\nView with: python ../examples-log-view/view_tree.py {log_file}")
