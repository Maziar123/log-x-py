#!/usr/bin/env python3
"""Example 05: Data Pipeline - complex ETL pipeline with multiple stages."""

import time

from logxpy import log, start_action

# Main pipeline
with start_action(action_type="pipeline:run", pipeline_id="daily_etl"):
    log.info("Pipeline start", timestamp="2026-02-05T10:00:00")

    # Stage 1: Extract
    with start_action(action_type="pipeline:extract", source="database"):
        log.info("Connecting", host="prod-db.example.com")
        time.sleep(0.05)
        log.info("Querying", table="transactions", date="2026-02-05")
        time.sleep(0.12)
        log.success("Extract complete", records=15234)

    # Stage 2: Transform
    with start_action(action_type="pipeline:transform"):
        log.info("Validating", records=15234)
        time.sleep(0.08)
        log.info("Filtering", invalid_records=12, valid_records=15222)
        time.sleep(0.10)
        log.info("Enriching", external_api="customer_service")
        time.sleep(0.15)
        log.info("Aggregating", groups=156)
        time.sleep(0.09)
        log.success("Transform complete", output_records=156)

    # Stage 3: Load
    with start_action(action_type="pipeline:load", destination="warehouse"):
        log.info("Connecting", warehouse="snowflake", database="analytics")
        time.sleep(0.06)
        log.info("Preparing", table="daily_transactions")
        time.sleep(0.04)
        log.info("Inserting", records=156, mode="append")
        time.sleep(0.11)
        log.success("Load complete", duration_ms=210)

    # Stage 4: Cleanup
    with start_action(action_type="pipeline:cleanup"):
        log.info("Removing temp files", files_deleted=3)
        time.sleep(0.03)
        log.info("Cache cleared", cache_cleared=True)
        time.sleep(0.02)

    log.success("Pipeline complete",
                total_duration_ms=950,
                records_processed=15234,
                records_output=156)

print("✓ Log created: example_05_data_pipeline.log")
