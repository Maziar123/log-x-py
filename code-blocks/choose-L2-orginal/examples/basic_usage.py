"""Basic usage examples for choose-L2 writers."""

from writer import FileWriter, Mode, Q


def example_simple() -> None:
    """Simplest usage with default writer."""
    print("=" * 50)
    print("Example: Simple Usage (Default Writer)")
    print("=" * 50)

    q = Q()
    
    # Default: BlockBufferedWriter with 64KB buffer
    writer = FileWriter(q, "output_simple.txt", Mode.TRIGGER)
    
    for i in range(100):
        writer.send(f"line {i}")
    
    q.stop()
    writer.join()
    
    print(f"  Lines written: {writer.lines_written}")
    print(f"  Flushes: {writer.flush_count}")
    print()


def example_explicit_writers() -> None:
    """Using specific writer implementations."""
    print("=" * 50)
    print("Example: Explicit Writers")
    print("=" * 50)

    from writer.sync import (
        LineBufferedWriter,
        BlockBufferedWriter,
        MemoryMappedWriter,
    )

    writers = [
        ("LineBuffered", LineBufferedWriter),
        ("BlockBuffered", BlockBufferedWriter),
        ("MemoryMapped", MemoryMappedWriter),
    ]

    for name, WriterClass in writers:
        q = Q()
        writer = WriterClass(q, f"output_{name.lower()}.txt", Mode.TRIGGER)
        
        for i in range(50):
            writer.send(f"{name} line {i}")
        
        q.stop()
        writer.join()
        
        print(f"  {name:15} {writer.lines_written:5} lines, {writer.flush_count:2} flushes")
    print()


def example_modes() -> None:
    """Demonstrate all 3 modes."""
    print("=" * 50)
    print("Example: Mode Comparison")
    print("=" * 50)

    modes = [
        (Mode.TRIGGER, "Event-driven"),
        (Mode.LOOP, "Periodic (100ms)"),
        (Mode.MANUAL, "On-demand"),
    ]

    for mode, description in modes:
        q = Q()
        
        if mode is Mode.LOOP:
            writer = FileWriter(q, f"output_{mode.name}.txt", mode, tick=0.1)
        else:
            writer = FileWriter(q, f"output_{mode.name}.txt", mode)

        # Send 100 lines
        for i in range(100):
            writer.send(f"line {i}")
            if mode is Mode.MANUAL and i % 25 == 0:
                writer.trigger()
        
        if mode is Mode.MANUAL:
            writer.trigger()

        q.stop()
        writer.join()

        print(f"  {mode.name:10} ({description:20}): {writer.flush_count:2} flushes")
    print()


def example_context_manager() -> None:
    """Using context manager for automatic cleanup."""
    print("=" * 50)
    print("Example: Context Manager")
    print("=" * 50)

    q = Q()
    
    with FileWriter(q, "output_context.txt", Mode.TRIGGER) as writer:
        for i in range(100):
            writer.send(f"line {i}")
        # Writer automatically cleaned up on exit
    
    q.stop()
    
    print("  Context manager handled cleanup automatically")
    print()


def main() -> None:
    """Run all examples."""
    print("\n" + "=" * 50)
    print("choose-L2: Basic Usage Examples")
    print("=" * 50 + "\n")

    example_simple()
    example_explicit_writers()
    example_modes()
    example_context_manager()

    print("=" * 50)
    print("Done! Check output_*.txt files")
    print("=" * 50)


if __name__ == "__main__":
    main()
