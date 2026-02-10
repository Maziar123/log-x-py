#!/usr/bin/env python3
"""Optimize async logging for maximum speed.

This script tests various optimizations for high-throughput logging.
"""

from __future__ import annotations

import gc
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from logxpy import log, QueuePolicy, AsyncConfig, AsyncWriter
from logxpy.src._async_destinations import AsyncFileDestination


def test_optimization(name: str, batch_size: int, queue_size: int, num_messages: int = 10_000) -> dict:
    """Test a specific optimization configuration."""
    log_file = f"opt_test_{name}.log"
    if os.path.exists(log_file):
        os.remove(log_file)

    # Configure with optimization
    log.init(
        log_file,
        async_enabled=True,
        async_max_queue=queue_size,
        async_batch_size=batch_size,
        async_flush_interval=0.5,  # Longer interval to allow batching
        async_policy="block",
    )

    # Pre-warm
    log.info("warmup")
    time.sleep(0.01)

    # Force GC before test
    gc.collect()

    # Benchmark
    start = time.perf_counter()
    for i in range(num_messages):
        log.info(f"Msg", i=i)
    enqueue_time = time.perf_counter() - start

    # Get immediate metrics
    metrics = log.get_async_metrics()
    pending = metrics['pending']

    # Wait for complete flush
    log.shutdown_async()

    # Verify
    with open(log_file) as f:
        lines = sum(1 for _ in f)

    # Cleanup
    os.remove(log_file)

    return {
        "name": name,
        "batch_size": batch_size,
        "queue_size": queue_size,
        "enqueue_time": enqueue_time,
        "throughput": num_messages / enqueue_time,
        "latency_ms": (enqueue_time / num_messages) * 1000,
        "pending_after_enqueue": pending,
        "lines_written": lines,
    }


def main():
    print("=" * 70)
    print("  ASYNC LOGGING OPTIMIZATION")
    print("  Testing configurations for maximum throughput")
    print("=" * 70)

    tests = [
        ("default", 100, 10_000),
        ("large_batch", 500, 10_000),
        ("xlarge_batch", 1000, 10_000),
        ("small_batch", 10, 10_000),
        ("huge_queue", 500, 100_000),
        ("drop_policy", 500, 1000),  # Small queue with drop
    ]

    results = []
    for name, batch_size, queue_size in tests:
        print(f"\n🧪 Testing: {name} (batch={batch_size}, queue={queue_size})")
        result = test_optimization(name, batch_size, queue_size)
        results.append(result)
        print(f"  Throughput: {result['throughput']:,.0f} msg/sec")
        print(f"  Latency: {result['latency_ms']:.4f} ms/msg")

    # Summary
    print("\n" + "=" * 70)
    print("  OPTIMIZATION SUMMARY")
    print("=" * 70)
    print(f"{'Config':<20} {'Batch':>8} {'Throughput':>15} {'Latency':>12}")
    print("-" * 70)

    for r in sorted(results, key=lambda x: x['throughput'], reverse=True):
        print(f"{r['name']:<20} {r['batch_size']:>8} {r['throughput']:>15,.0f} {r['latency_ms']:>12.4f}")

    best = max(results, key=lambda x: x['throughput'])
    print("\n🏆 Best configuration:")
    print(f"  Name: {best['name']}")
    print(f"  Batch size: {best['batch_size']}")
    print(f"  Queue size: {best['queue_size']}")
    print(f"  Throughput: {best['throughput']:,.0f} msg/sec")

    # Recommendations
    print("\n📋 Recommendations:")
    print("  1. Use batch_size=500-1000 for maximum throughput")
    print("  2. Use queue_size >= 10x batch_size to avoid blocking")
    print("  3. Use drop_oldest policy if latest data is most important")
    print("  4. Increase flush_interval for better batching")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
