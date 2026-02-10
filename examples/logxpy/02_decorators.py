"""02_decorators.py - Using decorators for automatic logging

Demonstrates:
- @log.logged: Entry, exit, args, result
- @log.timed: Timing execution
- @log.retry: Automatic retries
"""

import time
import random
from logxpy import log

# Setup output - auto-generate log file from __file__, clean old if exists
log.init(clean=True)


# 1. @log.logged - The all-in-one decorator
@log.logged
def calculate_sum(a, b):
    time.sleep(0.1)
    return a + b


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
    # 1. @log.logged
    calculate_sum(10, 20)

    # 2. @log.timed
    long_process()

    # 3. @log.retry
    try:
        result = unstable_network_call()
        log.success("Network call succeeded", result=result)
    except ConnectionError as e:
        log.error("Network call failed permanently", error=str(e))

    print(f"Log file: {log._auto_log_file}")
    print(f"View with: logxpy-view {log._auto_log_file}")


if __name__ == "__main__":
    main()
