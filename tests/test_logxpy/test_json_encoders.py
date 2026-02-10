"""Tests for logxpy/src/_json_encoders.py -- JSON encoding support."""
from __future__ import annotations
from pathlib import Path
from datetime import date, time
from logxpy.src._json_encoders import json_default, _dumps_bytes, _dumps_unicode

class TestJsonDefault:
    def test_path(self):
        result = json_default(Path("/tmp/test.log"))
        assert result == "/tmp/test.log"

    def test_date(self):
        result = json_default(date(2024, 1, 15))
        assert "2024-01-15" in result

    def test_time(self):
        result = json_default(time(12, 30, 45))
        assert "12:30:45" in result

    def test_set(self):
        result = json_default({1, 2, 3})
        assert isinstance(result, list)
        assert set(result) == {1, 2, 3}

    def test_complex(self):
        result = json_default(complex(1, 2))
        assert result == {"real": 1.0, "imag": 2.0}

    def test_unsupported_raises(self):
        import pytest
        with pytest.raises(TypeError, match="Unsupported"):
            json_default(object())

class TestDumpsBytes:
    def test_simple_dict(self):
        result = _dumps_bytes({"key": "value"})
        assert isinstance(result, bytes)
        assert b"key" in result

class TestDumpsUnicode:
    def test_simple_dict(self):
        result = _dumps_unicode({"key": "value"})
        assert isinstance(result, str)
        assert "key" in result
