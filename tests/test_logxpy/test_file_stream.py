"""Tests for logxpy/src/file_stream.py -- File/stream operations."""
from __future__ import annotations
from io import BytesIO, StringIO
from pathlib import Path
from logxpy.src.file_stream import (
    send_file_as_hex, send_text_file, send_stream_as_hex,
    send_stream_as_text, send_file_info, send_bytes,
)

class TestSendFileAsHex:
    def test_existing_file(self, tmp_path, captured_messages):
        p = tmp_path / "test.bin"
        p.write_bytes(b"\xDE\xAD\xBE\xEF")
        send_file_as_hex(p)
        assert len(captured_messages) >= 1

    def test_not_found(self, captured_messages):
        send_file_as_hex("/nonexistent/path")
        assert len(captured_messages) >= 1
        # _error is nested inside the 'data' dict
        assert any("_error" in m.get("data", {}) for m in captured_messages)

class TestSendTextFile:
    def test_existing_file(self, tmp_path, captured_messages):
        p = tmp_path / "test.txt"
        p.write_text("hello\nworld\n")
        send_text_file(p)
        assert len(captured_messages) >= 1

    def test_not_found(self, captured_messages):
        send_text_file("/nonexistent/path")
        assert len(captured_messages) >= 1

class TestSendStreamAsHex:
    def test_binary_stream(self, captured_messages):
        send_stream_as_hex(BytesIO(b"\x00\x01\x02"))
        assert len(captured_messages) >= 1

class TestSendStreamAsText:
    def test_text_stream(self, captured_messages):
        send_stream_as_text(StringIO("line1\nline2\n"))
        assert len(captured_messages) >= 1

class TestSendFileInfo:
    def test_existing_file(self, tmp_path, captured_messages):
        p = tmp_path / "test.txt"
        p.write_text("hello")
        send_file_info(p)
        assert len(captured_messages) >= 1

    def test_not_found(self, captured_messages):
        send_file_info("/nonexistent/path")
        assert len(captured_messages) >= 1

class TestSendBytes:
    def test_bytes(self, captured_messages):
        send_bytes(b"\x00\x01\x02\x03")
        assert len(captured_messages) >= 1
