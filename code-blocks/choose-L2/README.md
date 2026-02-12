# Choose-L2 Async Writer

Standalone async file writer implementation for logxpy with three writer types and three operating modes.

## Features

- **Three Writer Types:**
  - `LineBufferedWriter` - Immediate flush (real-time logging)
  - `BlockBufferedWriter` - 64KB buffer (balanced performance, default)
  - `MemoryMappedWriter` - OS-managed memory mapping (max throughput)

- **Three Operating Modes:**
  - `TRIGGER` - Event-driven, wake on message (best throughput)
  - `LOOP` - Timer-based periodic flush (predictable timing)
  - `MANUAL` - Explicit `trigger()` control (full control)

- **Backpressure Policies:**
  - `BLOCK` - Pause until space available (no data loss)
  - `DROP_OLDEST` - Remove oldest messages (fixed memory)
  - `DROP_NEWEST` - Discard new messages (overflow OK)
  - `WARN` - Warn and drop (debugging)

- **Thread-safe Queue:** GIL-atomic operations, no locks needed in CPython

## Quick Start

```python
from writer import create_writer, Mode, WriterType

# Simple - use defaults (BlockBuffered, Trigger mode)
writer = create_writer("app.log")

for i in range(1000):
    writer.send(f"Log line {i}")

writer.stop()
print(f"Written: {writer.lines_written}")
```

## Configuration

```python
from writer import create_writer, Mode, WriterType, QueuePolicy

writer = create_writer(
    "app.log",
    writer_type=WriterType.BLOCK,    # line | block | mmap
    mode=Mode.TRIGGER,                # trigger | loop | manual
    queue_size=10_000,                # Max queue size
    batch_size=100,                   # Messages per batch
    flush_interval=0.1,               # Seconds between flushes
    policy=QueuePolicy.BLOCK,         # Backpressure policy
)
```

## Writer Types

### LineBufferedWriter
```python
from writer import LineBufferedWriter, Mode, Q

q = Q()
writer = LineBufferedWriter(q, "app.log", Mode.TRIGGER)
# Each line flushed immediately (buffering=1)
```

### BlockBufferedWriter (Default)
```python
from writer import BlockBufferedWriter, Mode, Q

q = Q()
writer = BlockBufferedWriter(q, "app.log", Mode.TRIGGER)
# 64KB kernel buffer for batching
```

### MemoryMappedWriter
```python
from writer import MemoryMappedWriter, Mode, Q

q = Q()
writer = MemoryMappedWriter(q, "app.log", Mode.TRIGGER)
# OS-managed memory mapping
```

## Operating Modes

### TRIGGER Mode (Default)
```python
writer = create_writer("app.log", mode=Mode.TRIGGER, batch_size=100)
# Flushes when batch_size reached or on timeout
```

### LOOP Mode
```python
writer = create_writer("app.log", mode=Mode.LOOP, flush_interval=0.1)
# Flushes every 100ms OR when batch_size reached
```

### MANUAL Mode
```python
writer = create_writer("app.log", mode=Mode.MANUAL)
writer.send("line 1")
writer.send("line 2")
writer.trigger()  # Explicit flush
writer.stop()
```

## Metrics

```python
writer = create_writer("app.log")

for i in range(100):
    writer.send(f"line {i}")

writer.stop()

metrics = writer.metrics
print(f"Enqueued: {metrics.enqueued}")
print(f"Written:  {metrics.written}")
print(f"Dropped:  {metrics.dropped}")
print(f"Pending:  {metrics.pending}")

# Full snapshot
print(metrics.get_snapshot())
```

## Testing

```bash
# Run tests
cd code-blocks/choose-L2
pytest tests/ -v

# Run examples
PYTHONPATH=writer python examples/basic_usage.py
```

## Performance

| Writer | Buffer | Best For | Throughput |
|--------|--------|----------|------------|
| Line | 1 line | Real-time | ~260K L/s |
| Block | 64KB | Balanced | ~275K L/s |
| MMAP | OS-managed | Max throughput | ~250K L/s |

## API Reference

### Classes

- `Q` - Thread-safe queue with backpressure policies
- `WriterMetrics` - Performance metrics tracking
- `BaseFileWriterThread` - Abstract base class
- `LineBufferedWriter` - Line-buffered implementation
- `BlockBufferedWriter` - Block-buffered implementation  
- `MemoryMappedWriter` - Memory-mapped implementation

### Enums

- `Mode.TRIGGER | LOOP | MANUAL` - Operating modes
- `WriterType.LINE | BLOCK | MMAP` - Writer types
- `QueuePolicy.BLOCK | DROP_OLDEST | DROP_NEWEST | WARN` - Policies

### Functions

- `create_writer(path, **kwargs)` - Factory function

## License

MIT - Same as logxpy
