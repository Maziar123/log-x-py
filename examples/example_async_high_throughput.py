#!/usr/bin/env python3
"""High-throughput async logging example.

This example demonstrates tuning the async writer for maximum
throughput and using sync_mode() for critical sections.
"""

import time

from logxpy import QueuePolicy, log


def main() -> None:
    """Run the high-throughput example."""
    # Configure for maximum throughput
    log.init(
        "example_async_high_throughput.log",
        async_enabled=True,
        async_max_queue=50_000,        # Large queue to handle bursts
        async_batch_size=500,          # Larger batches = fewer syscalls
        async_flush_interval=0.5,      # Flush every 500ms
        async_policy="drop_oldest",    # Allow dropping old messages if needed
    )

    # High-volume logging
    start = time.perf_counter()
    for i in range(100_000):
        log.info("High volume message", index=i)
    elapsed = time.perf_counter() - start

    print(f"Logged 100,000 messages in {elapsed:.2f}s")
    print(f"Rate: {100_000 / elapsed:,.0f} messages/second")
    print(f"Metrics: {log.get_async_metrics()}")

    # Critical section - force synchronous logging
    with log.sync_mode():
        log.critical("Critical error - guaranteed to be written!")
        log.error("Error details", code=500)

    # Back to async
    log.info("Continuing with async logging")

    # Graceful shutdown
    log.shutdown_async()

    print("Done! Check example_async_high_throughput.log for output.")


if __name__ == "__main__":
    main()
