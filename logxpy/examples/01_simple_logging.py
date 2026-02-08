"""
01_simple_logging.py - Basic usage of LoggerX

Demonstrates:
- Importing the logger
- Basic logging methods (info, warn, error)
- Output to file
- Structured logging with key-value pairs
"""
from pathlib import Path
from logxpy import log, to_file

# Setup output to log file
LOG_FILE = Path(__file__).with_suffix(".log")
to_file(open(LOG_FILE, "w"))

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
