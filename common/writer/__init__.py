"""Unified async writer library for Python 3.12+.

Production-ready file writer with 3 I/O strategies and 3 operational modes.
All classes use __slots__ for memory efficiency.

Example:
    >>> from common.writer import UnifiedWriter, WriterConfig, Mode
    >>> from common.writer.destinations import BlockBufferedDestination
    >>> 
    >>> config = WriterConfig(mode=Mode.TRIGGER, batch_size=100)
    >>> writer = UnifiedWriter(config)
    >>> writer.add_destination(BlockBufferedDestination("app.log"))
    >>> writer.start()
    >>> writer.enqueue(b"log line\n")
    >>> writer.stop()
"""

from __future__ import annotations

from common.writer.core import (
    Mode,
    QueuePolicy,
    UnifiedWriter,
    WriterConfig,
    WriterMetrics,
)
from common.writer.destinations import (
    BlockBufferedDestination,
    FileDestination,
    LineBufferedDestination,
    MemoryMappedDestination,
)

__version__ = "1.0.0"

__all__ = [
    # Core classes
    "UnifiedWriter",
    "WriterConfig",
    "WriterMetrics",
    # Enums
    "Mode",
    "QueuePolicy",
    # Destinations
    "FileDestination",
    "LineBufferedDestination",
    "BlockBufferedDestination",
    "MemoryMappedDestination",
]
