#!/usr/bin/env python3
"""Writer Types and Modes Demo - Choose-L2 Based Writer

This example demonstrates all writer types and modes available
in the new choose-L2 based writer implementation.

Writer Types:
- line: Line buffered (immediate flush, real-time)
- block: Block buffered 64KB (balanced, default)
- mmap: Memory mapped (maximum throughput)

Writer Modes:
- trigger: Event-driven (wake on message, default)
- loop: Periodic poll (check queue every tick)
- manual: Explicit trigger() calls
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logxpy import log, Mode, WriterType


def demo_writer_type(writer_type: str):
    """Demonstrate a specific writer type."""
    log_file = f"demo_writer_{writer_type}.log"
    
    print(f"\n{'='*60}")
    print(f"Writer Type: {writer_type.upper()}")
    print(f"{'='*60}")
    
    log.init(
        log_file,
        async_en=True,
        writer_type=writer_type,
        writer_mode="trigger",
        size=10,
    )
    
    start = time.perf_counter()
    for i in range(100):
        log.info(f"Message {i}", writer_type=writer_type)
    elapsed = time.perf_counter() - start
    
    log.shutdown_async()
    
    print(f"  Enqueued 100 messages in {elapsed:.4f}s")
    print(f"  Throughput: {100/elapsed:,.0f} msg/sec")
    
    # Count lines
    with open(log_file) as f:
        lines = sum(1 for _ in f)
    print(f"  Lines written: {lines}")
    
    # Cleanup
    import os
    os.remove(log_file)


def demo_writer_mode(writer_mode: str):
    """Demonstrate a specific writer mode."""
    log_file = f"demo_mode_{writer_mode}.log"
    
    print(f"\n{'='*60}")
    print(f"Writer Mode: {writer_mode.upper()}")
    print(f"{'='*60}")
    
    tick = 0.05 if writer_mode == "loop" else 0.1
    
    log.init(
        log_file,
        async_en=True,
        writer_type="block",
        writer_mode=writer_mode,
        tick=tick,
        size=50,
    )
    
    start = time.perf_counter()
    for i in range(20):
        log.info(f"Message {i}", writer_mode=writer_mode)
        if writer_mode == "manual":
            log.trigger()
            time.sleep(0.01)
    
    if writer_mode == "manual":
        log.trigger()  # Final trigger
        time.sleep(0.05)
    elif writer_mode == "loop":
        time.sleep(0.2)  # Give LOOP mode time
    
    elapsed = time.perf_counter() - start
    log.shutdown_async()
    
    print(f"  Enqueued 20 messages in {elapsed:.4f}s")
    
    # Count lines
    with open(log_file) as f:
        lines = sum(1 for _ in f)
    print(f"  Lines written: {lines}")
    
    # Cleanup
    import os
    os.remove(log_file)


def demo_policies():
    """Demonstrate queue policies."""
    print(f"\n{'='*60}")
    print("Queue Policies")
    print(f"{'='*60}")
    
    policies = ["block", "drop_oldest", "drop_newest", "warn"]
    
    for policy in policies:
        log_file = f"demo_policy_{policy}.log"
        
        print(f"\n  Policy: {policy}")
        
        log.init(
            log_file,
            async_en=True,
            writer_type="block",
            queue=1000,
            size=100,
            policy=policy,
        )
        
        start = time.perf_counter()
        for i in range(500):
            log.info(f"Message {i}", policy=policy)
        elapsed = time.perf_counter() - start
        
        metrics = log.get_async_metrics()
        log.shutdown_async()
        
        print(f"    Enqueued: {metrics['enqueued']}")
        print(f"    Written: {metrics['written']}")
        print(f"    Dropped: {metrics['dropped']}")
        print(f"    Time: {elapsed:.4f}s")
        
        # Cleanup
        import os
        os.remove(log_file)


def demo_comparison():
    """Compare all writer types side by side."""
    print(f"\n{'='*60}")
    print("Writer Type Comparison (1000 messages each)")
    print(f"{'='*60}")
    
    results = []
    
    for writer_type in ["line", "block", "mmap"]:
        log_file = f"bench_{writer_type}.log"
        
        log.init(
            log_file,
            async_en=True,
            writer_type=writer_type,
            size=100,
        )
        
        start = time.perf_counter()
        for i in range(1000):
            log.info(f"Benchmark message {i}")
        elapsed = time.perf_counter() - start
        
        log.shutdown_async()
        
        results.append((writer_type, elapsed, 1000/elapsed))
        
        # Cleanup
        import os
        os.remove(log_file)
    
    print(f"\n  {'Type':<10} {'Time (s)':<12} {'Throughput':<15}")
    print(f"  {'-'*40}")
    for writer_type, elapsed, throughput in results:
        print(f"  {writer_type:<10} {elapsed:<12.4f} {throughput:>10,.0f} msg/s")
    
    best = max(results, key=lambda x: x[2])
    print(f"\n  Winner: {best[0]} ({best[2]:,.0f} msg/s)")


def main():
    """Run all demonstrations."""
    print("="*60)
    print("Choose-L2 Based Writer Demo")
    print("="*60)
    print("\nThis demo shows all writer types and modes available")
    print("in the new choose-L2 based async writer.")
    
    # Demo writer types
    for writer_type in ["line", "block", "mmap"]:
        demo_writer_type(writer_type)
    
    # Demo writer modes
    for writer_mode in ["trigger", "loop", "manual"]:
        demo_writer_mode(writer_mode)
    
    # Demo policies
    demo_policies()
    
    # Comparison
    demo_comparison()
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)
    print("\nRecommendations:")
    print("  • Use 'line' for real-time logging (immediate flush)")
    print("  • Use 'block' for balanced performance (default)")
    print("  • Use 'mmap' for maximum throughput")
    print("  • Use 'trigger' mode for event-driven (default)")
    print("  • Use 'loop' mode for periodic polling")
    print("  • Use 'manual' mode for explicit control")


if __name__ == "__main__":
    main()
