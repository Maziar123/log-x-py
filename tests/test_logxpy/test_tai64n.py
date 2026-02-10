"""Tests for logxpy/src/tai64n.py -- TAI64N encoding/decoding."""
from __future__ import annotations
from logxpy.src.tai64n import encode, decode

class TestEncode:
    def test_returns_string(self):
        result = encode(1700000000.0)
        assert isinstance(result, str)
        assert result.startswith("@")

    def test_includes_nanoseconds(self):
        result = encode(1700000000.5)
        assert len(result) > 10

class TestDecode:
    def test_roundtrip(self):
        ts = 1700000000.0
        encoded = encode(ts)
        decoded = decode(encoded)
        assert abs(decoded - ts) < 0.001

    def test_roundtrip_with_nanos(self):
        ts = 1700000000.123456
        encoded = encode(ts)
        decoded = decode(encoded)
        assert abs(decoded - ts) < 0.001
