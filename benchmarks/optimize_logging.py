#!/usr/bin/env python3
"""Optimize async logging for maximum speed.

This script tests various optimizations for high-throughput logging.
Updated for choose-L2 based writer.
"""

from __future__ import annotations

import gc
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from logxpy import log, Mode, WriterType


def test_optimization(name: str, batch_size: int, queue_size: int, writer_type: str = "block", num_messages: int = 10_000) -> dict:
    """Test a specific optimization configuration."""
    log_file = f"opt_test_{name}.log"
    if os.path.exists(log_file):
        os.remove(log_file)

    # Configure with optimization using new API
    log.init(
        log_file,
        async_en=True,
        writer_type=writer_type,
        writer_mode="trigger",
        queue=queue_size,
        size=batch_size,
        flush=0.5,  # Longer interval to allow batching
        policy="block",
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
        "writer_type": writer_type,
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
    print("  Using choose-L2 based writer")
    print("=" * 70)

    tests = [
        ("default_block", 100, 10_000, "block"),
        ("large_batch_block", 500, 10_000, "block"),
        ("xlarge_batch_block", 1000, 10_000, "block"),
        ("small_batch_block", 10, 10_000, "block"),
        ("huge_queue_block", 500, 100_000, "block"),
        ("default_line", 100, 10_000, "line"),
        ("large_batch_line", 500, 10_000, "line"),
        ("default_mmap", 100, 10_000, "mmap"),
        ("large_batch_mmap", 500, 10_000, "mmap"),
    ]

    results = []
    for name, batch_size, queue_size, writer_type in tests:
        print(f"\n🧪 Testing: {name} (type={writer_type}, batch={batch_size}, queue={queue_size})")
        result = test_optimization(name, batch_size, queue_size, writer_type)
        results.append(result)
        print(f"  Throughput: {result['throughput']:,.0f} msg/sec")
        print(f"  Latency: {result['latency_ms']:.4f} ms/msg")

    # Summary
    print("\n" + "=" * 70)
    print("  OPTIMIZATION SUMMARY")
    print("=" * 70)
    print(f"{'Config':<25} {'Type':<8} {'Batch':>8} {'Throughput':>15} {'Latency':>12}")
    print("-" * 70)

    for r in sorted(results, key=lambda x: x['throughput'], reverse=True):
        print(f"{r['name']:<25} {r['writer_type']:<8} {r['batch_size']:>8} {r['throughput']:>15,.0f} {r['latency_ms']:>12.4f}")

    best = max(results, key=lambda x: x['throughput'])
    print("\n🏆 Best configuration:")
    print(f"  Name: {best['name']}")
    print(f"  Writer type: {best['writer_type']}")
    print(f"  Batch size: {best['batch_size']}")
    print(f"  Queue size: {best['queue_size']}")
    print(f"  Throughput: {best['throughput']:,.0f} msg/sec")

    # Recommendations
    print("\n📋 Recommendations:")
    print("  1. Use writer_type='block' for balanced performance (default)")
    print("  2. Use writer_type='line' for immediate durability")
    print("  3. Use writer_type='mmap' for maximum throughput")
    print("  4. Use batch_size=500-1000 for high throughput")
    print("  5. Use queue_size >= 10x batch_size to avoid blocking")
    print("  6. Use writer_mode='trigger' for event-driven (default)")
    print("  7. Use writer_mode='loop' for periodic polling")
    print("  8. Use writer_mode='manual' for explicit control")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
