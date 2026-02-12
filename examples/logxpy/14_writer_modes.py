"""14_writer_modes.py - Demonstrating Writer Modes

Shows the three writer modes and their behavior:
- trigger: Event-driven (default) - flushes on batch size or event
- loop: Timer-based - flushes periodically
- manual: Explicit control - you call trigger()

For 200K+ logs/sec throughput, use trigger mode with block writer.
"""

import time
import os
from logxpy import log


def demo_trigger_mode():
    """TRIGGER mode: Event-driven flushing (recommended for high throughput)."""
    print("\n" + "="*60)
    print("TRIGGER MODE (Event-driven)")
    print("="*60)
    
    log_file = "/tmp/demo_trigger.log"
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # TRIGGER mode: Flushes when batch_size reached or on explicit events
    log.init(log_file, writer_mode="trigger", size=100, async_en=False)
    
    # These write immediately (sync mode for demo)
    for i in range(10):
        log.info(f"Message {i}")
    
    print(f"Log file: {log_file}")
    print(f"Lines written: {count_lines(log_file)}")
    print("Behavior: Flushes when batch_size (100) reached")
    
    os.remove(log_file)


def demo_loop_mode():
    """LOOP mode: Timer-based periodic flushing."""
    print("\n" + "="*60)
    print("LOOP MODE (Timer-based)")
    print("="*60)
    
    log_file = "/tmp/demo_loop.log"
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # LOOP mode: Flushes periodically based on flush interval
    # Also flushes when batch_size reached
    log.init(log_file, writer_mode="loop", size=100, flush=0.05, async_en=False)
    
    for i in range(10):
        log.info(f"Message {i}")
    
    # In real async mode, would need: time.sleep(0.1) for flush
    
    print(f"Log file: {log_file}")
    print(f"Lines written: {count_lines(log_file)}")
    print("Behavior: Flushes every 50ms OR when batch_size reached")
    
    os.remove(log_file)


def demo_manual_mode():
    """MANUAL mode: You control when to flush."""
    print("\n" + "="*60)
    print("MANUAL MODE (Explicit control)")
    print("="*60)
    
    log_file = "/tmp/demo_manual.log"
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # MANUAL mode: Only flushes when you call trigger() or shutdown
    log.init(log_file, writer_mode="manual", size=1000, async_en=False)
    
    for i in range(10):
        log.info(f"Message {i}")
    
    # In manual mode, logs stay in memory until trigger()
    print(f"Before trigger - Lines written: {count_lines(log_file)}")
    
    # Explicit flush
    log.flush()
    
    print(f"After trigger - Lines written: {count_lines(log_file)}")
    print("Behavior: Only flushes on explicit trigger() or shutdown")
    
    os.remove(log_file)


def demo_comparison():
    """Compare all three modes with timing."""
    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON")
    print("="*60)
    
    count = 1000
    
    # TRIGGER mode
    log_file = "/tmp/demo_compare_trigger.log"
    if os.path.exists(log_file):
        os.remove(log_file)
    
    log.init(log_file, writer_mode="trigger", async_en=False)
    start = time.perf_counter()
    for i in range(count):
        log.info(f"Message {i}")
    trigger_time = (time.perf_counter() - start) * 1000
    trigger_lines = count_lines(log_file)
    os.remove(log_file)
    
    # LOOP mode
    log_file = "/tmp/demo_compare_loop.log"
    if os.path.exists(log_file):
        os.remove(log_file)
    
    log.init(log_file, writer_mode="loop", flush=0.01, async_en=False)
    start = time.perf_counter()
    for i in range(count):
        log.info(f"Message {i}")
    loop_time = (time.perf_counter() - start) * 1000
    loop_lines = count_lines(log_file)
    os.remove(log_file)
    
    # MANUAL mode
    log_file = "/tmp/demo_compare_manual.log"
    if os.path.exists(log_file):
        os.remove(log_file)
    
    log.init(log_file, writer_mode="manual", async_en=False)
    start = time.perf_counter()
    for i in range(count):
        log.info(f"Message {i}")
    manual_time = (time.perf_counter() - start) * 1000
    manual_lines = count_lines(log_file)
    os.remove(log_file)
    
    print(f"\n{count} log entries:")
    print(f"  TRIGGER: {trigger_time:.1f}ms, {trigger_lines} lines written")
    print(f"  LOOP:    {loop_time:.1f}ms, {loop_lines} lines written")
    print(f"  MANUAL:  {manual_time:.1f}ms, {manual_lines} lines written (flushed at end)")
    
    print("\nRecommendation:")
    print("  • TRIGGER: Best for high throughput (200K+ L/s)")
    print("  • LOOP:    Use for predictable flush intervals")
    print("  • MANUAL:  Use when you need full control")


def count_lines(filepath: str) -> int:
    """Count lines in file."""
    if not os.path.exists(filepath):
        return 0
    with open(filepath) as f:
        return sum(1 for line in f if line.strip())


def main():
    print("="*60)
    print("WRITER MODES DEMONSTRATION")
    print("="*60)
    print("\nThis example shows the three writer modes:")
    print("  1. trigger - Event-driven (default, fastest)")
    print("  2. loop    - Timer-based (predictable)")
    print("  3. manual  - Explicit control")
    
    demo_trigger_mode()
    demo_loop_mode()
    demo_manual_mode()
    demo_comparison()
    
    print("\n" + "="*60)
    print("For 200K+ L/s throughput, use:")
    print('  log.init("app.log", writer_mode="trigger")')
    print("="*60)


if __name__ == "__main__":
    main()
