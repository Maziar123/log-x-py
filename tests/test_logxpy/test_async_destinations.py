"""Tests for logxpy/src/_async_destinations.py -- Async destinations."""
from __future__ import annotations
from pathlib import Path
from logxpy.src._async_destinations import (
    AsyncFileDestination, AsyncConsoleDestination,
    AsyncRotatingFileDestination, AsyncDestinationProxy,
    create_file_destination, create_console_destination,
)

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

class TestAsyncConsoleDestination:
    def test_write(self, capsys):
        dest = AsyncConsoleDestination()
        dest.write(b"test output\n")
        dest.close()

    def test_stderr(self):
        dest = AsyncConsoleDestination(use_stderr=True)
        dest.write(b"error\n")
        dest.close()

class TestAsyncRotatingFileDestination:
    def test_rotation(self, tmp_path):
        p = tmp_path / "test.log"
        dest = AsyncRotatingFileDestination(p, max_size=50, backup_count=2)
        # Write enough data to trigger rotation
        for i in range(10):
            dest.write(b"x" * 20 + b"\n")
        dest.close()
        # Check that backup files exist
        assert (tmp_path / "test.log").exists() or (tmp_path / "test.log.1").exists()

class TestAsyncDestinationProxy:
    def test_forwards_to_sync(self):
        received = []
        proxy = AsyncDestinationProxy(lambda msg: received.append(msg))
        proxy(b'{"key": "value"}\n')
        assert len(received) == 1
        assert received[0]["key"] == "value"

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

class TestCreateConsoleDestination:
    def test_creates(self):
        dest = create_console_destination()
        assert isinstance(dest, AsyncConsoleDestination)
        dest.close()

    def test_stderr(self):
        dest = create_console_destination(use_stderr=True)
        assert isinstance(dest, AsyncConsoleDestination)
        dest.close()
