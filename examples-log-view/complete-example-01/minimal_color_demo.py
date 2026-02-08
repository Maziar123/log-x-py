#!/usr/bin/env python3
"""Minimal logging demo - showcasing key logxpy features."""
import sys
from datetime import datetime
from enum import Enum, auto

sys.path.insert(0, "../../logxpy")
from logxpy import log, to_file, start_action

# Configuration
class Status(Enum):
    ACTIVE = auto()
    PENDING = auto()

# Setup
to_file(open("minimal_color.log", "w"))
log.system_info()
log.memory_status()

# Section 1: Basic Messages
log.info("App started", version="1.0.0", env="demo")
log.debug("Debug mode enabled")
log.checkpoint("Initialization complete")

# Section 2: Method Tracing with Actions
with start_action(action_type="user:login", user_id=42):
    log.info("Auth check", method="token")
    log.success("Login success", user="alice", roles=["admin", "user"])

# Section 3: Error Handling
try:
    with start_action(action_type="payment:process"):
        log.info("Processing", amount=99.99, currency="USD")
        raise ValueError("Invalid card")
except ValueError:
    log.error("Payment failed", code=500, retryable=True)
    log.stack_trace(limit=5)

# Section 4: Data Types
log.color((255, 128, 0), "Theme")
log.datetime(datetime.now(), "CurrentTime")
log.enum(Status.ACTIVE, "UserStatus")
log.currency("19.99", "USD", "ProductPrice")

# Section 5: Warnings
log.warning("Cache miss", key="user:123", latency_ms=45)

# Section 6: Color Features
log.set_foreground("cyan")
log.info("Processing completed", items=42)
log.reset_foreground()

log.set_foreground("white").set_background("red")
log.error("Critical validation failed")
log.reset_foreground().reset_background()

# Highlight block for critical alerts
log.colored(
    "╔════════════════════════════╗\n"
    "║  ⚠️  DEPLOYMENT BLOCKED   ║\n"
    "║  Review errors before prod ║\n"
    "╚════════════════════════════╝",
    foreground="black",
    background="yellow"
)

log.success("App shutdown gracefully", uptime_sec=45, peak_memory_mb=128)
print("✓ Log created: minimal_color.log")
