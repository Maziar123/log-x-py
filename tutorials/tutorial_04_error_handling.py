#!/usr/bin/env python3
"""
Tutorial 04: Error Handling and Exception Logging
==================================================

This tutorial demonstrates:
- Logging exceptions with tracebacks
- Error recovery patterns
- Try/catch with proper logging
- Exception context preservation
- Different error severity levels

Run this script to generate: tutorial_04_errors.log
Then view with: logxpy-view tutorial_04_errors.log
"""

import time
from pathlib import Path
from _setup_imports import log, to_file, start_action, write_traceback


def setup_logging():
    """Configure logging to write to a file."""
    log_file = Path(__file__).parent / "tutorial_04_errors.log"
    to_file(open(log_file, "w"))
    print(f"✓ Logging to: {log_file}")
    return log_file


# ============================================================================
# 1. Basic Exception Logging
# ============================================================================

def demo_basic_exception():
    """Demonstrate basic exception logging."""
    with start_action(action_type="demo:basic_exception"):
        log.info("Attempting risky operation")
        
        try:
            result = 10 / 0
        except ZeroDivisionError as e:
            # Log exception with automatic traceback
            log.exception("Division by zero error", operation="10 / 0")
            # Note: write_traceback can be used for full Eliot traceback format
            # but requires proper logger context - log.exception() is simpler


# ============================================================================
# 2. Exception with Context
# ============================================================================

def process_user_data(user_id: int, data: dict):
    """Process user data with error handling."""
    with start_action(action_type="user:process_data", user_id=user_id):
        try:
            log.info("Validating user data", fields=list(data.keys()))
            
            # Simulate validation errors
            if "email" not in data:
                raise ValueError("Email field is required")
            
            if not data["email"].endswith("@example.com"):
                raise ValueError("Invalid email domain")
            
            log.success("User data validated", user_id=user_id)
            
        except ValueError as e:
            log.error("Validation failed",
                     user_id=user_id,
                     error=str(e),
                     data_received=data)
            raise  # Re-raise for upstream handling


def demo_exception_with_context():
    """Demonstrate exception logging with rich context."""
    test_users = [
        (1, {"email": "alice@example.com", "name": "Alice"}),
        (2, {"name": "Bob"}),  # Missing email
        (3, {"email": "charlie@wrongdomain.com", "name": "Charlie"}),  # Invalid domain
        (4, {"email": "david@example.com", "name": "David"}),
    ]
    
    for user_id, data in test_users:
        try:
            process_user_data(user_id, data)
        except ValueError:
            log.warning("Skipping invalid user", user_id=user_id)


# ============================================================================
# 3. Nested Error Handling
# ============================================================================

def connect_to_database(host: str, port: int):
    """Simulate database connection."""
    if port != 5432:
        raise ConnectionError(f"Cannot connect to {host}:{port}")
    return f"connection_{host}"


def fetch_data_from_db(connection, query: str):
    """Simulate database query."""
    if "DROP" in query.upper():
        raise ValueError("Dangerous query detected!")
    return [{"id": 1, "name": "Result"}]


def demo_nested_errors():
    """Demonstrate nested error handling across multiple layers."""
    with start_action(action_type="database:operation", operation="fetch_user_list"):
        try:
            # Layer 1: Connection
            log.info("Connecting to database", host="localhost", port=5433)
            connection = connect_to_database("localhost", 5433)
            
            # Layer 2: Query
            log.info("Executing query", query="SELECT * FROM users")
            results = fetch_data_from_db(connection, "SELECT * FROM users")
            
            log.success("Data fetched", rows=len(results))
            
        except ConnectionError as e:
            log.error("Database connection failed",
                     host="localhost",
                     port=5433,
                     error=str(e),
                     retry_suggestion="Check if port is correct (should be 5432)")
            
        except ValueError as e:
            log.critical("Security violation detected",
                        error=str(e),
                        action="Query blocked")


# ============================================================================
# 4. Error Recovery Patterns
# ============================================================================

def demo_error_recovery():
    """Demonstrate error recovery with fallback mechanisms."""
    with start_action(action_type="service:fetch_data", source="primary"):
        primary_failed = False
        
        # Try primary source
        try:
            log.info("Attempting primary data source", endpoint="/api/v1/data")
            time.sleep(0.05)
            raise TimeoutError("Primary service timeout")
        except TimeoutError as e:
            log.warning("Primary source failed",
                       error=str(e),
                       fallback="Trying secondary source")
            primary_failed = True
        
        # Fallback to secondary source
        if primary_failed:
            with start_action(action_type="service:fallback", source="secondary"):
                try:
                    log.info("Attempting secondary data source", endpoint="/api/v2/data")
                    time.sleep(0.05)
                    log.success("Data fetched from secondary source",
                               latency_ms=50)
                except Exception as e:
                    log.error("Secondary source also failed", error=str(e))
                    
                    # Last resort: cache
                    with start_action(action_type="service:fallback", source="cache"):
                        log.info("Falling back to cached data")
                        log.warning("Using stale data from cache",
                                   age_seconds=3600,
                                   recommendation="Data may be outdated")


# ============================================================================
# 5. Complex Error Scenarios
# ============================================================================

class DataProcessingError(Exception):
    """Custom exception for data processing errors."""
    pass


def validate_record(record: dict):
    """Validate a single record."""
    required_fields = ["id", "name", "email", "status"]
    missing = [f for f in required_fields if f not in record]
    if missing:
        raise DataProcessingError(f"Missing fields: {missing}")


def transform_record(record: dict):
    """Transform a record."""
    if record.get("status") == "invalid":
        raise DataProcessingError("Cannot transform invalid record")
    return {**record, "processed": True}


def demo_batch_processing_with_errors():
    """Demonstrate batch processing with partial failures."""
    records = [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "status": "active"},
        {"id": 2, "name": "Bob", "status": "active"},  # Missing email
        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "status": "invalid"},
        {"id": 4, "name": "David", "email": "david@example.com", "status": "active"},
        {"id": 5, "email": "eve@example.com", "status": "active"},  # Missing name
    ]
    
    with start_action(action_type="batch:process_records", total=len(records)):
        successful = 0
        failed = 0
        
        for record in records:
            record_id = record.get("id", "unknown")
            
            with start_action(action_type="record:process", record_id=record_id):
                try:
                    log.info("Processing record", record_id=record_id)
                    
                    # Validate
                    validate_record(record)
                    log.checkpoint("Validation passed")
                    
                    # Transform
                    transformed = transform_record(record)
                    log.checkpoint("Transformation complete")
                    
                    log.success("Record processed successfully",
                               record_id=record_id)
                    successful += 1
                    
                except DataProcessingError as e:
                    log.error("Record processing failed",
                             record_id=record_id,
                             error=str(e),
                             record_data=record)
                    failed += 1
        
        log.info("Batch processing complete",
                total=len(records),
                successful=successful,
                failed=failed,
                success_rate=f"{(successful/len(records)*100):.1f}%")


def main():
    """Run all demonstrations."""
    log_file = setup_logging()
    
    print("\n" + "=" * 60)
    print("Tutorial 04: Error Handling")
    print("=" * 60)
    
    print("\n1. Basic Exception Logging")
    demo_basic_exception()
    
    print("\n2. Exception with Context")
    demo_exception_with_context()
    
    print("\n3. Nested Error Handling")
    demo_nested_errors()
    
    print("\n4. Error Recovery Patterns")
    demo_error_recovery()
    
    print("\n5. Batch Processing with Errors")
    demo_batch_processing_with_errors()
    
    log.success("Tutorial completed!", tutorial="04_error_handling")
    
    print("\n" + "=" * 60)
    print("✓ Log file created successfully!")
    print("=" * 60)
    print(f"\nTo view the logs:")
    print(f"  logxpy-view {log_file}")
    print(f"\nTo view only errors and failures:")
    print(f"  logxpy-view --action-status failed {log_file}")
    print(f"\nTo search for specific errors:")
    print(f"  logxpy-view --keyword 'validation' {log_file}")
    print(f"\nTo view with full tracebacks:")
    print(f"  logxpy-view --field-limit 200 {log_file}")


if __name__ == "__main__":
    main()
