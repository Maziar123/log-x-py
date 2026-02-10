#!/usr/bin/env python3
"""Example 01: Basic Logging - simple messages with LoggerX."""

from logxpy import log

log.init()

log.info("Application started", version="1.0.0", environment="production")
log.info("Application ready")
log.info("User login", user_id=123, username="alice", ip="192.168.1.100")
log.info("Database connected", host="localhost", port=5432, status="connected")
log.warning("High memory usage", memory_percent=85)
log.success("Data processed", records=1000, duration_ms=234)

print("✓ Log created: example_01_basic.log")
