#!/usr/bin/env python3
"""Generate deep_functions.log for Example 10 (deep nesting)."""

import json
from datetime import datetime, timezone

logs = []
base_time = datetime.now(timezone.utc).timestamp()

# Main HTTP request handler
main_tid = "Xa.1"
logs.append({
    "tid": main_tid,
    "at": "http_request_handler",
    "st": "started",
    "ts": base_time,
    "lvl": [1],
    "client_ip": "192.168.1.100",
    "method": "POST",
    "path": "/api/v2/orders",
})

# Auth middleware (level 2)
auth_tid = "Xa.2"
logs.append({
    "tid": auth_tid,
    "at": "authentication_middleware",
    "st": "started",
    "ts": base_time + 0.01,
    "lvl": [1, 1],
    "auth_header": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
})

# JWT validation (level 3)
jwt_tid = "Xa.3"
logs.append({
    "tid": jwt_tid,
    "at": "jwt_token_validation",
    "st": "started",
    "ts": base_time + 0.02,
    "lvl": [1, 1, 1],
    "token_type": "access",
})

# JWT parsing (level 4)
parse_tid = "Xa.4"
logs.append({
    "tid": parse_tid,
    "at": "jwt_token_parsing",
    "st": "started",
    "ts": base_time + 0.025,
    "lvl": [1, 1, 1, 1],
})
logs.append({
    "tid": parse_tid,
    "at": "jwt_token_parsing",
    "st": "succeeded",
    "ts": base_time + 0.03,
    "lvl": [1, 1, 1, 2],
    "algorithm": "HS256",
    "dur": 0.01,
})

# Permission check (level 4)
perm_tid = "Xa.5"
logs.append({
    "tid": perm_tid,
    "at": "permission_check",
    "st": "started",
    "ts": base_time + 0.04,
    "lvl": [1, 1, 2, 1],
    "action": "create",
    "resource": "orders",
})
logs.append({
    "tid": perm_tid,
    "at": "permission_check",
    "st": "succeeded",
    "ts": base_time + 0.07,
    "lvl": [1, 1, 2, 2],
    "allowed": True,
    "dur": 0.03,
})

# End JWT validation
logs.append({
    "tid": jwt_tid,
    "at": "jwt_token_validation",
    "st": "succeeded",
    "ts": base_time + 0.08,
    "lvl": [1, 1, 2],
    "user_id": "user_123",
    "dur": 0.06,
})

# Rate limit check (level 3)
rate_tid = "Xa.6"
logs.append({
    "tid": rate_tid,
    "at": "rate_limit_check",
    "st": "started",
    "ts": base_time + 0.09,
    "lvl": [1, 1, 3, 1],
    "user_id": "user_123",
    "endpoint": "/api/v2/orders",
})
logs.append({
    "tid": rate_tid,
    "at": "rate_limit_check",
    "st": "succeeded",
    "ts": base_time + 0.10,
    "lvl": [1, 1, 3, 2],
    "allowed": True,
    "remaining": 99,
    "dur": 0.01,
})

# End auth middleware
logs.append({
    "tid": auth_tid,
    "at": "authentication_middleware",
    "st": "succeeded",
    "ts": base_time + 0.13,
    "lvl": [1, 2],
    "authenticated_as": "user_123",
    "dur": 0.12,
})

# Request validation (level 2)
validate_tid = "Xa.7"
logs.append({
    "tid": validate_tid,
    "at": "request_validation",
    "st": "started",
    "ts": base_time + 0.14,
    "lvl": [1, 1],
    "content_type": "application/json",
})

# Schema validation (level 3)
schema_tid = "Xa.8"
logs.append({
    "tid": schema_tid,
    "at": "json_schema_validation",
    "st": "started",
    "ts": base_time + 0.15,
    "lvl": [1, 1, 1, 1],
    "schema": "order_request_v1",
})
logs.append({
    "tid": schema_tid,
    "at": "json_schema_validation",
    "st": "succeeded",
    "ts": base_time + 0.18,
    "lvl": [1, 1, 1, 2],
    "valid": True,
    "dur": 0.03,
})

# Business logic validation (level 3)
business_tid = "Xa.9"
logs.append({
    "tid": business_tid,
    "at": "business_rules_validation",
    "st": "started",
    "ts": base_time + 0.19,
    "lvl": [1, 1, 2, 1],
    "rules": ["inventory_check", "pricing_check"],
})

# Inventory check (level 4)
inventory_tid = "Xa.a"
logs.append({
    "tid": inventory_tid,
    "at": "inventory_check",
    "st": "started",
    "ts": base_time + 0.20,
    "lvl": [1, 1, 2, 1, 1],
    "product_id": "prod_456",
    "quantity": 5,
})
logs.append({
    "tid": inventory_tid,
    "at": "inventory_check",
    "st": "succeeded",
    "ts": base_time + 0.25,
    "lvl": [1, 1, 2, 1, 2],
    "available": True,
    "stock": 100,
    "dur": 0.05,
})

# Pricing check (level 4)
pricing_tid = "Xa.b"
logs.append({
    "tid": pricing_tid,
    "at": "pricing_check",
    "st": "started",
    "ts": base_time + 0.26,
    "lvl": [1, 1, 2, 2, 1],
    "product_id": "prod_456",
    "quantity": 5,
})
logs.append({
    "tid": pricing_tid,
    "at": "pricing_check",
    "st": "succeeded",
    "ts": base_time + 0.29,
    "lvl": [1, 1, 2, 2, 2],
    "unit_price": 29.99,
    "total": 149.95,
    "dur": 0.03,
})

logs.append({
    "tid": business_tid,
    "at": "business_rules_validation",
    "st": "succeeded",
    "ts": base_time + 0.30,
    "lvl": [1, 1, 2, 2],
    "all_passed": True,
    "dur": 0.11,
})

logs.append({
    "tid": validate_tid,
    "at": "request_validation",
    "st": "succeeded",
    "ts": base_time + 0.35,
    "lvl": [1, 2],
    "validated": True,
    "dur": 0.21,
})

# Order processing (level 2)
process_tid = "Xa.c"
logs.append({
    "tid": process_tid,
    "at": "order_processing",
    "st": "started",
    "ts": base_time + 0.36,
    "lvl": [1, 1],
    "order_type": "new",
})

# Create order record (level 3)
create_tid = "Xa.d"
logs.append({
    "tid": create_tid,
    "at": "create_order_record",
    "st": "started",
    "ts": base_time + 0.37,
    "lvl": [1, 1, 1, 1],
})
logs.append({
    "tid": create_tid,
    "at": "create_order_record",
    "st": "succeeded",
    "ts": base_time + 0.50,
    "lvl": [1, 1, 1, 2],
    "order_id": "ord_789",
    "dur": 0.13,
})

# Update inventory (level 3)
update_inv_tid = "Xa.e"
logs.append({
    "tid": update_inv_tid,
    "at": "update_inventory",
    "st": "started",
    "ts": base_time + 0.51,
    "lvl": [1, 1, 2, 1],
    "product_id": "prod_456",
    "delta": -5,
})

# Database operation (level 4)
db_inv_tid = "Xa.f"
logs.append({
    "tid": db_inv_tid,
    "at": "database_update",
    "st": "started",
    "ts": base_time + 0.52,
    "lvl": [1, 1, 2, 1, 1],
    "table": "inventory",
    "operation": "decrement",
})
logs.append({
    "tid": db_inv_tid,
    "at": "database_update",
    "st": "succeeded",
    "ts": base_time + 0.60,
    "lvl": [1, 1, 2, 1, 2],
    "rows_affected": 1,
    "dur": 0.08,
})

logs.append({
    "tid": update_inv_tid,
    "at": "update_inventory",
    "st": "succeeded",
    "ts": base_time + 0.61,
    "lvl": [1, 1, 2, 2],
    "new_stock": 95,
    "dur": 0.10,
})

# Payment processing (level 3)
payment_tid = "Xa.g"
logs.append({
    "tid": payment_tid,
    "at": "payment_processing",
    "st": "started",
    "ts": base_time + 0.62,
    "lvl": [1, 1, 3, 1],
    "amount": 149.95,
    "currency": "USD",
})

# Payment gateway call (level 4)
gateway_tid = "Xa.h"
logs.append({
    "tid": gateway_tid,
    "at": "payment_gateway_call",
    "st": "started",
    "ts": base_time + 0.63,
    "lvl": [1, 1, 3, 1, 1],
    "gateway": "stripe",
    "method": "charge",
})
logs.append({
    "tid": gateway_tid,
    "at": "payment_gateway_call",
    "st": "succeeded",
    "ts": base_time + 0.70,
    "lvl": [1, 1, 3, 1, 2],
    "transaction_id": "txn_xyz123",
    "dur": 0.07,
})

logs.append({
    "tid": payment_tid,
    "at": "payment_processing",
    "st": "succeeded",
    "ts": base_time + 0.71,
    "lvl": [1, 1, 3, 2],
    "payment_id": "pay_abc456",
    "dur": 0.09,
})

# Notification (level 3)
notify_tid = "Xa.i"
logs.append({
    "tid": notify_tid,
    "at": "send_confirmation_email",
    "st": "started",
    "ts": base_time + 0.72,
    "lvl": [1, 1, 4, 1],
    "recipient": "customer@example.com",
})
logs.append({
    "tid": notify_tid,
    "at": "send_confirmation_email",
    "st": "succeeded",
    "ts": base_time + 0.78,
    "lvl": [1, 1, 4, 2],
    "message_id": "msg_def789",
    "dur": 0.06,
})

logs.append({
    "tid": process_tid,
    "at": "order_processing",
    "st": "succeeded",
    "ts": base_time + 0.79,
    "lvl": [1, 2],
    "order_id": "ord_789",
    "dur": 0.43,
})

# Response formatting (level 2)
response_tid = "Xa.j"
logs.append({
    "tid": response_tid,
    "at": "response_formatting",
    "st": "started",
    "ts": base_time + 0.80,
    "lvl": [1, 1],
    "format": "json",
})
logs.append({
    "tid": response_tid,
    "at": "response_formatting",
    "st": "succeeded",
    "ts": base_time + 0.81,
    "lvl": [1, 2],
    "status_code": 201,
    "dur": 0.01,
})

# End main request
logs.append({
    "tid": main_tid,
    "at": "http_request_handler",
    "st": "succeeded",
    "ts": base_time + 0.82,
    "lvl": [2],
    "status_code": 201,
    "dur": 0.82,
})

with open("deep_functions.log", "w") as f:
    for log in logs:
        f.write(json.dumps(log) + "\n")

print("Generated deep_functions.log with deep nesting (up to 5 levels)")
