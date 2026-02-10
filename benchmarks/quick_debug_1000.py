#!/usr/bin/env python3
"""Quick debug and trace for 1000 log.info calls.

Simple script to test async logging performance.
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from logxpy import log


def main():
    print("=" * 50)
    print("Quick Debug: 1000 log.info() calls")
    print("=" * 50)

    # Initialize async logging
    log.init(
        "quick_debug.log",
        async_enabled=True,
        async_batch_size=100,
    )

    print(f"\nAsync enabled: {log.is_async}")
    print(f"Batch size: 100")

    # Test 1: Time 1000 log calls
    print("\n[Test 1] Timing 1000 log.info() calls...")
    
    start = time.perf_counter()
    for i in range(1000):
        log.info(f"Debug message", index=i)
    elapsed = time.perf_counter() - start

    print(f"  Enqueue time: {elapsed:.4f}s")
    print(f"  Throughput: {1000/elapsed:,.0f} calls/sec")
    print(f"  Per-call: {(elapsed/1000)*1000:.4f} ms")

    # Check metrics
    metrics = log.get_async_metrics()
    print(f"\n  Enqueued: {metrics['enqueued']}")
    print(f"  Written: {metrics['written']}")
    print(f"  Pending: {metrics['pending']}")

    # Wait for flush
    print("\nWaiting for flush...")
    time.sleep(0.2)
    
    final = log.get_async_metrics()
    print(f"  Written after flush: {final['written']}")

    # Shutdown
    log.shutdown_async()

    # Verify file
    with open("quick_debug.log") as f:
        lines = sum(1 for _ in f)
    print(f"  File lines: {lines}")

    # Cleanup
    import os
    os.remove("quick_debug.log")

    print("\n✅ Debug complete!")


if __name__ == "__main__":
    main()
