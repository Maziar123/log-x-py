"""09_configuration.py - Complete Configuration Guide

Demonstrates ALL log.init() parameters:
- target, level, mode, clean
- async_en, queue, size, flush
- policy, writer_type, writer_mode
- task_id_mode, tick

Also shows log.configure() for runtime changes.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "logxpy" / "src"))

from logxpy import log


def demo_basic_init():
    """Basic init() usage."""
    print("\n" + "="*60)
    print("1. BASIC INIT()")
    print("="*60)
    
    log_file = "/tmp/config_basic.log"
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Simplest form - auto-generate filename
    print("\n# Auto-generate filename from __file__")
    print('log.init()  # Creates <script_name>.log')
    
    # With custom filename
    print("\n# Custom filename")
    print('log.init("app.log")')
    
    # With options
    print("\n# With common options")
    print('log.init("app.log", level="INFO", clean=True)')
    
    # Demo
    log.init(log_file, async_en=False, clean=True)
    log.info("Basic init demo")
    
    print(f"\nCreated: {log_file}")
    os.remove(log_file)


def demo_file_modes():
    """File mode options."""
    print("\n" + "="*60)
    print("2. FILE MODES")
    print("="*60)
    
    print("\n# mode='w' - Write (default, overwrites existing)")
    print('log.init("app.log", mode="w")')
    
    print("\n# mode='a' - Append (adds to existing)")
    print('log.init("app.log", mode="a")')
    
    print("\n# clean=True - Delete existing file first")
    print('log.init("app.log", clean=True)')


def demo_async_options():
    """Async logging options."""
    print("\n" + "="*60)
    print("3. ASYNC OPTIONS")
    print("="*60)
    
    print("\n# async_en=True - Async logging (default, fastest)")
    print('log.init("app.log", async_en=True)')
    
    print("\n# async_en=False - Sync logging (immediate, slower)")
    print('log.init("app.log", async_en=False)')
    
    print("\n# queue=100000 - Large queue for burst handling")
    print('log.init("app.log", queue=100_000)')
    
    print("\n# size=500 - Batch 500 messages before flush")
    print('log.init("app.log", size=500)')
    
    print("\n# flush=0.1 - Flush every 100ms")
    print('log.init("app.log", flush=0.1)')
    print('# or: flush="100ms"')
    
    print("\n# policy='block' - Backpressure: block when full (default)")
    print('log.init("app.log", policy="block")')
    
    print("\n# policy='drop_oldest' - Backpressure: drop oldest")
    print('log.init("app.log", policy="drop_oldest")')
    
    print("\n# Available policies:")
    print("#   'block'       - Pause app until queue has space")
    print("#   'drop_oldest' - Remove oldest pending messages")
    print("#   'drop_newest' - Discard new messages")
    print("#   'warn'        - Warn and drop new messages")


def demo_writer_types():
    """Writer type options."""
    print("\n" + "="*60)
    print("4. WRITER TYPES")
    print("="*60)
    
    print("\n# writer_type='block' - Block buffered 64KB (default, balanced)")
    print('log.init("app.log", writer_type="block")')
    print("# Best for: Most applications")
    
    print("\n# writer_type='line' - Line buffered (immediate)")
    print('log.init("app.log", writer_type="line")')
    print("# Best for: Real-time logging, low latency")
    
    print("\n# writer_type='mmap' - Memory mapped (fastest)")
    print('log.init("app.log", writer_type="mmap")')
    print("# Best for: Maximum throughput")


def demo_writer_modes():
    """Writer mode options."""
    print("\n" + "="*60)
    print("5. WRITER MODES")
    print("="*60)
    
    print("\n# writer_mode='trigger' - Event-driven (default)")
    print('log.init("app.log", writer_mode="trigger")')
    print("# Flushes: On batch_size or explicit event")
    print("# Best for: High throughput (200K+ L/s)")
    
    print("\n# writer_mode='loop' - Timer-based")
    print('log.init("app.log", writer_mode="loop", flush=0.1)')
    print("# Flushes: Every flush interval OR batch_size")
    print("# Best for: Predictable flush timing")
    
    print("\n# writer_mode='manual' - Explicit control")
    print('log.init("app.log", writer_mode="manual")')
    print("# Flushes: Only when you call log.trigger()")
    print("# Best for: Full control over flushing")


def demo_task_id_modes():
    """Task ID mode options."""
    print("\n" + "="*60)
    print("6. TASK ID MODES")
    print("="*60)
    
    print("\n# task_id_mode='sqid' - Short hierarchical IDs (default)")
    print('log.init("app.log", task_id_mode="sqid")')
    print("# Format: Xa.1, Xa.1.1 (4-12 chars)")
    print("# Best for: Single-process apps, 78% smaller than UUID")
    
    print("\n# task_id_mode='uuid' - Standard UUID4")
    print('log.init("app.log", task_id_mode="uuid")')
    print("# Format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx (36 chars)")
    print("# Best for: Distributed systems, multi-process tracing")


def demo_complete_example():
    """Complete configuration example."""
    print("\n" + "="*60)
    print("7. COMPLETE EXAMPLE")
    print("="*60)
    
    log_file = "/tmp/config_complete.log"
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Full configuration
    log.init(
        log_file,                    # Target file
        level="DEBUG",               # Log level
        mode="w",                    # File mode (write)
        clean=True,                  # Remove existing
        async_en=True,               # Enable async
        queue=10_000,                # Queue size
        size=100,                    # Batch size
        flush=0.1,                   # Flush interval (100ms)
        deadline=None,               # Max time before flush
        policy="block",              # Backpressure policy
        writer_type="block",         # Writer type
        writer_mode="trigger",       # Writer mode
        tick=0.01,                   # Loop mode tick interval
        task_id_mode="sqid",         # Task ID format
    )
    
    log.debug("Debug message")
    log.info("Info message", user="alice")
    log.success("Success message")
    log.warning("Warning message")
    log.error("Error message")
    
    log.shutdown_async()
    
    # Read back
    print(f"\nLog file: {log_file}")
    print("Contents:")
    with open(log_file) as f:
        for line in f:
            print(f"  {line.strip()[:80]}...")
    
    os.remove(log_file)


def demo_configure_runtime():
    """Runtime configuration changes."""
    print("\n" + "="*60)
    print("8. RUNTIME CONFIGURATION (log.configure)")
    print("="*60)
    
    print("\n# Change log level at runtime")
    print("log.configure(level='WARNING')  # Now only WARNING and above")
    
    print("\n# Add field masking")
    print("log.configure(mask_fields=['password', 'token'])")
    
    print("\n# Multiple changes")
    print("""log.configure(
    level="INFO",
    destinations=["console", "file://app.log"],
    mask_fields=["password", "secret"]
)""")


def demo_environment_variables():
    """Environment variable configuration."""
    print("\n" + "="*60)
    print("9. ENVIRONMENT VARIABLES")
    print("="*60)
    
    print("\n# Force UUID mode for distributed systems")
    print("export LOGXPY_DISTRIBUTED=1")
    
    print("\n# Force sync mode")
    print("export LOGXPY_SYNC=1")
    
    print("\n# In Python, check environment:")
    print("import os")
    print('if os.environ.get("LOGXPY_DISTRIBUTED"):')
    print('    log.init("app.log", task_id_mode="uuid")')
    print('else:')
    print('    log.init("app.log", task_id_mode="sqid")')


def print_quick_reference():
    """Print quick reference card."""
    print("\n" + "="*60)
    print("QUICK REFERENCE")
    print("="*60)
    
    print("""
log.init(
    target=None,              # File path or None (auto)
    level="DEBUG",            # DEBUG, INFO, WARNING, ERROR, CRITICAL
    mode="w",                 # 'w' write or 'a' append
    clean=False,              # Delete existing file
    async_en=True,            # Enable async logging
    queue=10_000,             # Queue size
    size=100,                 # Batch size (messages)
    flush=0.1,                # Flush interval (seconds or "100ms")
    deadline=None,            # Max time before forced flush
    policy="block",           # Backpressure: block, drop_oldest, drop_newest, warn
    writer_type="block",      # line, block, mmap
    writer_mode="trigger",    # trigger, loop, manual
    tick=0.01,                # Loop mode poll interval
    task_id_mode="sqid",      # sqid (short) or uuid (36-char)
)

Performance Presets:
  # Max throughput (200K+ L/s)
  log.init("app.log", writer_type="block", size=500)
  
  # Min latency (<1ms)
  log.init("app.log", async_en=False, writer_type="line", size=1)
  
  # Balanced (default, 100K+ L/s)
  log.init("app.log")
  
  # Large scale (100K+ burst)
  log.init("app.log", queue=100_000, size=1000)
""")


def main():
    print("="*60)
    print("CONFIGURATION GUIDE")
    print("="*60)
    print("\nThis example demonstrates ALL log.init() parameters.")
    
    demo_basic_init()
    demo_file_modes()
    demo_async_options()
    demo_writer_types()
    demo_writer_modes()
    demo_task_id_modes()
    demo_complete_example()
    demo_configure_runtime()
    demo_environment_variables()
    print_quick_reference()
    
    print("\n" + "="*60)
    print("For more details, see:")
    print("  - GUIDE.md")
    print("  - API Reference: logxpy-api-reference.html")
    print("="*60)


if __name__ == "__main__":
    main()
