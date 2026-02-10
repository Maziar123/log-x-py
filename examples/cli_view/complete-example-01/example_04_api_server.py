#!/usr/bin/env python3
"""Example 04: API Server Simulation - realistic multi-request logging."""

import time

from logxpy import log, start_action

# Server startup
with start_action(action_type="server:startup"):
    log.info("Server config", port=8080, environment="production")
    time.sleep(0.02)
    log.success("Server ready")

# Request 1: GET /api/users
with start_action(action_type="http:request", method="GET", path="/api/users", request_id="req_001"):
    log.info("Auth verify", user_id="user_123")
    time.sleep(0.03)

    with start_action(action_type="database:query"):
        log.info("Executing", query="SELECT * FROM users")
        time.sleep(0.05)
        log.success("Result", rows=25)

    log.success("Response", status=200, duration_ms=80)

# Request 2: POST /api/orders (successful)
with start_action(action_type="http:request", method="POST", path="/api/orders", request_id="req_002"):
    log.info("Auth verify", user_id="user_456")
    time.sleep(0.02)

    with start_action(action_type="payment:process"):
        log.info("Validate", amount=149.99)
        time.sleep(0.08)
        log.success("Payment captured", transaction_id="txn_abc")

    with start_action(action_type="inventory:reserve"):
        log.info("Check inventory", items=2)
        time.sleep(0.04)
        log.success("Reserved")

    log.success("Response", status=201, order_id="ORD-12345")

# Request 3: GET /api/users (failed auth)
try:
    with start_action(action_type="http:request", method="GET", path="/api/users", request_id="req_003"):
        log.info("Auth verify", token="invalid")
        raise ValueError("Invalid authentication token")
except ValueError:
    log.error("Unauthorized", status=401)

# Request 4: POST /api/orders (payment failed)
with start_action(action_type="http:request", method="POST", path="/api/orders", request_id="req_004"):
    log.info("Auth verify", user_id="user_789")
    time.sleep(0.02)

    try:
        with start_action(action_type="payment:process"):
            log.info("Validate", amount=299.99)
            time.sleep(0.06)
            raise TimeoutError("Payment gateway timeout")
    except TimeoutError as e:
        log.error("Payment error", error=str(e))
        log.error("Response", status=500, error="Payment processing failed")

# Server shutdown
with start_action(action_type="server:shutdown"):
    log.info("Closing connections")
    time.sleep(0.02)
    log.success("Server stopped")

print("✓ Log created: example_04_api_server.log")
