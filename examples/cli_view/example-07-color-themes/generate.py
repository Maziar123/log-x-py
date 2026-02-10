#!/usr/bin/env python3
"""Generate with_errors.log for Example 07 (color themes)."""

import json
from datetime import datetime, timezone

logs = []

# Successful task
success_tid = "Xa.1"
logs.append({
    "tid": success_tid,
    "at": "successful_task",
    "st": "started",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1],
    "msg": "Starting successful task",
})
logs.append({
    "tid": success_tid,
    "at": "successful_task",
    "st": "succeeded",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [2],
    "msg": "Task succeeded",
    "dur": 1.0,
})

# Failed task
fail_tid = "Xa.2"
logs.append({
    "tid": fail_tid,
    "at": "failing_task",
    "st": "started",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1],
    "msg": "Starting failing task",
})
logs.append({
    "tid": fail_tid,
    "at": "failing_task",
    "st": "failed",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [2],
    "msg": "Task failed with error",
    "error": "ValueError: Invalid input",
    "dur": 1.0,
})

with open("with_errors.log", "w") as f:
    for log in logs:
        f.write(json.dumps(log) + "\n")

print("Generated with_errors.log for color themes example")
