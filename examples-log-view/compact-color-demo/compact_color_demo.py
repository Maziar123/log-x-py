#!/usr/bin/env python3
"""Compact demo - ONE yellow, ONE cyan, deep func nesting + decorators."""
import sys
from datetime import datetime
from enum import Enum, auto
sys.path.insert(0, "../../logxpy")
from logxpy import log, to_file, start_action
from logxpy.decorators import logged

class Status(Enum):
    ACTIVE = auto()

# ============ DECORATED FUNCTIONS ============

@logged(level="INFO", capture_args=True, capture_result=True)
def process_item(item_id: int, name: str) -> dict:
    """Process item - auto-logged by @logged."""
    log.info("Processing", item_id=item_id, name=name)
    return {"id": item_id, "status": "processed"}

@logged(level="DEBUG", capture_args=True, timer=True)
def validate_email(email: str) -> bool:
    """Validate email - auto-logged by @logged."""
    is_valid = "@" in email and "." in email
    return is_valid

@logged(level="INFO", capture_args=True, capture_result=True, timer=True)
def calculate_total(items: list) -> float:
    """Calculate total - auto-logged by @logged with timing."""
    total = sum(items)
    return total

def risky_operation():
    """Function that fails - for stack trace demo."""
    raise ValueError("Simulated failure in risky_operation")

# Setup
to_file(open("compact_color.log", "w"))

# ============ YELLOW BLOCK ============
log.set_background("yellow").set_foreground("black")
log.info("╔════════════════════════════════╗\n"
         "║  🚀 APP START                  ║\n"
         "╚════════════════════════════════╝")
log.reset_background().reset_foreground()

# Level 1: Main
with start_action(action_type="app:main"):
    
    # Level 2: System
    with start_action(action_type="system:init"):
        log.system_info()
        log.memory_status()
        log.checkpoint("Ready")
    
    # Level 2: Database
    with start_action(action_type="db:connect"):
        log.info("Postgres", host="localhost")
        with start_action(action_type="db:pool"):
            log.info("Pool", size=10)
    
    # Level 2: API Server
    with start_action(action_type="api:server"):
        log.info("HTTP", port=8080)
        with start_action(action_type="api:routes"):
            log.info("Routes", count=5)
            with start_action(action_type="api:middleware"):
                log.info("Middleware: auth, cors")
    
    # ============ DECORATOR DEMOS ============
    with start_action(action_type="decorator:demo"):
        log.info("Testing @logged decorator")
        
        # @logged - auto logs entry/exit with args/result/timing
        result1 = process_item(101, "Widget")
        valid = validate_email("user@example.com")
        total = calculate_total([19.99, 29.99, 5.00])
        
        log.success("Decorators done", items=1, emails=1, total=total)
    
    # ============ CYAN BLOCK ============
    with start_action(action_type="app:critical"):
        log.set_background("cyan")
        log.info("╔════════════════════════════════╗\n"
                 "║  🔒 CRITICAL SECTION           ║\n"
                 "╚════════════════════════════════╝")
        log.reset_background()
        
        # Level 3: Payment
        with start_action(action_type="payment:charge"):
            log.info("Charging", amount="99.99")
            
            with start_action(action_type="payment:validate"):
                log.info("Card check")
                log.color((255, 128, 0), "Risk")
            
            with start_action(action_type="payment:fraud"):
                log.info("Risk", score=15)
            
            log.success("Captured", id="txn_123")
        
        log.set_background("cyan")
        log.success("✓ Critical done")
        log.reset_background()
    
    # Level 2: Data processing
    with start_action(action_type="data:batch"):
        log.info("Batch", records=1000)
        
        with start_action(action_type="data:transform"):
            log.info("Transforming")
            with start_action(action_type="data:validate"):
                log.info("Schema")
                log.enum(Status.ACTIVE)
        
        log.success("Batch done")
    
    # ============ STACK TRACE DEMO ============
    with start_action(action_type="error:test"):
        log.info("Testing error + stack_trace()")
        try:
            with start_action(action_type="risky:op"):
                log.info("About to fail")
                risky_operation()
        except ValueError:
            log.error("Failed", error="ValueError")
            log.stack_trace(limit=5)
    
    # Level 2: Cleanup
    with start_action(action_type="app:cleanup"):
        log.info("Closing")
        log.datetime(datetime.now())
        log.success("Clean")

# Final checkpoint
log.checkpoint("🏁 Shutdown")

print("✓ Log created: compact_color.log")
