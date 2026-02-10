#!/usr/bin/env python3
"""
Tutorial 02: Actions and Context Management
============================================

This tutorial demonstrates:
- Actions (start_action) - grouped, nested operations
- Context managers (with log.action())
- Nested actions
- Action success/failure states
- Duration tracking

Run this script to generate: tutorial_02_actions.log
Then view with: logxpy-view tutorial_02_actions.log
"""

import time
from pathlib import Path
from _setup_imports import log, to_file, start_action


def setup_logging():
    """Configure logging to write to a file."""
    log_file = Path(__file__).parent / "tutorial_02_actions.log"
    to_file(open(log_file, "w"))
    print(f"✓ Logging to: {log_file}")
    return log_file


def demo_simple_action():
    """Demonstrate a simple action."""
    with start_action(action_type="user:login", user="alice123"):
        log.info("Validating credentials", method="password")
        time.sleep(0.1)
        log.info("Checking user permissions")
        time.sleep(0.05)
        log.success("User logged in successfully", session_id="sess_abc123")


def demo_nested_actions():
    """Demonstrate nested actions."""
    with start_action(action_type="order:process", order_id="ORD-12345"):
        log.info("Order received", total_amount=99.99, items=3)
        
        # Nested action: payment
        with start_action(action_type="payment:process", payment_method="credit_card"):
            log.info("Contacting payment gateway", gateway="stripe")
            time.sleep(0.1)
            log.info("Charging card", amount=99.99, last_four="4242")
            time.sleep(0.1)
            log.success("Payment authorized", transaction_id="txn_abc123")
        
        # Nested action: inventory
        with start_action(action_type="inventory:reserve", warehouse="WH-01"):
            log.info("Checking stock levels")
            time.sleep(0.05)
            log.info("Reserving items", item_ids=["ITEM-001", "ITEM-002", "ITEM-003"])
            time.sleep(0.05)
            log.success("Items reserved", reservation_id="res_xyz789")
        
        # Nested action: shipping
        with start_action(action_type="shipping:prepare", carrier="FedEx"):
            log.info("Generating shipping label")
            time.sleep(0.08)
            log.info("Printing label", printer="LabelPrinter-01")
            time.sleep(0.05)
            log.success("Label created", tracking_number="1Z999AA10123456784")
        
        log.success("Order processed successfully", 
                   order_id="ORD-12345",
                   estimated_delivery="2026-02-08")


def demo_failed_action():
    """Demonstrate action with failure."""
    try:
        with start_action(action_type="database:backup", database="production"):
            log.info("Starting backup", target="/backups/2026-02-05")
            time.sleep(0.1)
            log.info("Copying database files", size_gb=150)
            time.sleep(0.1)
            # Simulate failure
            raise IOError("Disk full: cannot write backup file")
    except IOError as e:
        log.error("Backup failed", error=str(e), disk_space_available="0GB")


def demo_mixed_success_failure():
    """Demonstrate mixed success and failure scenarios."""
    with start_action(action_type="batch:process_users", batch_size=100):
        log.info("Processing user batch")
        
        # Successful user processing
        for user_id in range(1, 4):
            with start_action(action_type="user:process", user_id=user_id):
                log.info("Fetching user data")
                time.sleep(0.03)
                log.info("Updating user profile")
                time.sleep(0.02)
                log.success("User processed", user_id=user_id)
        
        # Failed user processing
        try:
            with start_action(action_type="user:process", user_id=4):
                log.info("Fetching user data")
                time.sleep(0.03)
                log.warning("User data incomplete", missing_fields=["email", "phone"])
                raise ValueError("Required fields missing")
        except ValueError:
            log.error("User processing failed", user_id=4)
        
        # More successful processing
        for user_id in range(5, 7):
            with start_action(action_type="user:process", user_id=user_id):
                log.info("Fetching user data")
                time.sleep(0.03)
                log.success("User processed", user_id=user_id)
        
        log.success("Batch completed", 
                   total=6,
                   successful=5,
                   failed=1)


def demo_parallel_actions():
    """Demonstrate simulated parallel actions."""
    with start_action(action_type="report:generate", report_type="monthly_sales"):
        log.info("Starting report generation", month="February", year=2026)
        
        # Multiple data sources processed "in parallel"
        with start_action(action_type="data:fetch", source="database"):
            log.info("Querying sales data", table="orders")
            time.sleep(0.08)
            log.success("Fetched records", count=15234)
        
        with start_action(action_type="data:fetch", source="api"):
            log.info("Fetching external data", api="analytics-service")
            time.sleep(0.12)
            log.success("Fetched metrics", metrics=["conversion_rate", "avg_order_value"])
        
        with start_action(action_type="data:fetch", source="cache"):
            log.info("Loading cached data", cache_key="monthly_aggregates")
            time.sleep(0.03)
            log.success("Cache hit", items=42)
        
        # Final processing
        with start_action(action_type="report:render", format="PDF"):
            log.info("Rendering charts and tables")
            time.sleep(0.1)
            log.success("Report generated", 
                       file="monthly_sales_202602.pdf",
                       pages=23)


def main():
    """Run all demonstrations."""
    log_file = setup_logging()
    
    print("\n" + "=" * 60)
    print("Tutorial 02: Actions and Context")
    print("=" * 60)
    
    print("\n1. Simple Action")
    demo_simple_action()
    
    print("\n2. Nested Actions")
    demo_nested_actions()
    
    print("\n3. Failed Action")
    demo_failed_action()
    
    print("\n4. Mixed Success/Failure")
    demo_mixed_success_failure()
    
    print("\n5. Parallel Actions")
    demo_parallel_actions()
    
    log.success("Tutorial completed!", tutorial="02_actions_and_context")
    
    print("\n" + "=" * 60)
    print("✓ Log file created successfully!")
    print("=" * 60)
    print(f"\nTo view the logs with tree structure:")
    print(f"  logxpy-view {log_file}")
    print(f"\nTo view only failed actions:")
    print(f"  logxpy-view --action-status failed {log_file}")
    print(f"\nTo view specific action type:")
    print(f"  logxpy-view --action-type 'order:process' {log_file}")
    print(f"\nTo view with timing information:")
    print(f"  logxpy-view --human-readable {log_file}")


if __name__ == "__main__":
    main()
