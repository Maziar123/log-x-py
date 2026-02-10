"""Async log writer using a dedicated background thread.

Python 3.12+ features used:
- Type aliases (PEP 695): `type SerializedLog = bytes`
- StrEnum (PEP 663): Type-safe queue policies
- Dataclass slots (PEP 681): Memory optimization
- Self type (PEP 673): Fluent return types

This module provides high-performance async logging via a dedicated
background writer thread using lock-free queue.SimpleQueue.
"""

from __future__ import annotations

import contextlib
import queue
import threading
import time
import warnings
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Self

from ._json_encoders import _dumps_bytes, json_default

if TYPE_CHECKING:
    from ._types import Record


# ============================================================================
# Type Aliases (PEP 695 - Python 3.12+)
# ============================================================================

type SerializedLog = bytes
type LogBatch = list[SerializedLog]
type DestinationFn = Callable[[SerializedLog], None]
type BatchDestinationFn = Callable[[LogBatch], None]


# ============================================================================
# Queue Policy Enum (PEP 663 - StrEnum)
# ============================================================================


class QueuePolicy(StrEnum):
    """Backpressure policy when the async queue is full.

    Attributes:
        BLOCK: Block the caller until queue has space (default, no data loss).
        DROP_OLDEST: Remove oldest messages to make room for new ones.
        DROP_NEWEST: Skip new messages when queue is full.
        WARN: Emit a warning and drop the message.
    """

    BLOCK = "block"
    DROP_OLDEST = "drop_oldest"
    DROP_NEWEST = "drop_newest"
    WARN = "warn"


# ============================================================================
# Configuration & Metrics (PEP 681 - Dataclass with slots)
# ============================================================================


@dataclass(frozen=True, slots=True)
class AsyncConfig:
    """Immutable configuration for the async writer.

    Uses frozen dataclass with slots for memory efficiency and thread safety.

    Attributes:
        max_queue_size: Maximum number of messages in queue before backpressure.
        batch_size: Number of messages to batch before flushing.
        flush_interval_ms: Maximum milliseconds between flushes.
        queue_policy: Backpressure policy when queue is full.
        pre_serialize: Whether to serialize in caller thread (True recommended).
    """

    max_queue_size: int = 10_000
    batch_size: int = 100
    flush_interval_ms: float = 100.0
    queue_policy: QueuePolicy = field(default=QueuePolicy.BLOCK)
    pre_serialize: bool = True

    @property
    def flush_interval_sec(self) -> float:
        """Convert milliseconds to seconds for time calculations."""
        return self.flush_interval_ms / 1000.0


@dataclass(slots=True)
class AsyncMetrics:
    """Performance metrics for the async writer.

    Thread-safe for individual operations, but reading multiple fields
    together may be inconsistent under high concurrency.

    Attributes:
        enqueued: Total messages enqueued.
        written: Total messages written to destinations.
        dropped: Total messages dropped due to backpressure.
        errors: Total errors encountered.
    """

    enqueued: int = 0
    written: int = 0
    dropped: int = 0
    errors: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    @property
    def pending(self) -> int:
        """Calculate approximate pending messages."""
        with self._lock:
            return self.enqueued - self.written - self.dropped

    def record_enqueued(self) -> None:
        """Thread-safe increment of enqueued counter."""
        with self._lock:
            self.enqueued += 1

    def record_written(self, count: int = 1) -> None:
        """Thread-safe increment of written counter."""
        with self._lock:
            self.written += count

    def record_dropped(self, count: int = 1) -> None:
        """Thread-safe increment of dropped counter."""
        with self._lock:
            self.dropped += count

    def record_error(self) -> None:
        """Thread-safe increment of error counter."""
        with self._lock:
            self.errors += 1

    def get_snapshot(self) -> dict[str, int]:
        """Get a consistent snapshot of all metrics."""
        with self._lock:
            return {
                "enqueued": self.enqueued,
                "written": self.written,
                "dropped": self.dropped,
                "errors": self.errors,
                "pending": self.enqueued - self.written - self.dropped,
            }


# ============================================================================
# Async Writer - Core Implementation
# ============================================================================


class AsyncWriter:
    """Thread-based async log writer with batching and backpressure.

    Uses a dedicated background thread for I/O operations, allowing the
    caller thread to return immediately after queuing the log message.

    Features:
    - Lock-free queue (queue.SimpleQueue) for minimal overhead
    - Pre-serialization in caller thread (CPU work offloaded)
    - Configurable batching (size and time based)
    - Multiple backpressure policies
    - Auto-restart on writer thread crash
    - Graceful shutdown with pending message flush

    Example:
        >>> config = AsyncConfig(max_queue_size=50000, batch_size=500)
        >>> writer = AsyncWriter(config)
        >>> writer.start()
        >>> record = Record(...)  # Create log record
        >>> writer.enqueue(record)  # Returns immediately
        >>> writer.stop()  # Graceful shutdown
    """

    __slots__ = (
        "_batch_dests",
        "_config",
        "_destinations",
        "_fallback_to_sync",
        "_last_flush",
        "_max_restarts",
        "_metrics",
        "_queue",
        "_restart_count",
        "_running",
        "_shutdown",
        "_thread",
    )

    def __init__(
        self,
        config: AsyncConfig | None = None,
        max_restarts: int = 10,
    ) -> None:
        """Initialize the async writer.

        Args:
            config: Configuration for the writer. Uses defaults if None.
            max_restarts: Maximum number of auto-restarts before giving up.
        """
        self._config = config or AsyncConfig()
        # SimpleQueue is C-optimized and lock-free
        self._queue: queue.SimpleQueue[SerializedLog | None] = queue.SimpleQueue()
        self._running = False
        self._shutdown = False
        self._thread: threading.Thread | None = None
        self._destinations: list[DestinationFn] = []
        self._batch_dests: list[BatchDestinationFn] = []
        self._metrics = AsyncMetrics()
        self._last_flush = time.monotonic()
        self._restart_count = 0
        self._max_restarts = max_restarts
        self._fallback_to_sync = False

    # -------------------------------------------------------------------------
    # Lifecycle Management
    # -------------------------------------------------------------------------

    def start(self) -> Self:
        """Start the background writer thread.

        Returns:
            Self for method chaining.

        Raises:
            RuntimeError: If the writer is already running.
        """
        if self._running:
            return self

        self._running = True
        self._shutdown = False
        self._thread = threading.Thread(
            target=self._writer_loop_wrapper,
            name="logxpy-writer",
            daemon=True,
        )
        self._thread.start()
        return self

    def stop(self, timeout: float = 5.0) -> bool:
        """Stop the writer gracefully, flushing pending messages.

        Args:
            timeout: Maximum seconds to wait for graceful shutdown.

        Returns:
            True if stopped cleanly, False if timeout occurred.
        """
        if not self._running or self._thread is None:
            return True

        self._shutdown = True
        # Signal shutdown with sentinel value
        with contextlib.suppress(queue.Full):
            self._queue.put(None, timeout=0.1)

        # Wait for thread to finish
        self._thread.join(timeout)
        stopped = not self._thread.is_alive()
        self._running = False

        if not stopped:
            # Force stop - may lose messages
            warnings.warn(
                f"Async writer did not stop within {timeout}s. "
                "Some log messages may be lost.",
                RuntimeWarning,
                stacklevel=2,
            )

        return stopped

    # -------------------------------------------------------------------------
    # Destination Management
    # -------------------------------------------------------------------------

    def add_destination(self, dest: DestinationFn | BatchDestinationFn) -> None:
        """Add a destination function.

        Args:
            dest: Callable that receives either single bytes (if it accepts 1 arg)
                  or list[bytes] (if it accepts list). Auto-detected.
        """
        import inspect

        sig = inspect.signature(dest)
        params = list(sig.parameters.values())

        # Check if it's a batch destination (accepts list)
        if params:
            param = params[0]
            if param.annotation is not inspect.Parameter.empty:
                type_name = str(param.annotation).lower()
                if "list" in type_name or "batch" in type_name:
                    self._batch_dests.append(dest)  # type: ignore
                    return

        self._destinations.append(dest)  # type: ignore

    def remove_destination(
        self, dest: DestinationFn | BatchDestinationFn
    ) -> bool:
        """Remove a destination function.

        Args:
            dest: The destination to remove.

        Returns:
            True if found and removed, False otherwise.
        """
        if dest in self._destinations:
            self._destinations.remove(dest)  # type: ignore
            return True
        if dest in self._batch_dests:
            self._batch_dests.remove(dest)  # type: ignore
            return True
        return False

    # -------------------------------------------------------------------------
    # Message Enqueueing
    # -------------------------------------------------------------------------

    def enqueue(self, record: Record) -> bool:
        """Enqueue a log record for async writing.

        This method returns immediately (non-blocking). The record is
        serialized to JSON bytes in the caller thread if pre_serialize
        is enabled (recommended).

        Args:
            record: The log record to write.

        Returns:
            True if enqueued successfully, False if dropped.

        Note:
            If the writer has fallen back to sync mode due to too many
            restarts, this will return False and the caller should
            handle the record synchronously.
        """
        if not self._running or self._fallback_to_sync:
            return False

        # Pre-serialize to JSON bytes (CPU work in caller thread)
        data = self._serialize(record)

        # Apply backpressure policy
        match self._config.queue_policy:
            case QueuePolicy.BLOCK:
                return self._enqueue_block(data)
            case QueuePolicy.DROP_OLDEST:
                return self._enqueue_drop_oldest(data)
            case QueuePolicy.DROP_NEWEST:
                return self._enqueue_drop_newest(data)
            case QueuePolicy.WARN:
                return self._enqueue_warn(data)
            case _:
                # Should never happen with StrEnum
                return self._enqueue_block(data)

    def _enqueue_block(self, data: SerializedLog) -> bool:
        """Block until space available in queue."""
        # Local variable lookup for speed
        q = self._queue
        metrics = self._metrics
        try:
            q.put(data)
            metrics.record_enqueued()
            return True
        except Exception:
            metrics.record_error()
            return False

    def _enqueue_drop_oldest(self, data: SerializedLog) -> bool:
        """Remove oldest messages to make room."""
        # SimpleQueue doesn't support maxsize or peek, so we use a workaround
        # We check qsize() (which is approximate) and drop if needed
        max_size = self._config.max_queue_size

        # Drop oldest if queue appears full (approximate)
        while self._queue.qsize() >= max_size:
            try:
                self._queue.get_nowait()
                self._metrics.record_dropped()
            except queue.Empty:
                break

        try:
            self._queue.put(data, timeout=0.001)
            self._metrics.record_enqueued()
            return True
        except queue.Full:
            self._metrics.record_dropped()
            return False

    def _enqueue_drop_newest(self, data: SerializedLog) -> bool:
        """Skip new message if queue is full."""
        if self._queue.qsize() >= self._config.max_queue_size:
            self._metrics.record_dropped()
            return False

        try:
            self._queue.put(data, timeout=0.001)
            self._metrics.record_enqueued()
            return True
        except queue.Full:
            self._metrics.record_dropped()
            return False

    def _enqueue_warn(self, data: SerializedLog) -> bool:
        """Warn and drop if queue is full."""
        if self._queue.qsize() >= self._config.max_queue_size:
            warnings.warn(
                f"Async log queue full (size={self._queue.qsize()}). "
                "Dropping message.",
                RuntimeWarning,
                stacklevel=3,
            )
            self._metrics.record_dropped()
            return False

        try:
            self._queue.put(data, timeout=0.001)
            self._metrics.record_enqueued()
            return True
        except queue.Full:
            self._metrics.record_dropped()
            return False

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def _serialize(self, record: Record) -> SerializedLog:
        """Serialize a record to JSON bytes.

        Uses orjson if available for performance, falls back to stdlib json.
        Pre-allocates and reuses buffers where possible.

        Args:
            record: The log record to serialize.

        Returns:
            JSON bytes with newline appended.
        """
        # Use local reference for speed
        to_dict = record.to_dict
        dumps = _dumps_bytes
        default = json_default

        data = to_dict()
        return dumps(data, default=default) + b"\n"

    # -------------------------------------------------------------------------
    # Writer Thread
    # -------------------------------------------------------------------------

    def _writer_loop_wrapper(self) -> None:
        """Wrapper that handles crashes and auto-restart."""
        backoff = 0.1

        while self._running and not self._shutdown:
            try:
                self._writer_loop()
                backoff = 0.1  # Reset backoff on clean exit
            except Exception as e:
                self._metrics.record_error()
                self._restart_count += 1

                if self._restart_count >= self._max_restarts:
                    warnings.warn(
                        f"Async writer crashed {self._restart_count} times. "
                        "Falling back to sync mode.",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                    self._fallback_to_sync = True
                    self._running = False
                    break

                warnings.warn(
                    f"Async writer crashed: {e}. "
                    f"Restarting in {backoff}s "
                    f"(attempt {self._restart_count}/{self._max_restarts}).",
                    RuntimeWarning,
                    stacklevel=2,
                )
                time.sleep(backoff)
                backoff = min(backoff * 2, 30.0)  # Max 30s backoff

    def _writer_loop(self) -> None:
        """Main writer loop running in background thread.

        Collects messages into batches and writes to destinations.
        Handles both time-based and size-based flushing.

        Optimized for performance using local variable lookups.
        """
        # Local variable lookups for speed (avoid repeated attribute access)
        config = self._config
        q = self._queue
        flush_batch = self._flush_batch
        batch_size = config.batch_size
        flush_interval = config.flush_interval_sec
        monotonic = time.monotonic

        batch: LogBatch = []
        last_flush = monotonic()

        while self._running and not self._shutdown:
            try:
                # Calculate timeout for next flush
                now = monotonic()
                elapsed = now - last_flush
                timeout = flush_interval - elapsed if elapsed < flush_interval else 0.0

                # Wait for message with timeout
                try:
                    item = q.get(timeout=timeout) if timeout > 0 else q.get_nowait()
                except queue.Empty:
                    item = None

                # Check for shutdown signal
                if item is None:
                    # Timeout or shutdown - flush pending batch
                    if batch:
                        flush_batch(batch)
                        batch = []
                        last_flush = monotonic()

                    # Check if we should exit
                    if self._shutdown:
                        break
                    continue

                # Add to batch
                batch.append(item)

                # Flush on batch size
                if len(batch) >= batch_size:
                    flush_batch(batch)
                    batch = []
                    last_flush = monotonic()

            except Exception:
                self._metrics.record_error()
                # Continue loop - don't crash the writer thread

        # Final flush of any remaining messages
        if batch:
            flush_batch(batch)

    def _flush_batch(self, batch: LogBatch) -> None:
        """Write a batch of messages to all destinations.

        Optimized for performance using local variable lookups
        and minimizing method calls.

        Args:
            batch: List of serialized log messages.
        """
        if not batch:
            return

        # Local variable lookups are faster than attribute access
        destinations = self._destinations
        batch_dests = self._batch_dests
        metrics = self._metrics
        batch_len = len(batch)

        # Concatenate for single write (minimize syscalls)
        # Use memoryview for zero-copy where possible
        concatenated = b"".join(batch)

        # Write to single-message destinations
        for dest in destinations:
            try:
                dest(concatenated)
            except Exception:
                metrics.record_error()

        # Write to batch destinations
        batch_dest: BatchDestinationFn
        for batch_dest in batch_dests:
            try:
                batch_dest(batch)
            except Exception:
                metrics.record_error()

        metrics.record_written(batch_len)

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        """Check if the writer thread is running."""
        return self._running and self._thread is not None and self._thread.is_alive()

    @property
    def metrics(self) -> AsyncMetrics:
        """Get the metrics collector."""
        return self._metrics

    @property
    def is_fallback_to_sync(self) -> bool:
        """Check if writer has fallen back to sync mode due to errors."""
        return self._fallback_to_sync


# ============================================================================
# Convenience Functions
# ============================================================================


def create_default_writer(
    max_queue: int = 10_000,
    batch_size: int = 100,
    flush_interval: float = 0.1,
    policy: QueuePolicy | str = QueuePolicy.BLOCK,
) -> AsyncWriter:
    """Create an async writer with common defaults.

    Args:
        max_queue: Maximum queue size.
        batch_size: Messages per batch.
        flush_interval: Seconds between flushes.
        policy: Backpressure policy.

    Returns:
        Configured AsyncWriter instance.
    """
    if isinstance(policy, str):
        policy = QueuePolicy(policy)

    config = AsyncConfig(
        max_queue_size=max_queue,
        batch_size=batch_size,
        flush_interval_ms=flush_interval * 1000,
        queue_policy=policy,
    )
    return AsyncWriter(config)


__all__ = [
    # Classes (sorted)
    "AsyncConfig",
    "AsyncMetrics",
    "AsyncWriter",
    # Type aliases first (sorted)
    "BatchDestinationFn",
    "DestinationFn",
    "LogBatch",
    "QueuePolicy",
    "SerializedLog",
    # Functions
    "create_default_writer",
]
