#!/usr/bin/env python3
"""
Example 02: Actions (Nested Operations)
Create logs with actions and view the tree structure
"""

import sys
import time
from pathlib import Path

# Add logxpy to path
sys.path.insert(0, str(Path(__file__).parent.parent / "logxpy"))

from logxpy import Message, start_action, to_file

# Setup logging to file (delete old log first)
log_file = Path(__file__).parent / "example_02_actions.log"
if log_file.exists():
    log_file.unlink()
with open(log_file, "w", encoding="utf-8") as f:
    to_file(f)

# Simple action
with start_action(action_type="order:process", order_id="ORD-001"):
    Message.log(message_type="order:validate", items=3, total=99.99)
    time.sleep(0.05)

    # Nested action: payment
    with start_action(action_type="payment:charge", amount=99.99):
        Message.log(message_type="payment:gateway", gateway="stripe")
        time.sleep(0.08)
        Message.log(message_type="payment:success", transaction_id="txn_123")

    # Nested action: shipping
    with start_action(action_type="shipping:prepare", carrier="FedEx"):
        Message.log(message_type="shipping:label", tracking="1Z999AA10123456784")
        time.sleep(0.06)

    Message.log(message_type="order:complete", order_id="ORD-001")

# Another task with error
try:
    with start_action(action_type="order:process", order_id="ORD-002"):
        Message.log(message_type="order:validate", items=0)
        raise ValueError("Order has no items")
except ValueError:
    Message.log(message_type="order:error", error="Order validation failed", order_id="ORD-002")

print(f"✓ Log created: {log_file}")
print("\nView with: python view_tree.py example_02_actions.log")
