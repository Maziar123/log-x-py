"""Tests for logxpy/src/_fmt.py -- Value formatting."""
from __future__ import annotations
from logxpy.src._fmt import format_value

class TestFormatValue:
    def test_primitives(self):
        assert format_value(42) == 42
        assert format_value("hello") == "hello"
        assert format_value(True) is True

    def test_dict_passthrough(self):
        d = {"key": "value"}
        result = format_value(d)
        assert result == d

    def test_list(self):
        result = format_value([1, 2, 3])
        assert result == [1, 2, 3]
