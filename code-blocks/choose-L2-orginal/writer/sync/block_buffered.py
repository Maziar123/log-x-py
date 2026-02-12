"""Block-buffered file writer.

64KB buffer reduces syscalls while maintaining good throughput.
Best for: High-throughput logging, batch processing.
"""

from writer.base import BaseFileWriterThread, Mode, Q  # noqa: F401


class BlockBufferedWriter(BaseFileWriterThread):
    """Block-buffered file writer with 64KB buffer.
    
    Uses 64KB file buffer to batch writes at kernel level.
    Fewer syscalls than line-buffered, good throughput.
    
    Example:
        q = Q()
        writer = BlockBufferedWriter(q, "output.txt", Mode.TRIGGER)
        for i in range(1000):
            writer.send(f"line {i}")
        q.stop()
        writer.join()
    """
    
    _BUFFER_SIZE = 65536

    def _write_batch(self, items: list[str]) -> None:
        """Write batch with 64KB buffering."""
        if not items:
            return
        with open(
            self._path, "a", encoding="utf-8", buffering=self._BUFFER_SIZE
        ) as f:
            f.write("\n".join(items) + "\n")
            self._record(len(items))
