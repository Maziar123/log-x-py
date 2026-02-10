"""Tests for logxpy/src/system_info.py -- System information logging."""
from __future__ import annotations
from logxpy.src.system_info import (
    send_system_info, send_memory_status, send_memory_as_hex,
    send_stack_trace, send_heap_status,
)

class TestSendSystemInfo:
    def test_sends_message(self, captured_messages):
        send_system_info()
        assert len(captured_messages) >= 1

class TestSendMemoryStatus:
    def test_sends_message(self, captured_messages):
        send_memory_status()
        assert len(captured_messages) >= 1

class TestSendMemoryAsHex:
    def test_bytes_input(self, captured_messages):
        send_memory_as_hex(b"\x00\x01\x02\x03")
        assert len(captured_messages) >= 1

    def test_non_bytes_warns(self, captured_messages):
        send_memory_as_hex("not bytes")
        assert len(captured_messages) >= 1

class TestSendStackTrace:
    def test_sends_message(self, captured_messages):
        send_stack_trace()
        assert len(captured_messages) >= 1

class TestSendHeapStatus:
    def test_sends_message(self, captured_messages):
        send_heap_status()
        assert len(captured_messages) >= 1
