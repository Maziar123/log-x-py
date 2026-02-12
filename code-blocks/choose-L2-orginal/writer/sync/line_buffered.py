"""Line-buffered file writer.

Each line is flushed immediately (buffering=1).
Best for: Real-time logging, immediate durability.
"""

from writer.base import BaseFileWriterThread, Mode, Q  # noqa: F401


class LineBufferedWriter(BaseFileWriterThread):
    """Line-buffered file writer.
    
    Uses Python's line buffering (buffering=1) for immediate flush
    on each newline. Minimal latency but more syscalls.
    
    Example:
        q = Q()
        writer = LineBufferedWriter(q, "output.txt", Mode.TRIGGER)
        writer.send("line 1")  # Flushed immediately
        q.stop()
        writer.join()
    """

    def _write_batch(self, items: list[str]) -> None:
        """Write batch with line buffering."""
        if not items:
            return
        with open(self._path, "a", encoding="utf-8", buffering=1) as f:
            f.write("\n".join(items) + "\n")
            self._record(len(items))
