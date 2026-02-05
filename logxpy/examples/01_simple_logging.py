"""
01_simple_logging.py - Basic usage of LoggerX

Demonstrates:
- Importing the logger
- Basic logging methods (info, warn, error)
- Output to stdout
- Structured logging with key-value pairs
"""
import sys
from logxpy import log, to_file

# 1. Setup output to stdout (console)
to_file(sys.stdout)

def main():
    print("--- 1. Basic Messages ---")
    log.info("Hello, World!")
    log.warning("This is a warning")
    
    # 2. Structured Logging
    print("\n--- 2. Structured Data ---")
    # Instead of f-strings, pass kwargs for structured data
    log.info("User logged in", user_id=123, username="alice")
    log.success("Database connected", host="localhost", port=5432)
    
    # 3. Different Levels
    print("\n--- 3. Log Levels ---")
    log.debug("Debug message (hidden by default if level is INFO)")
    log.info("Info message")
    log.note("Note message")
    log.success("Success message")
    log.warning("Warning message")
    log.error("Error message")
    log.critical("Critical message")
    
    # 4. Fluent Interface
    print("\n--- 4. Fluent Interface ---")
    log.info("Starting task").checkpoint("Step 1 done").success("Task complete")

if __name__ == "__main__":
    main()
