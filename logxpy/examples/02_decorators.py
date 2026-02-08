"""
02_decorators.py - Using decorators for automatic logging

Demonstrates:
- @log.logged: Entry, exit, args, result
- @log.timed: Timing execution
- @log.retry: Automatic retries
"""
from pathlib import Path
import time
import random
from logxpy import log, to_file

LOG_FILE = Path(__file__).with_suffix(".log")
to_file(open(LOG_FILE, "w"))

# 1. @log.logged - The all-in-one decorator
# Captures entry arguments, exit result, and execution time
@log.logged
def calculate_sum(a, b):
    time.sleep(0.1)
    return a + b

# Configure what to capture
@log.logged(capture_args=True, capture_result=False, level="INFO")
def sensitive_operation(password):
    time.sleep(0.1)
    return "token-123"

# 2. @log.timed - Just timing
@log.timed(metric="process_duration")
def long_process():
    time.sleep(0.2)

# 3. @log.retry - Automatic retries with logging
@log.retry(attempts=3, delay=0.1, on_retry=lambda n, e: log.warning(f"Retry {n}: {e}"))
def unstable_network_call():
    if random.random() < 0.7:
        raise ConnectionError("Network flaked")
    return "Connected"

def main():
    print("--- 1. @log.logged ---")
    calculate_sum(10, 20)
    
    print("\n--- 2. Configured @log.logged ---")
    sensitive_operation("secret123")
    
    print("\n--- 3. @log.timed ---")
    long_process()
    
    print("\n--- 4. @log.retry ---")
    try:
        result = unstable_network_call()
        log.success("Network call succeeded", result=result)
    except Exception as e:
        log.error("Network call failed permanently", error=str(e))

if __name__ == "__main__":
    main()
