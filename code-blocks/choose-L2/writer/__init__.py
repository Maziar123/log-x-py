"""Choose-L2 async writer for logxpy.

Standalone writer implementation with three writer types:
- LineBufferedWriter: Immediate flush (real-time)
- BlockBufferedWriter: 64KB buffer (balanced, default)
- MemoryMappedWriter: OS-managed (max throughput)

And three operating modes:
- TRIGGER: Event-driven (wake on message)
- LOOP: Periodic poll
- MANUAL: Explicit trigger()
"""

from .base import (
    Q,
    QEmpty,
    Mode,
    WriterType,
    QueuePolicy,
    WriterMetrics,
    BaseFileWriterThread,
    LineBufferedWriter,
    BlockBufferedWriter,
    MemoryMappedWriter,
    create_writer,
)

__all__ = [
    # Core
    "Q", "QEmpty", "Mode", "WriterType", "QueuePolicy",
    "WriterMetrics", "BaseFileWriterThread",
    # Writers
    "LineBufferedWriter", "BlockBufferedWriter", "MemoryMappedWriter",
    # Factory
    "create_writer",
]

__version__ = "1.0.0"
