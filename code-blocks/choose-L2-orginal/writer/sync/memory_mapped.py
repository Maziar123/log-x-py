"""Memory-mapped file writer.

Uses mmap for zero-copy I/O. OS handles async flushing.
Best for: Maximum throughput, OS-managed persistence.
"""

import mmap
import os

from writer.base import BaseFileWriterThread, Mode, Q  # noqa: F401

_PREALLOC = 32 * 1024 * 1024  # 32MB initial


class MemoryMappedWriter(BaseFileWriterThread):
    """Memory-mapped file writer.
    
    Maps file into memory for zero-copy writes. OS handles
    flushing asynchronously. Best throughput for large batches.
    
    Pre-allocates 32MB and truncates to actual size on close.
    
    Example:
        q = Q()
        writer = MemoryMappedWriter(q, "output.txt", Mode.TRIGGER)
        for i in range(10000):
            writer.send(f"line {i}")
        q.stop()
        writer.join()
    """

    def _write_batch(self, items: list[str]) -> None:
        """Write batch via memory mapping."""
        if not items:
            return
        
        data = ("\n".join(items) + "\n").encode("utf-8")
        offset = getattr(self, "_offset", 0)
        
        # Check if we need to mmap
        mm = getattr(self, "_mm", None)
        fd = getattr(self, "_fd", None)
        
        if mm is None:
            # First write - setup mmap
            fd = os.open(self._path, os.O_RDWR | os.O_CREAT)
            os.ftruncate(fd, _PREALLOC)
            mm = mmap.mmap(fd, _PREALLOC)
            self._fd = fd
            self._mm = mm
            self._offset = 0
            offset = 0
        
        # Write to mmap
        end = offset + len(data)
        if end > _PREALLOC:
            raise RuntimeError(f"File size exceeded preallocation ({_PREALLOC} bytes)")
        
        mm[offset:end] = data
        self._offset = end
        self._record(len(items))
    
    def _cleanup(self) -> None:
        """Cleanup: flush mmap and truncate."""
        mm = getattr(self, "_mm", None)
        fd = getattr(self, "_fd", None)
        offset = getattr(self, "_offset", 0)

        if mm is not None and not mm.closed:
            mm.flush()
            mm.close()
            self._mm = None
            if fd is not None:
                os.ftruncate(fd, offset)
                os.close(fd)
                self._fd = None

        super()._cleanup()
