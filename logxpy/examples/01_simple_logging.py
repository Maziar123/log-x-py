"""01_simple_logging.py - Basic usage of LoggerX

Demonstrates:
- Importing the logger
- Basic logging methods (info, warn, error)
- Output to file
- Structured logging with key-value pairs
"""

from pathlib import Path
from logxpy import log, to_file

# Setup output to log file (delete old log first)
LOG_FILE = Path(__file__).with_suffix(".log")
if LOG_FILE.exists():
    LOG_FILE.unlink()
to_file(open(LOG_FILE, "w", encoding="utf-8"))


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

    print(f"Log written to: {LOG_FILE}")
    print(f"View with: logxpy-view {LOG_FILE}")


if __name__ == "__main__":
    main()
