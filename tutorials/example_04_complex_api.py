#!/usr/bin/env python3
"""Example 04: Complex API Request Simulation"""

import random
import time
from pathlib import Path

from _setup_imports import log, start_action, to_file

log_file = Path(__file__).parent / "example_04_complex_api.log"
to_file(open(log_file, "w"))

print(f"Creating log: {log_file.name}")

# Simulate multiple API requests
for req_num in range(1, 4):
    request_id = f"req_{req_num:04d}"

    with start_action(action_type="api:request", request_id=request_id):
        log.info("Request received", method="POST", path="/api/orders", ip=f"192.168.1.{random.randint(1, 255)}")

        # Authentication
        with start_action(action_type="auth:verify"):
            time.sleep(0.02)
            log.success("User authenticated", user_id=f"user_{req_num}")

        # Database query
        with start_action(action_type="db:query"):
            log.info("Executing query", table="orders")
            time.sleep(0.05)
            log.success("Query complete", rows=random.randint(1, 50))

        # External API call
        with start_action(action_type="external:notify"):
            log.info("Calling notification service")
            time.sleep(0.08)

            if req_num == 2:
                log.error("Notification failed", error="Timeout")
            else:
                log.success("Notification sent")

        if req_num == 2:
            log.warning("Request completed with warnings", status_code=200)
        else:
            log.success("Request completed", status_code=201)

print(f"✓ Log created: {log_file}")
print(f"\nView with: python ../examples-log-view/view_tree.py {log_file}")
