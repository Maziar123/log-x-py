#!/usr/bin/env python3
"""
Tutorial 03: Decorators for Automatic Logging
==============================================

This tutorial demonstrates:
- @log.logged - Automatic function entry/exit logging
- @log.timed - Execution time tracking
- @log.retry - Automatic retry with logging
- Decorator configuration options

Run this script to generate: tutorial_03_decorators.log
Then view with: logxpy-view tutorial_03_decorators.log
"""

import time
import random
from pathlib import Path
from _setup_imports import log, to_file


def setup_logging():
    """Configure logging to write to a file."""
    log_file = Path(__file__).parent / "tutorial_03_decorators.log"
    to_file(open(log_file, "w"))
    print(f"✓ Logging to: {log_file}")
    return log_file


# ============================================================================
# 1. @log.logged - Automatic entry/exit logging
# ============================================================================

@log.logged
def calculate_total(items: list, tax_rate: float = 0.1):
    """Calculate total with tax. Decorator logs entry/exit automatically."""
    subtotal = sum(item['price'] * item['quantity'] for item in items)
    tax = subtotal * tax_rate
    total = subtotal + tax
    time.sleep(0.05)  # Simulate processing
    return round(total, 2)


@log.logged(capture_args=True, capture_result=True, level="INFO")
def process_payment(amount: float, card_number: str, cvv: str):
    """Process payment. Captures arguments and result."""
    # Simulate payment processing
    time.sleep(0.1)
    transaction_id = f"txn_{random.randint(1000, 9999)}"
    return {"success": True, "transaction_id": transaction_id}


@log.logged(capture_args=False, capture_result=False)
def handle_sensitive_data(password: str, api_key: str):
    """Handle sensitive data. Args/result NOT logged for security."""
    # Do something with sensitive data
    time.sleep(0.03)
    return "processed"


# ============================================================================
# 2. @log.timed - Execution time tracking
# ============================================================================

@log.timed(metric="database_query_time")
def fetch_user_data(user_id: int):
    """Fetch user data. Logs execution time."""
    time.sleep(0.15)  # Simulate database query
    return {"user_id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}


@log.timed(metric="cache_operation")
def cache_lookup(key: str):
    """Cache lookup with timing."""
    time.sleep(random.uniform(0.01, 0.08))
    return f"value_for_{key}"


# ============================================================================
# 3. @log.retry - Automatic retry with logging
# ============================================================================

attempt_counter = 0

@log.retry(attempts=3, delay=0.05, on_retry=lambda n, e: log.warning(f"Retry {n}", error=str(e)))
def unstable_api_call(endpoint: str):
    """Simulates an unstable API that sometimes fails."""
    global attempt_counter
    attempt_counter += 1
    
    # 50% chance of failure on first attempts
    if attempt_counter % 3 != 0:
        raise ConnectionError(f"Failed to connect to {endpoint}")
    
    return {"status": "success", "data": "API response data"}


@log.retry(attempts=5, delay=0.1, backoff=2.0)
def download_file(url: str, retries_allowed: int = 5):
    """Download file with exponential backoff retry."""
    if random.random() < 0.6:
        raise TimeoutError(f"Timeout downloading {url}")
    return f"file_data_from_{url}"


# ============================================================================
# 4. Combining decorators
# ============================================================================

@log.logged
@log.timed(metric="complex_operation_time")
def complex_operation(data: dict):
    """Combine multiple decorators for comprehensive logging."""
    log.info("Starting complex processing", data_size=len(data))
    
    # Multiple steps
    time.sleep(0.08)
    log.checkpoint("Step 1: Validation complete")
    
    time.sleep(0.12)
    log.checkpoint("Step 2: Transformation complete")
    
    time.sleep(0.05)
    log.checkpoint("Step 3: Output generation complete")
    
    return {"processed": True, "output_size": len(data) * 2}


# ============================================================================
# Demonstration functions
# ============================================================================

def demo_logged_decorator():
    """Demonstrate @log.logged decorator."""
    log.info("=== Demo: @log.logged ===")
    
    items = [
        {"name": "Widget", "price": 10.00, "quantity": 2},
        {"name": "Gadget", "price": 25.00, "quantity": 1},
        {"name": "Doohickey", "price": 5.00, "quantity": 3}
    ]
    
    total = calculate_total(items, tax_rate=0.08)
    log.info("Total calculated", total=total)
    
    result = process_payment(total, "4532-1234-5678-9012", "123")
    log.info("Payment processed", result=result)
    
    handle_sensitive_data("secret_password", "api_key_12345")


def demo_timed_decorator():
    """Demonstrate @log.timed decorator."""
    log.info("=== Demo: @log.timed ===")
    
    for user_id in [101, 102, 103]:
        user_data = fetch_user_data(user_id)
        log.info("User data fetched", user_id=user_id, name=user_data["name"])
    
    for key in ["user_session", "cache_data", "temp_storage"]:
        value = cache_lookup(key)
        log.info("Cache lookup complete", key=key)


def demo_retry_decorator():
    """Demonstrate @log.retry decorator."""
    log.info("=== Demo: @log.retry ===")
    
    global attempt_counter
    attempt_counter = 0
    
    try:
        result = unstable_api_call("/api/v1/data")
        log.success("API call succeeded after retries", result=result)
    except Exception as e:
        log.error("API call failed permanently", error=str(e))
    
    try:
        file_data = download_file("https://example.com/file.zip")
        log.success("File downloaded", size=len(file_data))
    except Exception as e:
        log.error("Download failed", error=str(e))


def demo_combined_decorators():
    """Demonstrate combining decorators."""
    log.info("=== Demo: Combined Decorators ===")
    
    test_data = {"records": list(range(100)), "metadata": {"version": 1}}
    result = complex_operation(test_data)
    log.success("Complex operation completed", result=result)


def main():
    """Run all demonstrations."""
    log_file = setup_logging()
    
    print("\n" + "=" * 60)
    print("Tutorial 03: Decorators")
    print("=" * 60)
    
    print("\n1. @log.logged Decorator")
    demo_logged_decorator()
    
    print("\n2. @log.timed Decorator")
    demo_timed_decorator()
    
    print("\n3. @log.retry Decorator")
    demo_retry_decorator()
    
    print("\n4. Combined Decorators")
    demo_combined_decorators()
    
    log.success("Tutorial completed!", tutorial="03_decorators")
    
    print("\n" + "=" * 60)
    print("✓ Log file created successfully!")
    print("=" * 60)
    print(f"\nTo view the logs:")
    print(f"  logxpy-view {log_file}")
    print(f"\nTo view only entries with timing data:")
    print(f"  logxpy-view --select 'contains(keys(@), `duration`)' {log_file}")
    print(f"\nTo view with minimal output:")
    print(f"  logxpy-view --field-limit 50 {log_file}")


if __name__ == "__main__":
    main()
