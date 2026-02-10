"""Tests for logxpy/src/serializers.py -- Serialization helpers."""
from __future__ import annotations
import datetime
from logxpy.src.serializers import timestamp, identity, md5hex

class TestTimestamp:
    def test_formats_datetime(self):
        dt = datetime.datetime(2024, 1, 15, 12, 30, 45, 123456)
        result = timestamp(dt)
        assert "2024-01-15" in result
        assert "12:30:45" in result

class TestIdentity:
    def test_returns_same_value(self):
        assert identity(42) == 42
        assert identity("hello") == "hello"
        assert identity(None) is None

class TestMd5hex:
    def test_known_value(self):
        result = md5hex(b"hello")
        assert isinstance(result, str)
        assert len(result) == 32

    def test_different_inputs(self):
        assert md5hex(b"hello") != md5hex(b"world")
