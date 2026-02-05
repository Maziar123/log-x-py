"""
10_advanced_patterns.py - Advanced usage patterns

Demonstrates:
- Conditional logging with @log.logged(when=...)
- Custom log levels (via generic log method)
- Mixing sync and async contexts
"""

import asyncio
import sys

from logxpy import log, to_file

to_file(sys.stdout)


# 1. Conditional Logging
# Only log if amount > 1000
@log.logged(when=lambda func, args, kwargs: args[0] > 1000)
def process_transaction(amount, currency="USD"):
    return f"Processed {amount} {currency}"


# 2. Custom/Dynamic Action Levels
async def dynamic_level_task(importance):
    # Use dynamic level based on input
    lvl = "CRITICAL" if importance > 9 else "INFO"
    with log.scope(importance=importance, level=lvl):
        log.info("Starting task")
        if importance > 9:
            log.critical("High importance task!")
        else:
            log.info("Normal task")


def main():
    print("--- 1. Conditional Logging ---")
    print("Small transaction (should not log):")
    process_transaction(50)

    print("\nLarge transaction (should log):")
    process_transaction(5000)

    print("\n--- 2. Dynamic Logic ---")
    asyncio.run(dynamic_level_task(5))
    asyncio.run(dynamic_level_task(10))


if __name__ == "__main__":
    main()
