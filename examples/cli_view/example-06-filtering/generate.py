#!/usr/bin/env python3
"""Generate web_service.log for Example 06 (filtering)."""

import json
from datetime import datetime, timezone

logs = []
base_time = datetime.now(timezone.utc).timestamp()

# Request 1: GET /api/users - success
req1_tid = "Xa.1"
logs.append({
    "tid": req1_tid,
    "at": "http_request",
    "st": "started",
    "ts": base_time,
    "lvl": [1],
    "method": "GET",
    "path": "/api/users",
})
logs.append({
    "tid": req1_tid,
    "at": "http_request",
    "st": "succeeded",
    "ts": base_time + 0.1,
    "lvl": [2],
    "status_code": 200,
    "dur": 0.1,
})

# Request 2: POST /api/users - success
req2_tid = "Xa.2"
logs.append({
    "tid": req2_tid,
    "at": "http_request",
    "st": "started",
    "ts": base_time + 0.2,
    "lvl": [1],
    "method": "POST",
    "path": "/api/users",
    "user_id": 123,
})
logs.append({
    "tid": req2_tid,
    "at": "http_request",
    "st": "succeeded",
    "ts": base_time + 0.7,
    "lvl": [2],
    "status_code": 201,
    "dur": 0.5,
})

# Database query (separate task)
db_tid = "Xa.3"
logs.append({
    "tid": db_tid,
    "at": "database_query",
    "st": "started",
    "ts": base_time + 0.8,
    "lvl": [1],
    "query": "SELECT * FROM users",
})
logs.append({
    "tid": db_tid,
    "at": "database_query",
    "st": "succeeded",
    "ts": base_time + 0.9,
    "lvl": [2],
    "rows": 50,
    "dur": 0.1,
})

# Request 3: GET /api/products - FAILED
req3_tid = "Xa.4"
logs.append({
    "tid": req3_tid,
    "at": "http_request",
    "st": "started",
    "ts": base_time + 1.0,
    "lvl": [1],
    "method": "GET",
    "path": "/api/products",
})
logs.append({
    "tid": req3_tid,
    "at": "http_request",
    "st": "failed",
    "ts": base_time + 6.0,
    "lvl": [2],
    "error": "Connection timeout",
    "dur": 5.0,
})

with open("web_service.log", "w") as f:
    for log in logs:
        f.write(json.dumps(log) + "\n")

print("Generated web_service.log for filtering example (3 requests, 1 failure)")
