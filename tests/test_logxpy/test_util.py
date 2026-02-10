"""Tests for logxpy/src/_util.py -- Utility functions."""
from __future__ import annotations
from logxpy.src._util import safeunicode, saferepr, load_module

class TestSafeunicode:
    def test_normal_string(self):
        assert safeunicode("hello") == "hello"

    def test_number(self):
        assert safeunicode(42) == "42"

    def test_exception_in_str(self):
        class Bad:
            def __str__(self):
                raise RuntimeError("boom")
        result = safeunicode(Bad())
        assert "unknown" in result

class TestSaferepr:
    def test_normal_object(self):
        assert saferepr("hello") == "'hello'"

    def test_exception_in_repr(self):
        class Bad:
            def __repr__(self):
                raise RuntimeError("boom")
        result = saferepr(Bad())
        assert "unknown" in result

class TestLoadModule:
    def test_loads_copy_of_module(self):
        import textwrap
        module = load_module("test_textwrap", textwrap)
        assert module is not textwrap
        assert hasattr(module, "dedent")
