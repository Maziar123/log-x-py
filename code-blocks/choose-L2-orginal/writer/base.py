"""Base file writer infrastructure.

Provides:
- BaseFileWriterThread: Abstract base with 3 mode implementations
- Q: Fast thread-safe queue
- Mode: Enum for TRIGGER/LOOP/MANUAL
- QEmpty: Exception for timeout
"""

from __future__ import annotations

import atexit
from abc import ABC, abstractmethod
from collections import deque
from enum import Enum, auto
from threading import Event, Thread

_STOP = object()


class QEmpty(Exception):
    """Raised when Q.get() times out with no data."""


class Mode(Enum):
    """Writer thread operating mode."""
    TRIGGER = auto()  # Wake on message via Event
    LOOP = auto()     # Poll every tick seconds
    MANUAL = auto()   # Main calls trigger()


class Q:
    """Fast thread-safe queue using GIL-atomic deque operations.
    
    put() is GIL-atomic (no lock needed in CPython). Consumer blocks
    on Event, woken lazily. Uses _STOP sentinel to signal termination.
    """
    __slots__ = ("_d", "_event", "_stopped")

    def __init__(self) -> None:
        self._d: deque[str | object] = deque()
        self._event = Event()
        self._stopped = False

    def put(self, text: str) -> None:
        """Add item to queue. Thread-safe via GIL."""
        self._d.append(text)
        if not self._event.is_set():
            self._event.set()

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


class BaseFileWriterThread(ABC):
    """Abstract base for all file writers.
    
    Handles thread lifecycle, mode loops (TRIGGER/LOOP/MANUAL),
    batching, and statistics. Subclasses only implement _write_batch().
    
    Usage:
        q = Q()
        writer = MyWriter(q, "output.txt", Mode.TRIGGER)
        writer.send("line 1")
        writer.send("line 2")
        q.stop()
        writer.join()
    """
    __slots__ = (
        "_q", "_mode", "_tick", "_path", "_closed",
        "_lines_written", "_flush_count", "_event", "_t"
    )

    def __init__(
        self,
        q: Q,
        path: str,
        mode: Mode = Mode.TRIGGER,
        *,
        running: bool = True,
        tick: float = 0.01,
    ) -> None:
        self._q = q
        self._path = path
        self._mode = mode
        self._tick = tick
        self._closed = False
        self._lines_written = 0
        self._flush_count = 0
        self._event = Event()
        if running:
            self._event.set()
        
        self._t = Thread(target=self._run_safe, daemon=True)
        self._t.start()
        atexit.register(self._cleanup)

    # Public API
    @property
    def lines_written(self) -> int:
        """Total lines written to file."""
        return self._lines_written

    @property
    def flush_count(self) -> int:
        """Number of flush operations performed."""
        return self._flush_count

    def send(self, text: str) -> None:
        """Send a line to be written."""
        if self._closed:
            raise RuntimeError("Writer closed")
        self._q.put(text)

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
            print(f"Writer error: {sys.exc_info()[1]}", file=sys.stderr)

    def _run_mode_loop(self) -> None:
        """Dispatch to appropriate mode loop."""
        if self._mode is Mode.TRIGGER:
            self._loop_trigger()
        elif self._mode is Mode.LOOP:
            self._loop_poll()
        else:
            self._loop_manual()

    def _loop_trigger(self) -> None:
        """TRIGGER mode: wake on each message."""
        q = self._q
        while True:
            msg = q.get()
            if msg is None:
                break
            self._event.wait()
            batch = [msg, *q.drain()]
            self._write_batch(batch)

    def _loop_poll(self) -> None:
        """LOOP mode: poll every tick seconds."""
        q = self._q
        while not self._closed:
            self._event.wait()
            try:
                msg = q.get(timeout=self._tick)
            except QEmpty:
                continue
            if msg is None:
                break
            batch = [msg, *q.drain()]
            self._write_batch(batch)

    def _loop_manual(self) -> None:
        """MANUAL mode: trigger controls batch writes."""
        q = self._q
        while not self._closed:
            if not self._event.wait(timeout=0.05):
                if q.stopped:
                    self._closed = True
                    self._write_batch(q.drain())
                    break
                continue
            if self._closed:
                break
            batch = q.drain()
            if q.stopped:
                self._closed = True
            self._write_batch(batch)
            self._event.clear()

    def _record(self, count: int) -> None:
        """Record statistics after a write."""
        if count > 0:
            self._lines_written += count
            self._flush_count += 1

    def _cleanup(self) -> None:
        """Cleanup on exit."""
        if not self._closed:
            self._closed = True
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
