#!/usr/bin/env python3
"""Generate web_service.log for Example 04."""

import json
from datetime import datetime, timezone

logs = []

# HTTP request task
request_tid = "Xa.1"
logs.append({
    "tid": request_tid,
    "at": "http_request",
    "st": "started",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1],
    "method": "GET",
    "path": "/api/users/123",
})

# Database query child
db_tid = "Xa.2"
logs.append({
    "tid": db_tid,
    "at": "database_query",
    "st": "started",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1, 1],
    "query": "SELECT * FROM users WHERE id = 123",
})
logs.append({
    "tid": db_tid,
    "at": "database_query",
    "st": "succeeded",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1, 2],
    "rows": 1,
    "dur": 0.2,
})

# End request
logs.append({
    "tid": request_tid,
    "at": "http_request",
    "st": "succeeded",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [2],
    "status_code": 200,
    "dur": 1.0,
})

with open("web_service.log", "w") as f:
    for log in logs:
        f.write(json.dumps(log) + "\n")

print("Generated web_service.log with HTTP request and DB query")
