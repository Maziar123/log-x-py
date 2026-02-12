"""01_simple_logging.py - Basic usage of LoggerX

Demonstrates:
- Importing the logger
- Basic logging methods (info, warn, error)
- Output to file
- Structured logging with key-value pairs
"""

from logxpy import log

# Setup output - auto-generate log file from __file__, clean old if exists
# log.init(clean=True)
log.init("", size=0, flush="100µs", clean=True)


def main():
    # 1. Basic Messages
    log.info("Hello, World!")
    log.warning("This is a warning")

    # 2. Structured Logging
    log.info("User logged in", user_id=123, username="alice")
    log.success("Database connected", host="localhost", port=5432)

    # 3. Different Levels
    log.debug("Debug message")
    log.info("Info message")
    log.note("Note message")
    log.success("Success message")
    log.warning("Warning message")
    log.error("Error message")
    log.critical("Critical message")

    # 4. Fluent Interface
    log.info("Starting task").checkpoint("Step 1 done").success("Task complete")

    print(f"Log file: {log._auto_log_file}")
    print(f"View with: logxpy-view {log._auto_log_file}")


if __name__ == "__main__":
    main()
