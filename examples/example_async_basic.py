#!/usr/bin/env python3
"""Basic async logging example - async is ON by default.

This example demonstrates the default async behavior in logxpy.
No special configuration needed - just call log.init() and start logging!

Updated for choose-L2 based writer.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logxpy import log


def main() -> None:
    """Run the basic async logging example."""
    # Async is enabled by default - no special setup required!
    # Using block writer (64KB buffer) with trigger mode
    log.init("example_async_basic.log")

    # These log calls return immediately (non-blocking)
    log.info("Application started")
    log.debug("Debug information", value=42)

    # Log many messages quickly - they'll be batched in the background
    for i in range(1000):
        log.info("Processing item", index=i)

    log.success("Processing complete", total=1000)

    # Check async status
    print(f"Async enabled: {log.is_async}")
    print(f"Metrics: {log.get_async_metrics()}")

    # Graceful shutdown (optional - automatically called at exit)
    log.shutdown_async()

    print("Done! Check example_async_basic.log for output.")


if __name__ == "__main__":
    main()
