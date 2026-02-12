# choose-L2: Unified File Writer Library

Cross-platform file writer with **unified base class** and **3 I/O strategies**.

## Quick Start

```python
from writer import FileWriter, Mode, Q

q = Q()
writer = FileWriter(q, "output.txt", Mode.TRIGGER)

for i in range(100000):
    writer.send(f"line {i}")

q.stop()
writer.join()  # ~3M lines/second
```

## Architecture

```
writer/
├── __init__.py          # Default export: BlockBufferedWriter
├── base.py              # BaseFileWriterThread, Q, Mode
└── sync/
    ├── __init__.py      # Exports all 3 writers
    ├── line_buffered.py # LineBufferedWriter
    ├── block_buffered.py# BlockBufferedWriter (default)
    └── memory_mapped.py # MemoryMappedWriter
```

**Key Design:**
- One `BaseFileWriterThread` handles all 3 modes (TRIGGER/LOOP/MANUAL)
- Implementations only override `_write_batch()` method
- ~15 lines per implementation

## Three Writers

| Writer | Lines | Buffer | 100K Perf | Use Case |
|--------|-------|--------|-----------|----------|
| `LineBufferedWriter` | ~15 | 1 line | 37ms / 2.7M L/s | Real-time logging |
| `BlockBufferedWriter` | ~15 | 64KB | 39ms / 2.5M L/s | **Default** - balanced |
| `MemoryMappedWriter` | ~35 | OS-managed | 36ms / 2.7M L/s | Max throughput |

## Three Modes

### TRIGGER (Event-Driven)
```python
writer = FileWriter(q, "output.txt", Mode.TRIGGER)
# Writer wakes immediately on each send()
```

### LOOP (Periodic)
```python
writer = FileWriter(q, "output.txt", Mode.LOOP, tick=0.1)  # 100ms
# Writer checks queue every 100ms
```

### MANUAL (Explicit)
```python
writer = FileWriter(q, "output.txt", Mode.MANUAL)
# Writer only writes when you call writer.trigger()
```

## Usage Examples

### Default Writer
```python
from writer import FileWriter, Mode, Q

q = Q()
writer = FileWriter(q, "output.txt", Mode.TRIGGER)
# Uses BlockBufferedWriter (64KB buffer)
```

### Explicit Writers
```python
from writer.sync import (
    LineBufferedWriter,
    BlockBufferedWriter, 
    MemoryMappedWriter,
)

# Line-buffered for immediate flush
writer = LineBufferedWriter(q, "output.txt", Mode.TRIGGER)

# Block-buffered for throughput
writer = BlockBufferedWriter(q, "output.txt", Mode.LOOP, tick=0.5)

# Memory-mapped for OS-managed flush
writer = MemoryMappedWriter(q, "output.txt", Mode.TRIGGER)
```

### Context Manager
```python
q = Q()
with FileWriter(q, "output.txt", Mode.TRIGGER) as writer:
    for i in range(1000):
        writer.send(f"line {i}")
q.stop()
```

## Running

```bash
# Examples
PYTHONPATH=$(pwd) python examples/basic_usage.py

# Tests
PYTHONPATH=$(pwd) python -m pytest tests/ -v
```

## Benchmark Results

> **Note:** Run benchmarks from the **root directory** (`../benchmark*.py`)

Expected performance (100,000 lines):
```
MemoryMapped TRIGGER   36.39ms  2,748,326 L/s  (5 flushes)
LineBuffered  TRIGGER  37.54ms  2,663,675 L/s  (5 flushes)
BlockBuffered TRIGGER  39.26ms  2,547,113 L/s  (4 flushes)
```

## Platform Support

| Platform | Support | Best Writer |
|----------|---------|-------------|
| Linux | ✅ | All 3 |
| macOS | ✅ | All 3 |
| Windows | ✅ | All 3 |

**Dependencies:** None (stdlib only)

## Implementation Example

New writer implementations are ~15 lines:

```python
from writer.base import BaseFileWriterThread, Mode, Q

class MyWriter(BaseFileWriterThread):
    """Custom writer implementation."""
    
    def _write_batch(self, items: list[str]) -> None:
        """Write batch - only method to implement."""
        if not items:
            return
        with open(self._path, "a") as f:
            f.write("\n".join(items) + "\n")
            self._record(len(items))
```

Base class handles:
- Thread lifecycle
- Mode loops (TRIGGER/LOOP/MANUAL)
- Queue management
- Batching
- Statistics (lines_written, flush_count)

## Files

| File | Purpose |
|------|---------|
| `writer/base.py` | Base class, Q, Mode (~200 lines) |
| `writer/sync/line_buffered.py` | Line-buffered writer |
| `writer/sync/block_buffered.py` | Block-buffered writer (default) |
| `writer/sync/memory_mapped.py` | Memory-mapped writer |
| `examples/basic_usage.py` | Usage examples |
| `tests/test_*.py` | Unit tests |

## See Also

- `PLAN.md` — Design document and architecture decisions
