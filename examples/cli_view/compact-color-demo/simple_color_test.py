#!/usr/bin/env python3
"""Simple color demo - TWO colored blocks without @logged decorator."""
import sys
from datetime import datetime
from logxpy import log, to_file, start_action

# Setup
to_file(open("simple_color.log", "w"))

# ============ YELLOW BLOCK ============
log.set_background("yellow").set_foreground("black")
log.info("╔════════════════════════════════╗")
log.info("║  🚀 APP START                  ║")
log.info("╚════════════════════════════════╝")
log.reset_background().reset_foreground()

# Level 1: Main
with start_action(action_type="app:main"):
    log.info("Application started")

    # Level 2: Yellow block section
    with start_action(action_type="app:processing"):
        log.set_background("cyan")
        log.info("╔════════════════════════════════╗")
        log.info("║  🔒 CRITICAL SECTION           ║")
        log.info("╚════════════════════════════════╝")
        log.reset_background()

        log.success("Critical operations completed")

# Another yellow block
log.set_background("yellow").set_foreground("black")
log.info("╔════════════════════════════════╗")
log.info("║  ✅ SUCCESS BLOCK               ║")
log.info("╚════════════════════════════════╝")
log.reset_background().reset_foreground()

log.info("Done!")

print("✓ Log created: simple_color.log")
