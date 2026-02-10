#!/usr/bin/env python3
"""Disable async logging example - synchronous mode.

This example shows how to disable async logging for synchronous
behavior, useful when you need guaranteed immediate writes.
"""

from logxpy import log


def main() -> None:
    """Run the sync logging example."""
    # Disable async by passing async_enabled=False
    log.init("example_async_disable.log", async_enabled=False)

    # These calls block until written to disk
    log.info("Synchronous log message")
    log.debug("Debug info", value=123)

    # Check async status
    print(f"Async enabled: {log.is_async}")  # Should be False

    # Or use environment variable: LOGXPY_SYNC=1 python example.py

    print("Done! Check example_async_disable.log for output.")


if __name__ == "__main__":
    main()
