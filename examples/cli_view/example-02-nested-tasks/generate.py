#!/usr/bin/env python3
"""Generate nested_tasks.log for Example 02."""

import json
from datetime import datetime, timezone

logs = []

# Parent task
parent_tid = "Xa.1"
logs.append({
    "tid": parent_tid,
    "at": "process_data",
    "st": "started",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1],
    "msg": "Starting data processing",
})

# Child task: transform_data
child_tid = "Xa.2"
logs.append({
    "tid": child_tid,
    "at": "transform_data",
    "st": "started",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1, 1],
    "msg": "Transforming data",
})
logs.append({
    "tid": child_tid,
    "at": "transform_data",
    "st": "succeeded",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1, 2],
    "msg": "Transformation complete",
    "dur": 0.2,
})

# End parent
logs.append({
    "tid": parent_tid,
    "at": "process_data",
    "st": "succeeded",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [2],
    "msg": "Processing complete",
    "dur": 2.0,
})

with open("nested_tasks.log", "w") as f:
    for log in logs:
        f.write(json.dumps(log) + "\n")

print("Generated nested_tasks.log with parent-child structure")
