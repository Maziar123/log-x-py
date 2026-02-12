"""Basic usage examples for choose-L2 writers."""

from writer import (
    BlockBufferedWriter,
    LineBufferedWriter,
    MemoryMappedWriter,
    Mode,
    Q,
    QueuePolicy,
    WriterType,
    create_writer,
)


def example_simple() -> None:
    """Simplest usage with factory function."""
    print("=" * 60)
    print("Example: Simple Usage (Factory Function)")
    print("=" * 60)

    # Default: BlockBufferedWriter with TRIGGER mode
    writer = create_writer("output_simple.log", writer_type=WriterType.BLOCK)
    
    for i in range(100):
        writer.send(f"line {i}")
    
    writer.stop()
    
    print(f"  Lines written: {writer.lines_written}")
    print(f"  Flushes: {writer.flush_count}")
    print(f"  Mode: {writer._mode.value}")
    print()


def example_explicit_writers() -> None:
    """Using specific writer implementations."""
    print("=" * 60)
    print("Example: Explicit Writers")
    print("=" * 60)

    writers = [
        ("LineBuffered", LineBufferedWriter),
        ("BlockBuffered", BlockBufferedWriter),
        ("MemoryMapped", MemoryMappedWriter),
    ]

    for name, WriterClass in writers:
        q = Q()
        writer = WriterClass(q, f"output_{name.lower()}.log", Mode.TRIGGER)
        
        for i in range(50):
            writer.send(f"{name} line {i}")
        
        writer.stop()
        
        print(f"  {name:15} {writer.lines_written:5} lines, {writer.flush_count:2} flushes")
    print()


def example_modes() -> None:
    """Demonstrate all 3 modes."""
    print("=" * 60)
    print("Example: Mode Comparison")
    print("=" * 60)

    import time

    modes = [
        (Mode.TRIGGER, "Event-driven"),
        (Mode.LOOP, "Periodic (100ms)"),
        (Mode.MANUAL, "On-demand"),
    ]

    for mode, description in modes:
        writer = create_writer(
            f"output_{mode.value}.log",
            writer_type=WriterType.BLOCK,
            mode=mode,
            flush_interval=0.1,
        )

        # Send 100 lines
        for i in range(100):
            writer.send(f"{mode.value} line {i}")

        if mode is Mode.MANUAL:
            # Manual mode needs explicit trigger or stop
            writer.trigger()
        
        # Wait a bit for LOOP mode to flush
        if mode is Mode.LOOP:
            time.sleep(0.15)
        
        writer.stop()

        print(f"  {mode.value:10} ({description:20}): {writer.lines_written:3} lines")
    print()


def example_policies() -> None:
    """Demonstrate queue policies."""
    print("=" * 60)
    print("Example: Queue Policies")
    print("=" * 60)

    import time

    policies = [
        (QueuePolicy.BLOCK, "Block until space"),
        (QueuePolicy.DROP_OLDEST, "Drop oldest"),
        (QueuePolicy.DROP_NEWEST, "Drop newest"),
    ]

    for policy, description in policies:
        # Small queue to demonstrate policy
        writer = create_writer(
            f"output_policy_{policy.value}.log",
            queue_size=10,  # Small queue
            batch_size=5,
            policy=policy,
        )

        # Send 50 lines quickly
        for i in range(50):
            writer.send(f"line {i}")

        time.sleep(0.1)
        writer.stop()

        metrics = writer.metrics
        print(f"  {policy.value:15} {description:20}: "
              f"written={metrics.written:2}, dropped={metrics.dropped:2}")
    print()


def example_metrics() -> None:
    """Demonstrate metrics tracking."""
    print("=" * 60)
    print("Example: Metrics Tracking")
    print("=" * 60)

    writer = create_writer("output_metrics.log", queue_size=1000)

    for i in range(100):
        writer.send(f"line {i}")

    writer.stop()

    metrics = writer.metrics
    print(f"  Enqueued: {metrics.enqueued}")
    print(f"  Written:  {metrics.written}")
    print(f"  Dropped:  {metrics.dropped}")
    print(f"  Errors:   {metrics.errors}")
    print(f"  Pending:  {metrics.pending}")
    
    snapshot = metrics.get_snapshot()
    print(f"\n  Full snapshot: {snapshot}")
    print()


def cleanup():
    """Remove example output files."""
    import os
    import glob
    
    for pattern in ["output_*.log"]:
        for f in glob.glob(pattern):
            try:
                os.remove(f)
            except OSError:
                pass


def main():
    """Run all examples."""
    try:
        example_simple()
        example_explicit_writers()
        example_modes()
        example_policies()
        example_metrics()
    finally:
        cleanup()


if __name__ == "__main__":
    main()
