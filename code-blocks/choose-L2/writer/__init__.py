"""Unified file writer library.

Default: BlockBufferedWriter (64KB buffer, best overall performance)
"""

from writer.base import BaseFileWriterThread, Mode, Q, QEmpty
from writer.sync.block_buffered import BlockBufferedWriter as FileWriter

__all__ = ["BaseFileWriterThread", "FileWriter", "Mode", "Q", "QEmpty"]
