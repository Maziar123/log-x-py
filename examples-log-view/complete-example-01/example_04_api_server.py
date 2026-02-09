#!/usr/bin/env python3
"""
Example 04: API Server Simulation
Realistic API server with multiple requests
"""

import sys
import time
from pathlib import Path

# Add logxpy to path
sys.path.insert(0, str(Path(__file__).parent.parent / "logxpy"))

from logxpy import Message, start_action, to_file

# Setup logging to file (delete old log first)
log_file = Path(__file__).parent / "example_04_api_server.log"
if log_file.exists():
    log_file.unlink()
with open(log_file, "w", encoding="utf-8") as f:
    to_file(f)

# Server startup
with start_action(action_type="server:startup"):
    Message.log(message_type="server:config", port=8080, environment="production")
    time.sleep(0.02)
    Message.log(message_type="server:ready")

# Request 1: GET /api/users
with start_action(action_type="http:request", method="GET", path="/api/users", request_id="req_001"):
    Message.log(message_type="auth:verify", user_id="user_123")
    time.sleep(0.03)

    with start_action(action_type="database:query"):
        Message.log(message_type="db:execute", query="SELECT * FROM users")
        time.sleep(0.05)
        Message.log(message_type="db:result", rows=25)

    Message.log(message_type="http:response", status=200, duration_ms=80)

# Request 2: POST /api/orders (successful)
with start_action(action_type="http:request", method="POST", path="/api/orders", request_id="req_002"):
    Message.log(message_type="auth:verify", user_id="user_456")
    time.sleep(0.02)

    with start_action(action_type="payment:process"):
        Message.log(message_type="payment:validate", amount=149.99)
        time.sleep(0.08)
        Message.log(message_type="payment:success", transaction_id="txn_abc")

    with start_action(action_type="inventory:reserve"):
        Message.log(message_type="inventory:check", items=2)
        time.sleep(0.04)
        Message.log(message_type="inventory:reserved")

    Message.log(message_type="http:response", status=201, order_id="ORD-12345")

# Request 3: GET /api/users (failed auth)
try:
    with start_action(action_type="http:request", method="GET", path="/api/users", request_id="req_003"):
        Message.log(message_type="auth:verify", token="invalid")
        raise ValueError("Invalid authentication token")
except ValueError:
    Message.log(message_type="http:response", status=401, error="Unauthorized")

# Request 4: POST /api/orders (payment failed)
with start_action(action_type="http:request", method="POST", path="/api/orders", request_id="req_004"):
    Message.log(message_type="auth:verify", user_id="user_789")
    time.sleep(0.02)

    try:
        with start_action(action_type="payment:process"):
            Message.log(message_type="payment:validate", amount=299.99)
            time.sleep(0.06)
            raise TimeoutError("Payment gateway timeout")
    except TimeoutError as e:
        Message.log(message_type="payment:error", error=str(e))
        Message.log(message_type="http:response", status=500, error="Payment processing failed")

# Server shutdown
with start_action(action_type="server:shutdown"):
    Message.log(message_type="server:closing")
    time.sleep(0.02)
    Message.log(message_type="server:stopped")

print(f"✓ Log created: {log_file}")
print("\nView with: python view_tree.py example_04_api_server.log")
