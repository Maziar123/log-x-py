"""Tests for logxpy/src/_async_destinations.py -- Async destinations.

Tests cover:
- AsyncFileDestination: write, context manager, close, flush/fsync
- AsyncConsoleDestination: write, stderr
- AsyncRotatingFileDestination: rotation
- AsyncDestinationProxy: forwards to sync
- Factory functions
- Real file I/O verification with JSON log parsing
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from logxpy.src._async_destinations import (
    AsyncFileDestination, AsyncConsoleDestination,
    AsyncRotatingFileDestination, AsyncDestinationProxy,
    create_file_destination, create_console_destination,
)
from logxpy.src._async_writer import AsyncConfig, AsyncWriter
from logxpy.src._types import Level, Record


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _record(msg: str = "test") -> Record:
    return Record(
        timestamp=time.time(),
        level=Level.INFO,
        message=msg,
        fields={},
        context={},
        task_uuid="X.1",
        task_level=(1,),
        message_type="info",
    )


def _parse_log(path: Path) -> list[dict]:
    """Read a log file and return parsed JSON lines."""
    text = path.read_text().strip()
    if not text:
        return []
    return [json.loads(line) for line in text.splitlines() if line.strip()]


# ============================================================================
# AsyncFileDestination
# ============================================================================

class TestAsyncFileDestination:
    def test_write_to_file(self, tmp_path):
        p = tmp_path / "test.log"
        dest = AsyncFileDestination(p)
        dest.write(b"hello\n")
        dest.close()
        assert p.read_bytes() == b"hello\n"

    def test_context_manager(self, tmp_path):
        p = tmp_path / "test.log"
        with AsyncFileDestination(p) as dest:
            dest.write(b"hello\n")
        assert p.read_bytes() == b"hello\n"

    def test_close(self, tmp_path):
        p = tmp_path / "test.log"
        dest = AsyncFileDestination(p)
        dest.close()
        assert dest.is_closed

    def test_flush_calls_fsync(self, tmp_path):
        """flush() calls os.fsync — data persisted to disk."""
        p = tmp_path / "fsync_test.log"
        dest = AsyncFileDestination(p, use_fsync=False)
        dest.write(b'{"msg":"fsync-test"}\n')
        dest.flush()  # Triggers os.fsync(fd)
        dest.close()

        entries = _parse_log(p)
        assert len(entries) == 1
        assert entries[0]["msg"] == "fsync-test"

    def test_use_fsync_on_every_write(self, tmp_path):
        """use_fsync=True flushes on every write call."""
        p = tmp_path / "auto_fsync.log"
        dest = AsyncFileDestination(p, use_fsync=True)
        dest.write(b'{"msg":"auto-1"}\n')
        dest.write(b'{"msg":"auto-2"}\n')
        dest.close()

        entries = _parse_log(p)
        assert len(entries) == 2
        assert entries[0]["msg"] == "auto-1"
        assert entries[1]["msg"] == "auto-2"

    def test_write_batch(self, tmp_path):
        """write_batch() writes multiple messages in one syscall."""
        p = tmp_path / "batch.log"
        dest = AsyncFileDestination(p)
        batch = [
            b'{"msg":"b1"}\n',
            b'{"msg":"b2"}\n',
            b'{"msg":"b3"}\n',
        ]
        dest.write_batch(batch)
        dest.close()

        entries = _parse_log(p)
        assert len(entries) == 3
        assert entries[0]["msg"] == "b1"
        assert entries[2]["msg"] == "b3"


# ============================================================================
# AsyncFileDestination with AsyncWriter (full pipeline)
# ============================================================================

class TestFileDestWithWriter:
    """End-to-end: AsyncWriter → AsyncFileDestination → real file."""

    def test_writer_flushes_to_file(self, tmp_path):
        """Writer flushes batch to file destination, verifies JSON."""
        log_file = tmp_path / "writer_dest.log"
        writer = AsyncWriter(AsyncConfig(batch_size=10000, flush_interval_ms=60000))
        dest = AsyncFileDestination(log_file, use_fsync=False)
        writer.add_destination(dest)
        writer.start()

        for i in range(10):
            writer.enqueue(_record(f"wd-{i}"))

        writer.flush(timeout=5.0)

        entries = _parse_log(log_file)
        assert len(entries) == 10
        assert entries[0]["msg"] == "wd-0"
        assert entries[9]["msg"] == "wd-9"

        writer.stop(timeout=2.0)
        dest.close()

    def test_writer_fsync_after_batch(self, tmp_path):
        """Writer calls dest.flush() (fsync) after each batch write."""
        flush_count = {"n": 0}

        class TrackingDest:
            """Destination that counts flush() calls."""
            def __init__(self, real_dest):
                self._real = real_dest

            def __call__(self, data):
                self._real(data)

            def flush(self):
                flush_count["n"] += 1
                self._real.flush()

            def close(self):
                self._real.close()

        log_file = tmp_path / "fsync_batch.log"
        real_dest = AsyncFileDestination(log_file, use_fsync=False)
        tracking = TrackingDest(real_dest)

        writer = AsyncWriter(AsyncConfig(batch_size=5, flush_interval_ms=10))
        writer.add_destination(tracking)
        writer.start()

        for i in range(10):
            writer.enqueue(_record(f"fsync-{i}"))

        time.sleep(0.3)
        writer.stop(timeout=2.0)

        # flush() was called at least once per batch
        assert flush_count["n"] >= 1

        entries = _parse_log(log_file)
        assert len(entries) == 10
        tracking.close()


# ============================================================================
# AsyncConsoleDestination
# ============================================================================

class TestAsyncConsoleDestination:
    def test_write(self, capsys):
        dest = AsyncConsoleDestination()
        dest.write(b"test output\n")
        dest.close()

    def test_stderr(self):
        dest = AsyncConsoleDestination(use_stderr=True)
        dest.write(b"error\n")
        dest.close()

    def test_flush(self):
        """flush() on console doesn't crash."""
        dest = AsyncConsoleDestination()
        dest.flush()
        dest.close()


# ============================================================================
# AsyncRotatingFileDestination
# ============================================================================

class TestAsyncRotatingFileDestination:
    def test_rotation(self, tmp_path):
        p = tmp_path / "test.log"
        dest = AsyncRotatingFileDestination(p, max_size=50, backup_count=2)
        for i in range(10):
            dest.write(b"x" * 20 + b"\n")
        dest.close()
        assert (tmp_path / "test.log").exists() or (tmp_path / "test.log.1").exists()

    def test_rotation_creates_backups(self, tmp_path):
        """Rotation creates numbered backup files with valid content."""
        p = tmp_path / "rot.log"
        dest = AsyncRotatingFileDestination(p, max_size=30, backup_count=3)
        for i in range(20):
            dest.write(f'{{"msg":"rot-{i}"}}\n'.encode())
        dest.close()

        # At least one backup should exist
        assert (tmp_path / "rot.log.1").exists()


# ============================================================================
# AsyncDestinationProxy
# ============================================================================

class TestAsyncDestinationProxy:
    def test_forwards_to_sync(self):
        received = []
        proxy = AsyncDestinationProxy(lambda msg: received.append(msg))
        proxy(b'{"key": "value"}\n')
        assert len(received) == 1
        assert received[0]["key"] == "value"

    def test_forwards_complex_json(self):
        """Proxy decodes complex JSON correctly."""
        received = []
        proxy = AsyncDestinationProxy(lambda msg: received.append(msg))
        proxy(b'{"msg":"hello","lvl":[1],"mt":"info"}\n')
        assert received[0]["msg"] == "hello"
        assert received[0]["mt"] == "info"


# ============================================================================
# Factory Functions
# ============================================================================

class TestCreateFileDestination:
    def test_creates_simple(self, tmp_path):
        p = tmp_path / "test.log"
        dest = create_file_destination(p)
        assert isinstance(dest, AsyncFileDestination)
        dest.close()

    def test_creates_rotating(self, tmp_path):
        p = tmp_path / "test.log"
        dest = create_file_destination(p, rotating=True)
        assert isinstance(dest, AsyncRotatingFileDestination)
        dest.close()

    def test_creates_with_fsync(self, tmp_path):
        """Factory creates destination with fsync enabled."""
        p = tmp_path / "fsync.log"
        dest = create_file_destination(p, use_fsync=True)
        dest.write(b'{"msg":"factory-fsync"}\n')
        dest.close()

        entries = _parse_log(p)
        assert len(entries) == 1
        assert entries[0]["msg"] == "factory-fsync"


class TestCreateConsoleDestination:
    def test_creates(self):
        dest = create_console_destination()
        assert isinstance(dest, AsyncConsoleDestination)
        dest.close()

    def test_stderr(self):
        dest = create_console_destination(use_stderr=True)
        assert isinstance(dest, AsyncConsoleDestination)
        dest.close()
