#!/usr/bin/env python3
"""Benchmark: Debug, trace, and monitor 1000 log.info calls.

This script provides detailed performance analysis of async logging:
- Execution time breakdown
- Throughput metrics
- Queue behavior monitoring
- Memory usage tracking
- File output verification
"""

from __future__ import annotations

import gc
import os
import sys
import time
import tracemalloc
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from logxpy import log, QueuePolicy


class PerformanceMonitor:
    """Monitor and report performance metrics."""

    def __init__(self):
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.peak_memory: int = 0
        self.metrics: dict = {}

    def start(self) -> None:
        """Start monitoring."""
        gc.collect()  # Clean up before measurement
        tracemalloc.start()
        self.start_time = time.perf_counter()

    def stop(self) -> None:
        """Stop monitoring."""
        self.end_time = time.perf_counter()
        current, self.peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        return self.end_time - self.start_time

    @property
    def throughput(self) -> float:
        """Calculate throughput (logs/sec)."""
        if self.elapsed <= 0:
            return 0.0
        return 1000.0 / self.elapsed

    def report(self, title: str = "Performance Report") -> None:
        """Print performance report."""
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}")
        print(f"  Total Time:     {self.elapsed:.4f} seconds")
        print(f"  Throughput:     {self.throughput:,.0f} logs/second")
        print(f"  Avg Latency:    {(self.elapsed / 1000) * 1000:.4f} ms/log")
        print(f"  Peak Memory:    {self.peak_memory / 1024:.2f} KB")
        print(f"{'=' * 60}\n")


def benchmark_async_mode() -> dict:
    """Benchmark async logging mode.

    Returns:
        Dictionary with performance metrics.
    """
    print("\n🔥 BENCHMARK: Async Mode (1000 log.info calls)")
    print("-" * 60)

    # Setup
    log_file = "bench_async_1000.log"
    if os.path.exists(log_file):
        os.remove(log_file)

    # Initialize with async enabled (default)
    log.init(
        log_file,
        async_enabled=True,
        async_max_queue=10_000,
        async_batch_size=100,
        async_flush_interval=0.1,
        async_policy="block",
    )

    print(f"Async enabled: {log.is_async}")
    print(f"Queue size: 10,000")
    print(f"Batch size: 100")
    print(f"Policy: BLOCK")
    print("-" * 60)

    # Pre-warm
    log.info("Warmup message")
    time.sleep(0.05)

    # Get initial metrics
    initial_metrics = log.get_async_metrics()
    print(f"Initial metrics: {initial_metrics}")

    # Start monitoring
    monitor = PerformanceMonitor()
    monitor.start()

    # Execute 1000 log calls
    for i in range(1000):
        log.info(f"Test log message", index=i, timestamp=time.time())

    # Stop timing (enqueue complete)
    monitor.stop()

    # Get metrics immediately after enqueue
    post_enqueue_metrics = log.get_async_metrics()

    # Wait for writer to flush
    print("Waiting for async writer to flush...")
    time.sleep(0.3)

    # Get final metrics
    final_metrics = log.get_async_metrics()

    # Shutdown and verify file
    log.shutdown_async()

    # Verify file contents
    line_count = 0
    if os.path.exists(log_file):
        with open(log_file) as f:
            line_count = sum(1 for _ in f)

    # Report
    monitor.report("Async Mode Results")

    print(f"Enqueued:     {post_enqueue_metrics['enqueued']}")
    print(f"Written:      {final_metrics['written']}")
    print(f"Pending:      {post_enqueue_metrics['pending']}")
    print(f"Dropped:      {final_metrics['dropped']}")
    print(f"File lines:   {line_count}")

    # Cleanup
    if os.path.exists(log_file):
        os.remove(log_file)

    return {
        "mode": "async",
        "elapsed": monitor.elapsed,
        "throughput": monitor.throughput,
        "peak_memory_kb": monitor.peak_memory / 1024,
        "lines_written": line_count,
    }


def benchmark_sync_mode() -> dict:
    """Benchmark sync logging mode.

    Returns:
        Dictionary with performance metrics.
    """
    print("\n🔥 BENCHMARK: Sync Mode (1000 log.info calls)")
    print("-" * 60)

    # Setup
    log_file = "bench_sync_1000.log"
    if os.path.exists(log_file):
        os.remove(log_file)

    # Initialize with async disabled
    log.init(log_file, async_enabled=False)

    print(f"Async enabled: {log.is_async}")
    print("-" * 60)

    # Pre-warm
    log.info("Warmup message")

    # Start monitoring
    monitor = PerformanceMonitor()
    monitor.start()

    # Execute 1000 log calls
    for i in range(1000):
        log.info(f"Test log message", index=i, timestamp=time.time())

    # Stop timing
    monitor.stop()

    # Verify file contents
    line_count = 0
    if os.path.exists(log_file):
        with open(log_file) as f:
            line_count = sum(1 for _ in f)

    # Report
    monitor.report("Sync Mode Results")
    print(f"File lines: {line_count}")

    # Cleanup
    if os.path.exists(log_file):
        os.remove(log_file)

    return {
        "mode": "sync",
        "elapsed": monitor.elapsed,
        "throughput": monitor.throughput,
        "peak_memory_kb": monitor.peak_memory / 1024,
        "lines_written": line_count,
    }


def benchmark_with_backpressure() -> dict:
    """Benchmark with different backpressure policies.

    Returns:
        Dictionary with performance metrics.
    """
    print("\n🔥 BENCHMARK: Backpressure Policies (1000 calls each)")
    print("-" * 60)

    results = {}

    for policy in [QueuePolicy.BLOCK, QueuePolicy.DROP_OLDEST, QueuePolicy.DROP_NEWEST]:
        log_file = f"bench_{policy}.log"
        if os.path.exists(log_file):
            os.remove(log_file)

        print(f"\nTesting policy: {policy}")

        # Use small queue to trigger backpressure
        log.init(
            log_file,
            async_enabled=True,
            async_max_queue=100,  # Small queue
            async_batch_size=50,
            async_policy=str(policy),
        )

        start = time.perf_counter()
        for i in range(1000):
            log.info(f"Test message", index=i)
        elapsed = time.perf_counter() - start

        # Wait and get metrics
        time.sleep(0.3)
        metrics = log.get_async_metrics()
        log.shutdown_async()

        print(f"  Enqueue time: {elapsed:.4f}s")
        print(f"  Enqueued: {metrics['enqueued']}")
        print(f"  Written: {metrics['written']}")
        print(f"  Dropped: {metrics['dropped']}")

        results[str(policy)] = {
            "elapsed": elapsed,
            "enqueued": metrics['enqueued'],
            "written": metrics['written'],
            "dropped": metrics['dropped'],
        }

        # Cleanup
        if os.path.exists(log_file):
            os.remove(log_file)

    return results


def trace_execution() -> None:
    """Trace detailed execution of log calls."""
    print("\n🔍 TRACE: Detailed Execution Analysis")
    print("-" * 60)

    log_file = "trace_debug.log"
    if os.path.exists(log_file):
        os.remove(log_file)

    log.init(log_file, async_enabled=True)

    # Trace first 10 calls in detail
    print("\nTracing first 10 log calls:")
    print("-" * 40)

    for i in range(10):
        t0 = time.perf_counter()
        log.info(f"Trace message {i}", trace_id=i)
        t1 = time.perf_counter()

        metrics = log.get_async_metrics()
        print(f"Call {i}: enqueue_time={(t1-t0)*1000:.4f}ms, "
              f"enqueued={metrics['enqueued']}, "
              f"pending={metrics['pending']}")

    # Wait for flush
    time.sleep(0.2)
    final_metrics = log.get_async_metrics()
    print(f"\nFinal: written={final_metrics['written']}")

    log.shutdown_async()

    # Cleanup
    if os.path.exists(log_file):
        os.remove(log_file)


def compare_batch_sizes() -> None:
    """Compare performance with different batch sizes."""
    print("\n📊 COMPARISON: Batch Sizes (1000 calls each)")
    print("-" * 60)

    batch_sizes = [1, 10, 50, 100, 500]
    results = []

    for batch_size in batch_sizes:
        log_file = f"bench_batch_{batch_size}.log"
        if os.path.exists(log_file):
            os.remove(log_file)

        log.init(
            log_file,
            async_enabled=True,
            async_batch_size=batch_size,
            async_flush_interval=1.0,  # Long interval to test batching
        )

        # Pre-warm
        log.info("warmup")
        time.sleep(0.05)

        start = time.perf_counter()
        for i in range(1000):
            log.info(f"Test", index=i)
        elapsed = time.perf_counter() - start

        # Force flush by shutting down
        log.shutdown_async()

        results.append((batch_size, elapsed))
        print(f"Batch size {batch_size:4d}: {elapsed:.4f}s ({1000/elapsed:,.0f} logs/sec)")

        # Cleanup
        if os.path.exists(log_file):
            os.remove(log_file)

    print(f"\nBest throughput: {max(results, key=lambda x: 1000/x[1])}")


def main() -> None:
    """Run all benchmarks."""
    print("\n" + "=" * 60)
    print("  ASYNC LOGGING PERFORMANCE BENCHMARK")
    print("  1000 log.info() calls - Debug, Trace & Monitor")
    print("=" * 60)

    # Run benchmarks
    async_results = benchmark_async_mode()
    sync_results = benchmark_sync_mode()

    # Compare
    print("\n📈 COMPARISON: Async vs Sync")
    print("-" * 60)
    print(f"Async throughput: {async_results['throughput']:,.0f} logs/sec")
    print(f"Sync throughput:  {sync_results['throughput']:,.0f} logs/sec")

    if async_results['throughput'] > sync_results['throughput']:
        speedup = async_results['throughput'] / sync_results['throughput']
        print(f"Speedup: {speedup:.1f}x faster (async)")
    else:
        slowdown = sync_results['throughput'] / async_results['throughput']
        print(f"Slowdown: {slowdown:.1f}x slower (async)")

    print(f"\nMemory usage:")
    print(f"  Async: {async_results['peak_memory_kb']:.2f} KB")
    print(f"  Sync:  {sync_results['peak_memory_kb']:.2f} KB")

    # Additional tests
    trace_execution()
    compare_batch_sizes()
    benchmark_with_backpressure()

    print("\n" + "=" * 60)
    print("  BENCHMARK COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
