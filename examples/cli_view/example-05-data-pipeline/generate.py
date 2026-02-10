#!/usr/bin/env python3
"""Generate data_pipeline.log for Example 05."""

import json
from datetime import datetime, timezone

logs = []

# Main pipeline task
pipeline_tid = "Xa.1"
logs.append({
    "tid": pipeline_tid,
    "at": "data_pipeline",
    "st": "started",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1],
    "pipeline_name": "daily_import",
    "source": "external_api",
})

# Load data stage
load_tid = "Xa.2"
logs.append({
    "tid": load_tid,
    "at": "load_data",
    "st": "started",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1, 1],
    "destination": "warehouse",
})
logs.append({
    "tid": load_tid,
    "at": "load_data",
    "st": "succeeded",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1, 2],
    "records_loaded": 1000,
    "dur": 2.5,
})

# Transform data stage
transform_tid = "Xa.3"
logs.append({
    "tid": transform_tid,
    "at": "transform_data",
    "st": "started",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1, 1],
    "transform_type": "normalize",
})
logs.append({
    "tid": transform_tid,
    "at": "transform_data",
    "st": "succeeded",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1, 2],
    "records_transformed": 1000,
    "dur": 3.0,
})

# Validate stage
validate_tid = "Xa.4"
logs.append({
    "tid": validate_tid,
    "at": "validate_data",
    "st": "started",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1, 1],
})
logs.append({
    "tid": validate_tid,
    "at": "validate_data",
    "st": "succeeded",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1, 2],
    "valid": 995,
    "invalid": 5,
    "dur": 1.0,
})

# Save stage
save_tid = "Xa.5"
logs.append({
    "tid": save_tid,
    "at": "save_data",
    "st": "started",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1, 1],
    "destination": "database",
})
logs.append({
    "tid": save_tid,
    "at": "save_data",
    "st": "succeeded",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [1, 2],
    "records_saved": 995,
    "dur": 2.0,
})

# End pipeline
logs.append({
    "tid": pipeline_tid,
    "at": "data_pipeline",
    "st": "succeeded",
    "ts": datetime.now(timezone.utc).timestamp(),
    "lvl": [2],
    "total_processed": 995,
    "dur": 8.5,
})

with open("data_pipeline.log", "w") as f:
    for log in logs:
        f.write(json.dumps(log) + "\n")

print("Generated data_pipeline.log with 4-stage pipeline")
