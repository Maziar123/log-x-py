"""Choose-L2 based async writer for logxpy.

Provides three writer types:
- LineBufferedWriter: Immediate flush (real-time)
- BlockBufferedWriter: 64KB buffer (balanced, default)
- MemoryMappedWriter: OS-managed (max throughput)

And three operating modes:
- TRIGGER: Event-driven (wake on message)
- LOOP: Periodic poll
- MANUAL: Explicit trigger()
"""

from __future__ import annotations

import atexit
import mmap
import os
from abc import ABC, abstractmethod
from collections import deque
from enum import StrEnum
from pathlib import Path
from threading import Event, Thread
from typing import Any, final

_STOP = object()


class QEmpty(Exception):
    """Raised when Q.get() times out with no data."""


class Mode(StrEnum):
    """Writer operating mode."""
    TRIGGER = "trigger"
    LOOP = "loop"
    MANUAL = "manual"


class WriterType(StrEnum):
    """Writer implementation type."""
    LINE = "line"
    BLOCK = "block"
    MMAP = "mmap"


class QueuePolicy(StrEnum):
    """Backpressure policy."""
    BLOCK = "block"
    DROP_OLDEST = "drop_oldest"
    DROP_NEWEST = "drop_newest"
    WARN = "warn"


class Q:
    """Fast thread-safe queue using GIL-atomic deque operations.
    
    put() is GIL-atomic (no lock needed in CPython). Consumer blocks
    on Event, woken lazily. Uses _STOP sentinel to signal termination.
    """
    __slots__ = ("_d", "_event", "_stopped", "_maxsize")

    def __init__(self, maxsize: int = 0) -> None:
        self._d: deque[str | object] = deque()
        self._event = Event()
        self._stopped = False
        self._maxsize = maxsize

    def put(self, text: str, policy: QueuePolicy = QueuePolicy.BLOCK) -> bool:
        """Add item to queue. Thread-safe via GIL.
        
        Returns True if added, False if dropped.
        """
        if self._maxsize > 0 and len(self._d) >= self._maxsize:
            match policy:
                case QueuePolicy.BLOCK:
                    # SimpleQueue-like blocking behavior - just append
                    pass
                case QueuePolicy.DROP_NEWEST:
                    return False
                case QueuePolicy.DROP_OLDEST:
                    if self._d:
                        self._d.popleft()
                case QueuePolicy.WARN:
                    import warnings
                    warnings.warn("Queue full, dropping message", RuntimeWarning)
                    return False
        
        self._d.append(text)
        if not self._event.is_set():
            self._event.set()
        return True

    def get(self, timeout: float | None = None) -> str | None:
        """Blocking get. Returns None on stop sentinel."""
        # Fast path
        if self._d:
            item = self._d.popleft()
            if item is _STOP:
                self._stopped = True
                return None
            return item  # type: ignore[return-value]

        if self._stopped:
            return None

        # Slow path
        self._event.clear()
        
        if self._d:
            item = self._d.popleft()
            if item is _STOP:
                self._stopped = True
                return None
            return item  # type: ignore[return-value]

        self._event.wait(timeout=timeout)
        
        if self._d:
            item = self._d.popleft()
            if item is _STOP:
                self._stopped = True
                return None
            return item  # type: ignore[return-value]

        if self._stopped:
            return None
        if timeout is not None:
            raise QEmpty
        return None

    def drain(self) -> list[str]:
        """Drain all available items (stops at sentinel)."""
        items: list[str] = []
        while self._d:
            item = self._d.popleft()
            if item is _STOP:
                self._stopped = True
                break
            items.append(item)  # type: ignore[arg-type]
        return items

    def stop(self) -> None:
        """Signal queue to stop."""
        self._stopped = True
        self._d.append(_STOP)
        self._event.set()

    def has_data(self) -> bool:
        """Check if queue has data."""
        return bool(self._d)

    @property
    def stopped(self) -> bool:
        """True if stop sentinel processed."""
        return self._stopped
    
    def qsize(self) -> int:
        """Approximate queue size."""
        return len(self._d)


@final
class WriterMetrics:
    """Thread-safe writer metrics."""
    __slots__ = ("_enqueued", "_written", "_dropped", "_errors")
    
    def __init__(self) -> None:
        self._enqueued = 0
        self._written = 0
        self._dropped = 0
        self._errors = 0
    
    def record_enqueued(self) -> None:
        self._enqueued += 1
    
    def record_written(self, count: int = 1) -> None:
        self._written += count
    
    def record_dropped(self) -> None:
        self._dropped += 1
    
    def record_error(self) -> None:
        self._errors += 1
    
    @property
    def enqueued(self) -> int:
        return self._enqueued
    
    @property
    def written(self) -> int:
        return self._written
    
    @property
    def dropped(self) -> int:
        return self._dropped
    
    @property
    def errors(self) -> int:
        return self._errors
    
    @property
    def pending(self) -> int:
        return self._enqueued - self._written - self._dropped
    
    def get_snapshot(self) -> dict[str, int]:
        return {
            "enqueued": self._enqueued,
            "written": self._written,
            "dropped": self._dropped,
            "errors": self._errors,
            "pending": self.pending,
        }


class BaseFileWriterThread(ABC):
    """Abstract base for all file writers.
    
    Handles thread lifecycle, mode loops (TRIGGER/LOOP/MANUAL),
    batching, and statistics. Subclasses only implement _write_batch().
    """
    __slots__ = (
        "_q", "_mode", "_tick", "_path", "_closed",
        "_lines_written", "_flush_count", "_event", "_t",
        "_metrics", "_batch_size", "_flush_interval", "_policy",
        "_running", "_last_flush_time"
    )

    def __init__(
        self,
        q: Q,
        path: str | Path,
        mode: Mode = Mode.TRIGGER,
        *,
        running: bool = True,
        tick: float = 0.01,
        batch_size: int = 100,
        flush_interval: float = 0.1,
        policy: QueuePolicy = QueuePolicy.BLOCK,
    ) -> None:
        self._q = q
        self._path = Path(path)
        self._mode = mode
        self._tick = tick
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._policy = policy
        self._closed = False
        self._running = False
        self._lines_written = 0
        self._flush_count = 0
        self._last_flush_time = 0.0
        self._metrics = WriterMetrics()
        self._event = Event()
        
        # Ensure directory exists
        self._path.parent.mkdir(parents=True, exist_ok=True)
        
        if running:
            self._event.set()
            self._running = True
            self._last_flush_time = self._now()
        
        self._t = Thread(target=self._run_safe, daemon=True)
        self._t.start()
        atexit.register(self._cleanup)

    def _now(self) -> float:
        """Get current time."""
        import time
        return time.monotonic()

    # Public API
    @property
    def lines_written(self) -> int:
        """Total lines written to file."""
        return self._lines_written

    @property
    def flush_count(self) -> int:
        """Number of flush operations performed."""
        return self._flush_count
    
    @property
    def metrics(self) -> WriterMetrics:
        """Writer metrics."""
        return self._metrics
    
    @property
    def is_running(self) -> bool:
        """Check if writer thread is running."""
        return self._running and self._t.is_alive()

    def send(self, text: str) -> bool:
        """Send a line to be written."""
        if self._closed:
            raise RuntimeError("Writer closed")
        if self._metrics.record_enqueued() is None:  # type: ignore[func-returns-value]
            pass
        return self._q.put(text, self._policy)

    def trigger(self) -> None:
        """Trigger a write in MANUAL mode."""
        if self._mode is Mode.MANUAL:
            self._event.set()

    def join(self, timeout: float | None = None) -> bool:
        """Wait for writer thread to complete."""
        self._t.join(timeout=timeout)
        return not self._t.is_alive()

    def close(self) -> None:
        """Close the writer gracefully."""
        self._cleanup()
    
    def stop(self, timeout: float = 5.0) -> bool:
        """Stop the writer with timeout."""
        self._cleanup()
        return self.join(timeout)

    def __enter__(self) -> BaseFileWriterThread:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    # Internal
    def _run_safe(self) -> None:
        """Wrapper to catch exceptions in daemon thread."""
        try:
            self._run_mode_loop()
        except Exception:
            import sys
            self._metrics.record_error()
            print(f"Writer error: {sys.exc_info()[1]}", file=sys.stderr)

    def _run_mode_loop(self) -> None:
        """Dispatch to appropriate mode loop."""
        match self._mode:
            case Mode.TRIGGER:
                self._loop_trigger()
            case Mode.LOOP:
                self._loop_poll()
            case Mode.MANUAL:
                self._loop_manual()

    def _loop_trigger(self) -> None:
        """TRIGGER mode: wake on each message with batching."""
        q = self._q
        batch: list[str] = []
        last_flush = self._now()
        
        while True:
            try:
                msg = q.get(timeout=self._flush_interval)
            except QEmpty:
                # Timeout - flush any pending
                if batch:
                    self._write_batch(batch)
                    batch = []
                    last_flush = self._now()
                continue
                
            if msg is None:
                if batch:
                    self._write_batch(batch)
                break
            
            batch.append(msg)
            # Note: record_enqueued() already called in send()
            
            # Drain more messages
            drained = q.drain()
            batch.extend(drained)
            # Note: record_enqueued() already called in send() for drained messages
            
            # Check flush conditions
            now = self._now()
            elapsed = now - last_flush
            
            if len(batch) >= self._batch_size or elapsed >= self._flush_interval:
                self._write_batch(batch)
                batch = []
                last_flush = now

    def _loop_poll(self) -> None:
        """LOOP mode: timer-based periodic flushing.
        
        Uses flush_interval as the timer period. Messages are batched and
        flushed periodically, or immediately when batch_size is reached.
        """
        q = self._q
        batch: list[str] = []
        last_flush = self._now()
        
        # Use flush_interval as the loop timer period
        timer_period = self._flush_interval
        
        while not self._closed:
            # Wait for message with short timeout (responsive but efficient)
            if not q.has_data():
                self._event.wait(timeout=0.001)  # 1ms max wait
            
            # Collect all available messages (non-blocking)
            while True:
                if not q.has_data():
                    break
                try:
                    msg = q.get(timeout=0)
                    if msg is None:
                        # Stop signal - flush remaining batch
                        if batch:
                            self._write_batch(batch)
                        return
                    batch.append(msg)
                    # Note: record_enqueued() already called in send()
                except QEmpty:
                    break
            
            # Check flush conditions
            now = self._now()
            elapsed = now - last_flush
            
            if batch and (len(batch) >= self._batch_size or elapsed >= timer_period):
                self._write_batch(batch)
                batch = []
                last_flush = now
        
        # Drain remaining queue and flush on shutdown
        while True:
            if not q.has_data():
                break
            try:
                msg = q.get(timeout=0)
                if msg is None:
                    break
                batch.append(msg)
            except QEmpty:
                break
        
        # Flush any remaining messages when closing
        if batch:
            self._write_batch(batch)

    def _loop_manual(self) -> None:
        """MANUAL mode: trigger controls batch writes."""
        q = self._q
        
        while not self._closed:
            if not self._event.wait(timeout=0.05):
                if q.stopped:
                    self._closed = True
                    remaining = q.drain()
                    if remaining:
                        self._write_batch(remaining)
                    break
                continue
            
            if self._closed:
                break
            
            batch = q.drain()
            if q.stopped:
                self._closed = True
            
            if batch:
                # Note: record_enqueued() already called in send()
                self._write_batch(batch)
            
            self._event.clear()

    def _record(self, count: int) -> None:
        """Record statistics after a write."""
        if count > 0:
            self._lines_written += count
            self._flush_count += 1
            self._metrics.record_written(count)

    def _cleanup(self) -> None:
        """Cleanup on exit."""
        if not self._closed:
            self._closed = True
            self._running = False
            self._event.set()
            self._q.stop()
            self._t.join(timeout=2.0)
            atexit.unregister(self._cleanup)

    # Subclass contract
    @abstractmethod
    def _write_batch(self, items: list[str]) -> None:
        """Write batch of lines to file.
        
        Must be implemented by subclasses.
        Called by mode loops when data is ready to write.
        
        Args:
            items: List of strings to write (already joined with newlines)
        """
        ...


@final
class LineBufferedWriter(BaseFileWriterThread):
    """Line-buffered file writer.
    
    Each line is flushed immediately (buffering=1).
    Best for: Real-time logging, immediate durability.
    """

    def _write_batch(self, items: list[str]) -> None:
        """Write batch with line buffering."""
        if not items:
            return
        try:
            with open(self._path, "a", encoding="utf-8", buffering=1) as f:
                f.write("\n".join(items) + "\n")
            self._record(len(items))
        except Exception:
            self._metrics.record_error()
            raise


@final
class BlockBufferedWriter(BaseFileWriterThread):
    """Block-buffered file writer with 64KB buffer.
    
    Uses 64KB file buffer to batch writes at kernel level.
    Best for: High-throughput logging, batch processing.
    """
    
    _BUFFER_SIZE = 65536

    def _write_batch(self, items: list[str]) -> None:
        """Write batch with 64KB buffering."""
        if not items:
            return
        try:
            with open(
                self._path, "a", encoding="utf-8", buffering=self._BUFFER_SIZE
            ) as f:
                f.write("\n".join(items) + "\n")
            self._record(len(items))
        except Exception:
            self._metrics.record_error()
            raise


@final
class MemoryMappedWriter(BaseFileWriterThread):
    """Memory-mapped file writer.
    
    Maps file into memory for zero-copy writes. OS handles
    flushing asynchronously. Best throughput for large batches.
    """
    
    _PREALLOC = 32 * 1024 * 1024  # 32MB initial
    
    __slots__ = ("_mm", "_fd", "_offset")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._mm: mmap.mmap | None = None
        self._fd: int | None = None
        self._offset = 0
        super().__init__(*args, **kwargs)

    def _write_batch(self, items: list[str]) -> None:
        """Write batch via memory mapping."""
        if not items:
            return
        
        data = ("\n".join(items) + "\n").encode("utf-8")
        
        # Check if we need to mmap
        if self._mm is None:
            # First write - setup mmap
            self._fd = os.open(self._path, os.O_RDWR | os.O_CREAT)
            os.ftruncate(self._fd, self._PREALLOC)
            self._mm = mmap.mmap(self._fd, self._PREALLOC)
            self._offset = 0
        
        # Write to mmap
        end = self._offset + len(data)
        if end > self._PREALLOC:
            raise RuntimeError(f"File size exceeded preallocation ({self._PREALLOC} bytes)")
        
        if self._mm is not None:
            self._mm[self._offset:end] = data
            self._offset = end
        
        self._record(len(items))
    
    def _cleanup(self) -> None:
        """Cleanup: flush mmap and truncate."""
        if self._mm is not None and not self._mm.closed:
            self._mm.flush()
            self._mm.close()
            self._mm = None
            if self._fd is not None:
                os.ftruncate(self._fd, self._offset)
                os.close(self._fd)
                self._fd = None
        
        super()._cleanup()


def create_writer(
    path: str | Path,
    writer_type: WriterType = WriterType.BLOCK,
    mode: Mode = Mode.TRIGGER,
    queue_size: int = 10_000,
    batch_size: int = 100,
    flush_interval: float = 0.1,
    tick: float = 0.01,
    policy: QueuePolicy = QueuePolicy.BLOCK,
) -> BaseFileWriterThread:
    """Factory function to create appropriate writer.
    
    Args:
        path: Output file path
        writer_type: LINE, BLOCK, or MMAP
        mode: TRIGGER, LOOP, or MANUAL
        queue_size: Max queue size (0=unlimited)
        batch_size: Messages per batch
        flush_interval: Seconds between flushes
        tick: Poll interval for LOOP mode
        policy: Backpressure policy
    
    Returns:
        Configured writer instance
    """
    q = Q(maxsize=queue_size)
    
    kwargs = {
        "batch_size": batch_size,
        "flush_interval": flush_interval,
        "tick": tick,
        "policy": policy,
    }
    
    match writer_type:
        case WriterType.LINE:
            return LineBufferedWriter(q, path, mode, **kwargs)
        case WriterType.MMAP:
            return MemoryMappedWriter(q, path, mode, **kwargs)
        case _:
            return BlockBufferedWriter(q, path, mode, **kwargs)


__all__ = [
    # Core
    "Q", "QEmpty", "Mode", "WriterType", "QueuePolicy",
    "BaseFileWriterThread", "WriterMetrics",
    # Writers
    "LineBufferedWriter", "BlockBufferedWriter", "MemoryMappedWriter",
    # Factory
    "create_writer",
]
