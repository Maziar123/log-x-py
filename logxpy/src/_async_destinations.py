"""Async-optimized destinations for the background writer thread.

Python 3.12+ features used:
- Type aliases (PEP 695): `type Destination = ...`
- override decorator (PEP 698): Explicit method overrides
- pathlib.Path integration for modern path handling

These destinations are optimized for use with AsyncWriter's background
thread. They use low-level OS operations for maximum performance.
"""

from __future__ import annotations

import contextlib
import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, override

if TYPE_CHECKING:
    from ._async_writer import LogBatch, SerializedLog
else:
    LogBatch = list
    SerializedLog = bytes


# ============================================================================
# Type Aliases (PEP 695 - Python 3.12+)
# ============================================================================

type PathLike = str | Path


# ============================================================================
# Base Async Destination Interface
# ============================================================================


class AsyncDestination(ABC):
    """Abstract base class for async-capable destinations.

    Destinations are called from the background writer thread.
    Implementations must be thread-safe.
    """

    __slots__ = ("_closed",)

    def __init__(self) -> None:
        self._closed = False

    @abstractmethod
    def write(self, data: SerializedLog) -> None:
        """Write data to the destination.

        Args:
            data: Serialized log data as bytes.
        """
        raise NotImplementedError

    @abstractmethod
    def flush(self) -> None:
        """Flush any buffered data."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Close the destination and release resources."""
        raise NotImplementedError

    @property
    def is_closed(self) -> bool:
        """Check if the destination is closed."""
        return self._closed

    def __call__(self, data: SerializedLog) -> None:
        """Make destination callable for use with AsyncWriter.

        Args:
            data: Serialized log data.
        """
        if not self._closed:
            self.write(data)


# ============================================================================
# File Destination with O_APPEND
# ============================================================================


class AsyncFileDestination(AsyncDestination):
    """File destination optimized for async batch writing.

    Uses O_APPEND for atomic writes at the OS level, ensuring that
even with multiple processes writing to the same file, each write
    is appended atomically.

    Features:
    - O_APPEND for atomic writes (no race conditions)
    - O_CLOEXEC to prevent fd leaking to child processes
    - Raw os.write() for minimal overhead
    - Optional fsync for durability

    Example:
        >>> dest = AsyncFileDestination("/var/log/app.log")
        >>> writer.add_destination(dest)
        >>> dest.close()  # When done
    """

    __slots__ = ("_fd", "_mode", "_path", "_use_fsync")

    def __init__(
        self,
        path: PathLike,
        *,
        mode: int = 0o644,
        use_fsync: bool = False,
        create_dirs: bool = True,
    ) -> None:
        """Initialize the file destination.

        Args:
            path: Path to the log file.
            mode: File permissions for new files (default: 0o644).
            use_fsync: Whether to fsync after each write (slower but durable).
            create_dirs: Whether to create parent directories if missing.
        """
        super().__init__()
        self._path = Path(path)
        self._mode = mode
        self._use_fsync = use_fsync
        self._fd: int | None = None

        # Create parent directories if needed
        if create_dirs:
            self._path.parent.mkdir(parents=True, exist_ok=True)

        # Open file with O_APPEND for atomic writes
        # O_CLOEXEC prevents fd from leaking to child processes
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_CLOEXEC

        # Use os.open for low-level control
        self._fd = os.open(self._path, flags, mode)

    @override
    def write(self, data: SerializedLog) -> None:
        """Write data to the file.

        Args:
            data: Serialized log data as bytes.

        Raises:
            IOError: If the file descriptor is invalid or write fails.
        """
        if self._fd is None or self._closed:
            raise OSError("File destination is closed")

        # Use os.write for raw I/O (faster than file.write)
        remaining = data
        while remaining:
            written = os.write(self._fd, remaining)
            if written == 0:
                raise OSError("Write returned 0 bytes")
            remaining = remaining[written:]

        if self._use_fsync:
            os.fsync(self._fd)

    def write_batch(self, batch: LogBatch) -> None:
        """Write a batch of messages efficiently.

        Uses writev if available for vectored I/O.

        Args:
            batch: List of serialized log messages.
        """
        if self._fd is None or self._closed:
            raise OSError("File destination is closed")

        if not batch:
            return

        # Concatenate all messages
        data = b"".join(batch)

        # Write in a single syscall
        remaining = data
        while remaining:
            written = os.write(self._fd, remaining)
            if written == 0:
                raise OSError("Write returned 0 bytes")
            remaining = remaining[written:]

        if self._use_fsync:
            os.fsync(self._fd)

    @override
    def flush(self) -> None:
        """Flush file buffers to disk."""
        if self._fd is not None and not self._closed:
            os.fsync(self._fd)

    @override
    def close(self) -> None:
        """Close the file descriptor."""
        if self._fd is not None and not self._closed:
            os.close(self._fd)
            self._fd = None
        self._closed = True

    def __enter__(self) -> AsyncFileDestination:
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()


# ============================================================================
# Console Destination (stdout/stderr)
# ============================================================================


class AsyncConsoleDestination(AsyncDestination):
    """Console destination for async logging.

    Writes to stdout by default, with optional stderr for errors.

    Note: On Windows, console output may have encoding issues with
    certain characters. This destination uses 'replace' error handling
    to avoid crashes.
    """

    __slots__ = ("_encoding", "_is_stderr", "_stream")

    def __init__(
        self,
        use_stderr: bool = False,
        encoding: str | None = None,
    ) -> None:
        """Initialize console destination.

        Args:
            use_stderr: Write to stderr instead of stdout.
            encoding: Text encoding. Defaults to stdout.encoding or 'utf-8'.
        """
        super().__init__()
        self._is_stderr = use_stderr
        self._stream = sys.stderr if use_stderr else sys.stdout
        self._encoding = encoding or getattr(
            self._stream, "encoding", None
        ) or "utf-8"

    @override
    def write(self, data: SerializedLog) -> None:
        """Write data to the console.

        Args:
            data: Serialized log data as bytes.
        """
        if self._closed:
            return

        try:
            # Decode and write, handling encoding errors gracefully
            text = data.decode(self._encoding, errors="replace")
            self._stream.write(text)
            self._stream.flush()
        except Exception:
            # Console errors should not crash the writer
            pass

    @override
    def flush(self) -> None:
        """Flush the console buffer."""
        if not self._closed:
            with contextlib.suppress(Exception):
                self._stream.flush()

    @override
    def close(self) -> None:
        """Close the destination (no-op for console)."""
        self._closed = True


# ============================================================================
# Rotating File Destination
# ============================================================================


class AsyncRotatingFileDestination(AsyncFileDestination):
    """Rotating file destination based on size.

    When the file reaches max_size, it's renamed with a timestamp
    and a new file is created.

    Note: Rotation is not perfectly thread-safe across multiple
    processes, but is safe within a single process.
    """

    __slots__ = ("_backup_count", "_current_size", "_max_size")

    def __init__(
        self,
        path: PathLike,
        *,
        max_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        mode: int = 0o644,
        use_fsync: bool = False,
    ) -> None:
        """Initialize rotating file destination.

        Args:
            path: Base path for log files.
            max_size: Maximum file size before rotation (bytes).
            backup_count: Number of backup files to keep.
            mode: File permissions for new files.
            use_fsync: Whether to fsync after writes.
        """
        super().__init__(path, mode=mode, use_fsync=use_fsync)
        self._max_size = max_size
        self._backup_count = backup_count
        self._current_size = self._path.stat().st_size if self._path.exists() else 0

    @override
    def write(self, data: SerializedLog) -> None:
        """Write data, rotating if necessary."""
        if self._should_rotate(len(data)):
            self._rotate()

        super().write(data)
        self._current_size += len(data)

    def _should_rotate(self, data_len: int) -> bool:
        """Check if we need to rotate the file."""
        return self._current_size + data_len > self._max_size

    def _rotate(self) -> None:
        """Rotate the log files."""
        # Close current file
        if self._fd is not None:
            os.close(self._fd)

        # Rotate existing backups
        for i in range(self._backup_count - 1, 0, -1):
            src = Path(f"{self._path}.{i}")
            dst = Path(f"{self._path}.{i + 1}")
            if src.exists():
                src.rename(dst)

        # Rename current file
        if self._path.exists():
            self._path.rename(f"{self._path}.1")

        # Reopen new file
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_CLOEXEC
        self._fd = os.open(self._path, flags, self._mode)
        self._current_size = 0


# ============================================================================
# Destination Proxy for Sync Destinations
# ============================================================================


class AsyncDestinationProxy:
    """Proxy that adapts sync destinations for async writer.

    Wraps existing sync destinations (like _output.FileDestination)
    so they can be used with AsyncWriter. Serializes the message
    before enqueueing to avoid ContextVar issues in the writer thread.

    Example:
        >>> from ._output import FileDestination
        >>> sync_dest = FileDestination(file=open("app.log", "a"))
        >>> proxy = AsyncDestinationProxy(sync_dest)
        >>> writer.add_destination(proxy)
    """

    __slots__ = ("_dest",)

    def __init__(self, dest: Any) -> None:
        """Initialize the proxy.

        Args:
            dest: A sync destination with __call__(message: dict).
        """
        self._dest = dest

    def __call__(self, data: SerializedLog) -> None:
        """Forward to the wrapped destination.

        Args:
            data: Serialized log data (JSON bytes with newline).
        """
        try:
            # Decode JSON and call the sync destination
            import json

            # Remove trailing newline for parsing
            text = data.decode("utf-8", errors="replace").rstrip("\n")
            message = json.loads(text)
            self._dest(message)
        except Exception:
            # Don't crash the writer thread
            pass


# ============================================================================
# Factory Functions
# ============================================================================


def create_file_destination(
    path: PathLike,
    *,
    rotating: bool = False,
    max_size: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    use_fsync: bool = False,
) -> AsyncFileDestination | AsyncRotatingFileDestination:
    """Create an appropriate file destination.

    Args:
        path: Path to the log file.
        rotating: Whether to enable log rotation.
        max_size: Maximum size before rotation (for rotating dest).
        backup_count: Number of backups to keep (for rotating dest).
        use_fsync: Whether to fsync after writes.

    Returns:
        AsyncFileDestination or AsyncRotatingFileDestination.
    """
    if rotating:
        return AsyncRotatingFileDestination(
            path=path,
            max_size=max_size,
            backup_count=backup_count,
            use_fsync=use_fsync,
        )
    return AsyncFileDestination(path=path, use_fsync=use_fsync)


def create_console_destination(use_stderr: bool = False) -> AsyncConsoleDestination:
    """Create a console destination.

    Args:
        use_stderr: Use stderr instead of stdout.

    Returns:
        AsyncConsoleDestination instance.
    """
    return AsyncConsoleDestination(use_stderr=use_stderr)


__all__ = [
    # Classes (sorted)
    "AsyncConsoleDestination",
    "AsyncDestination",
    "AsyncDestinationProxy",
    "AsyncFileDestination",
    "AsyncRotatingFileDestination",
    # Type aliases
    "PathLike",
    # Factory functions (sorted)
    "create_console_destination",
    "create_file_destination",
]
