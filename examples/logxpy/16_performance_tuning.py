"""16_performance_tuning.py - Performance Configuration Guide

Demonstrates how to configure logxpy for different performance profiles:
- Maximum throughput (200K+ L/s)
- Minimum latency
- Balanced (default)
- Memory efficient
"""

import time
import os
from logxpy import log


def benchmark_config(name: str, config: dict, count: int = 10_000) -> dict:
    """Benchmark a configuration."""
    log_file = f"/tmp/perf_{name}.log"
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Apply config
    log.init(log_file, **config)
    
    # Warmup
    for i in range(100):
        log.info(f"warmup {i}")
    
    # Benchmark
    start = time.perf_counter()
    for i in range(count):
        log.info(f"Message {i}", idx=i)
    
    # Shutdown if async
    if config.get("async_en", True):
        log.shutdown_async()
    
    elapsed = time.perf_counter() - start
    
    # Count lines
    line_count = 0
    with open(log_file) as f:
        line_count = sum(1 for line in f if line.strip())
    
    os.remove(log_file)
    
    return {
        "name": name,
        "throughput": count / elapsed,
        "elapsed_ms": elapsed * 1000,
        "lines": line_count,
        "delivery": (line_count / count) * 100,
    }


def demo_max_throughput():
    """Configuration for maximum throughput."""
    print("\n" + "="*70)
    print("CONFIG 1: MAXIMUM THROUGHPUT")
    print("="*70)
    
    config = {
        "async_en": True,
        "writer_type": "block",      # 64KB buffer
        "writer_mode": "trigger",    # Event-driven
        "size": 500,                 # Large batches
        "queue": 50_000,             # Large queue
        "policy": "block",
    }
    
    print("\nConfiguration:")
    for k, v in config.items():
        print(f"  {k}: {v}")
    
    result = benchmark_config("max_throughput", config)
    
    print(f"\nResults:")
    print(f"  Throughput: {result['throughput']:,.0f} L/s")
    print(f"  Time: {result['elapsed_ms']:.1f}ms")
    print(f"  Delivery: {result['delivery']:.1f}%")
    
    print("\nUse case: High-volume logging, batch processing")


def demo_min_latency():
    """Configuration for minimum latency."""
    print("\n" + "="*70)
    print("CONFIG 2: MINIMUM LATENCY")
    print("="*70)
    
    config = {
        "async_en": False,           # Sync mode (immediate write)
        "writer_type": "line",       # Line buffered
        "writer_mode": "trigger",
        "size": 1,                   # Batch size 1
    }
    
    print("\nConfiguration:")
    for k, v in config.items():
        print(f"  {k}: {v}")
    
    result = benchmark_config("min_latency", config, count=1_000)
    
    print(f"\nResults:")
    print(f"  Throughput: {result['throughput']:,.0f} L/s")
    print(f"  Time: {result['elapsed_ms']:.1f}ms")
    print(f"  Latency: ~{result['elapsed_ms'] / 1000:.3f}ms per log")
    
    print("\nUse case: Real-time alerts, debugging")


def demo_balanced():
    """Balanced configuration (default)."""
    print("\n" + "="*70)
    print("CONFIG 3: BALANCED (DEFAULT)")
    print("="*70)
    
    config = {
        "async_en": True,
        "writer_type": "block",      # Block buffered (default)
        "writer_mode": "trigger",    # Trigger mode (default)
        "size": 100,                 # Default batch size
        "queue": 10_000,             # Default queue
    }
    
    print("\nConfiguration:")
    for k, v in config.items():
        print(f"  {k}: {v}")
    
    result = benchmark_config("balanced", config)
    
    print(f"\nResults:")
    print(f"  Throughput: {result['throughput']:,.0f} L/s")
    print(f"  Time: {result['elapsed_ms']:.1f}ms")
    print(f"  Delivery: {result['delivery']:.1f}%")
    
    print("\nUse case: General purpose logging")


def demo_memory_efficient():
    """Memory-efficient configuration."""
    print("\n" + "="*70)
    print("CONFIG 4: MEMORY EFFICIENT")
    print("="*70)
    
    config = {
        "async_en": True,
        "writer_type": "line",
        "writer_mode": "loop",
        "size": 50,
        "queue": 1_000,              # Small queue
        "flush": 0.01,               # Frequent flushes
        "policy": "drop_oldest",     # Drop old on overflow
    }
    
    print("\nConfiguration:")
    for k, v in config.items():
        print(f"  {k}: {v}")
    
    result = benchmark_config("memory_efficient", config)
    
    print(f"\nResults:")
    print(f"  Throughput: {result['throughput']:,.0f} L/s")
    print(f"  Time: {result['elapsed_ms']:.1f}ms")
    print(f"  Delivery: {result['delivery']:.1f}%")
    
    print("\nUse case: Memory-constrained environments")


def demo_comparison_table():
    """Compare all configurations."""
    print("\n" + "="*70)
    print("COMPARISON TABLE")
    print("="*70)
    
    configs = [
        ("Max Throughput", {"async_en": True, "writer_type": "block", "writer_mode": "trigger", "size": 500, "queue": 50_000}),
        ("Min Latency", {"async_en": False, "writer_type": "line", "size": 1}),
        ("Balanced", {"async_en": True}),
        ("Memory Efficient", {"async_en": True, "writer_type": "line", "queue": 1_000, "policy": "drop_oldest"}),
    ]
    
    results = []
    for name, config in configs:
        result = benchmark_config(name.lower().replace(" ", "_"), config)
        results.append((name, result))
    
    print(f"\n{'Configuration':<18} | {'Throughput':>14} | {'Latency':>10} | {'Memory':>10}")
    print("-" * 70)
    
    for name, result in results:
        throughput = f"{result['throughput']:,.0f} L/s"
        latency = f"{1000000 / result['throughput']:.1f} µs" if result['throughput'] > 0 else "N/A"
        memory = "High" if "max" in name.lower() else "Low" if "memory" in name.lower() else "Medium"
        print(f"{name:<18} | {throughput:>14} | {latency:>10} | {memory:>10}")
    
    print("\nRecommendations:")
    print("  • Use 'Max Throughput' for production high-volume logging")
    print("  • Use 'Min Latency' for debugging and real-time alerts")
    print("  • Use 'Balanced' for most applications (good default)")
    print("  • Use 'Memory Efficient' for containers/embedded systems")


def print_code_examples():
    """Print ready-to-use code examples."""
    print("\n" + "="*70)
    print("READY-TO-USE CODE EXAMPLES")
    print("="*70)
    
    print("\n# Maximum Throughput (200K+ L/s)")
    print('log.init("app.log", writer_type="block", writer_mode="trigger", size=500)')
    
    print("\n# Minimum Latency (<1ms)")
    print('log.init("app.log", async_en=False, writer_type="line", size=1)')
    
    print("\n# Balanced (default, 100K+ L/s)")
    print('log.init("app.log")')
    
    print("\n# Memory Efficient (constrained environments)")
    print('log.init("app.log", queue=1000, policy="drop_oldest", size=50)')
    
    print("\n# Large Scale (100K+ logs in burst)")
    print('log.init("app.log", queue=100_000, size=1000, writer_type="block")')


def main():
    print("="*70)
    print("PERFORMANCE TUNING GUIDE")
    print("="*70)
    print("\nThis example demonstrates different performance configurations.")
    print("Running benchmarks with 10,000 log entries each...")
    
    demo_max_throughput()
    demo_min_latency()
    demo_balanced()
    demo_memory_efficient()
    demo_comparison_table()
    print_code_examples()
    
    print("\n" + "="*70)
    print("Note: Results vary by hardware, OS, and filesystem.")
    print("Run your own benchmarks for your specific environment.")
    print("="*70)


if __name__ == "__main__":
    main()
