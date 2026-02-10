#!/usr/bin/env python3
"""Generate simple_task.log for Example 01."""

import json
from datetime import datetime, timezone

# Simple task log entries
logs = []

# Task 1: simple_task
task1_tid = "Xa.1"
logs.append({
    "tid": task1_tid,
    "at": "simple_task",
    "st": "started",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1],
    "msg": "Starting simple task",
})
logs.append({
    "tid": task1_tid,
    "at": "simple_task",
    "st": "succeeded",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [2],
    "msg": "Task completed",
    "dur": 1.0,
})

# Task 2: another_task
task2_tid = "Xa.2"
logs.append({
    "tid": task2_tid,
    "at": "another_task",
    "st": "started",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1],
    "msg": "Starting another task",
})
logs.append({
    "tid": task2_tid,
    "at": "another_task",
    "st": "succeeded",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [2],
    "msg": "Another task completed",
    "dur": 1.0,
})

# Write log file
with open("simple_task.log", "w") as f:
    for log in logs:
        f.write(json.dumps(log) + "\n")

print("Generated simple_task.log with 2 tasks")
