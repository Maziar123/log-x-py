#!/usr/bin/env python3
"""
Tutorial 01: Basic Logging with logxpy
========================================

This tutorial demonstrates:
- Basic logging methods (info, warning, error, success)
- Structured logging with key-value pairs
- Different log levels
- Fluent interface (chaining)

Run this script to generate: tutorial_01_basic.log
Then view with: logxpy-tree2 tutorial_01_basic.log
"""

from pathlib import Path
from _setup_imports import log, to_file


def setup_logging():
    """Configure logging to write to a file."""
    log_file = Path(__file__).parent / "tutorial_01_basic.log"
    to_file(open(log_file, "w"))
    print(f"✓ Logging to: {log_file}")
    return log_file


def demo_basic_messages():
    """Demonstrate basic logging methods."""
    log.info("Application started", version="1.0.0", environment="development")
    log.debug("Debug information", memory_usage="45MB", cpu_usage="12%")
    log.success("Configuration loaded successfully", config_file="app.config")
    log.warning("High memory usage detected", threshold="80%", current="92%")
    log.error("Failed to connect to database", host="localhost", port=5432, retry_count=3)
    log.critical("System is out of memory!", available_memory="0MB")


def demo_structured_logging():
    """Demonstrate structured logging with rich data."""
    # User authentication scenario
    log.info("User login attempt", 
             user_id="alice123",
             ip_address="192.168.1.100",
             user_agent="Mozilla/5.0")
    
    log.success("User authenticated successfully",
                user_id="alice123",
                session_id="sess_abc123",
                roles=["admin", "user"])
    
    # File processing
    log.info("Processing file upload",
             filename="document.pdf",
             size_bytes=1024000,
             content_type="application/pdf")
    
    log.success("File uploaded successfully",
                filename="document.pdf",
                storage_path="/uploads/2026/02/document.pdf",
                processing_time_ms=234)


def demo_fluent_interface():
    """Demonstrate fluent/chaining interface."""
    # Chain multiple log calls
    log.info("Starting data pipeline") \
        .checkpoint("Loading data from source") \
        .checkpoint("Transforming data") \
        .checkpoint("Validating data") \
        .success("Pipeline completed successfully")
    
    # Another example
    log.info("Order processing started", order_id="ORD-12345") \
        .checkpoint("Payment verified") \
        .checkpoint("Inventory checked") \
        .checkpoint("Shipping label created") \
        .success("Order shipped", tracking_number="TRK-98765")


def main():
    """Run all demonstrations."""
    log_file = setup_logging()
    
    print("\n" + "=" * 60)
    print("Tutorial 01: Basic Logging")
    print("=" * 60)
    
    print("\n1. Basic Messages (info, warning, error, etc.)")
    demo_basic_messages()
    
    print("\n2. Structured Logging (key-value pairs)")
    demo_structured_logging()
    
    print("\n3. Fluent Interface (chaining)")
    demo_fluent_interface()
    
    log.success("Tutorial completed!", tutorial="01_basic_logging")
    
    print("\n" + "=" * 60)
    print("✓ Log file created successfully!")
    print("=" * 60)
    print(f"\nTo view the logs, run:")
    print(f"  logxpy-tree2 {log_file}")
    print(f"\nOr with colors disabled:")
    print(f"  logxpy-tree2 --color never {log_file}")
    print(f"\nOr filter by level:")
    print(f"  logxpy-tree2 --select 'level == `ERROR`' {log_file}")


if __name__ == "__main__":
    main()
