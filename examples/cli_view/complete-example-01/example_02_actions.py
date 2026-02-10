#!/usr/bin/env python3
"""Example 02: Actions (Nested Operations) - tree structure with start_action."""

import time

from logxpy import log, start_action

log.init()

# Simple action with nested children
with start_action(action_type="order:process", order_id="ORD-001"):
    log.info("Validating order", items=3, total=99.99)
    time.sleep(0.05)

    with start_action(action_type="payment:charge", amount=99.99):
        log.info("Calling gateway", gateway="stripe")
        time.sleep(0.08)
        log.success("Payment captured", transaction_id="txn_123")

    with start_action(action_type="shipping:prepare", carrier="FedEx"):
        log.info("Creating label", tracking="1Z999AA10123456784")
        time.sleep(0.06)

    log.success("Order complete", order_id="ORD-001")

# Another task with error
try:
    with start_action(action_type="order:process", order_id="ORD-002"):
        log.info("Validating order", items=0)
        raise ValueError("Order has no items")
except ValueError:
    log.error("Order validation failed", order_id="ORD-002")

print("✓ Log created: example_02_actions.log")
