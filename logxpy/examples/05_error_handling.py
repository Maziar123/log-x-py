"""
05_error_handling.py - Exception logging patterns

Demonstrates:
- log.exception(): Capturing tracebacks
- @log.logged: Auto-capturing exceptions
- silent_errors: Suppressing errors in logs
"""
from pathlib import Path
from logxpy import log, to_file

LOG_FILE = Path(__file__).with_suffix(".log")
to_file(open(LOG_FILE, "w"))

def risky_function():
    raise ValueError("Something went wrong!")

# 1. Automatic Capture
@log.logged
def protected_function():
    risky_function()

# 2. Silent Errors (logging the error but returning None)
@log.logged(silent_errors=True)
def suppressed_function():
    raise ConnectionError("Flaky connection")

def main():
    print("--- 1. Manual Exception Logging ---")
    try:
        risky_function()
    except Exception:
        # Logs the exception, type, and traceback
        log.exception("Caught an error manually")

    print("\n--- 2. Decorator Capture ---")
    try:
        protected_function()
    except ValueError:
        print("(Exception bubbled up as expected)")

    print("\n--- 3. Suppressed Errors ---")
    # This won't raise, just logs the failure in the action
    result = suppressed_function()
    print(f"Result was: {result}")

if __name__ == "__main__":
    main()
