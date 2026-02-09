#!/usr/bin/env python3
"""
Example 05: Data Pipeline
Complex data processing pipeline with multiple stages
"""

import sys
import time
from pathlib import Path

# Add logxpy to path
sys.path.insert(0, str(Path(__file__).parent.parent / "logxpy"))

from logxpy import Message, start_action, to_file

# Setup logging to file (delete old log first)
log_file = Path(__file__).parent / "example_05_data_pipeline.log"
if log_file.exists():
    log_file.unlink()
with open(log_file, "w", encoding="utf-8") as f:
    to_file(f)

# Main pipeline
with start_action(action_type="pipeline:run", pipeline_id="daily_etl"):
    Message.log(message_type="pipeline:start", timestamp="2026-02-05T10:00:00")

    # Stage 1: Extract
    with start_action(action_type="pipeline:extract", source="database"):
        Message.log(message_type="extract:connect", host="prod-db.example.com")
        time.sleep(0.05)
        Message.log(message_type="extract:query", table="transactions", date="2026-02-05")
        time.sleep(0.12)
        Message.log(message_type="extract:complete", records=15234)

    # Stage 2: Transform
    with start_action(action_type="pipeline:transform"):
        Message.log(message_type="transform:validate", records=15234)
        time.sleep(0.08)
        Message.log(message_type="transform:filter", invalid_records=12, valid_records=15222)
        time.sleep(0.10)
        Message.log(message_type="transform:enrich", external_api="customer_service")
        time.sleep(0.15)
        Message.log(message_type="transform:aggregate", groups=156)
        time.sleep(0.09)
        Message.log(message_type="transform:complete", output_records=156)

    # Stage 3: Load
    with start_action(action_type="pipeline:load", destination="warehouse"):
        Message.log(message_type="load:connect", warehouse="snowflake", database="analytics")
        time.sleep(0.06)
        Message.log(message_type="load:prepare", table="daily_transactions")
        time.sleep(0.04)
        Message.log(message_type="load:insert", records=156, mode="append")
        time.sleep(0.11)
        Message.log(message_type="load:complete", duration_ms=210)

    # Stage 4: Cleanup
    with start_action(action_type="pipeline:cleanup"):
        Message.log(message_type="cleanup:temp_files", files_deleted=3)
        time.sleep(0.03)
        Message.log(message_type="cleanup:cache", cache_cleared=True)
        time.sleep(0.02)

    Message.log(
        message_type="pipeline:complete",
        total_duration_ms=950,
        records_processed=15234,
        records_output=156,
        status="success",
    )

print(f"✓ Log created: {log_file}")
print("\nView with: python view_tree.py example_05_data_pipeline.log")
