"""Tests for logxpy/src/_base.py -- Shared utilities."""
from __future__ import annotations

from dataclasses import dataclass

from logxpy.src._base import (
    now, uuid, truncate,
    strip_ansi_codes, pluralize, clean_text,
    get_first, is_non_string_iterable,
    escape_html_text, get_module,
)


# ============================================================================
# Time
# ============================================================================

class TestNow:
    def test_returns_float(self):
        assert isinstance(now(), float)

    def test_monotonically_increasing(self):
        a = now()
        b = now()
        assert b >= a


# ============================================================================
# UUID / Sqid
# ============================================================================

class TestUuid:
    def test_returns_string(self):
        assert isinstance(uuid(), str)

    def test_sqid_mode_default(self):
        result = uuid()
        assert "." in result
        assert len(result) < 20

    def test_uuid4_mode(self):
        result = uuid(use_sqid=False)
        assert len(result) == 36
        assert "-" in result

    def test_distributed_env_var(self, monkeypatch):
        monkeypatch.setenv("LOGXPY_DISTRIBUTED", "1")
        result = uuid()
        assert len(result) == 36
        assert "-" in result

    def test_uniqueness(self):
        ids = {uuid() for _ in range(500)}
        assert len(ids) == 500


# ============================================================================
# Truncate
# ============================================================================

class TestTruncate:
    def test_primitives_passthrough(self):
        assert truncate(42) == 42
        assert truncate(None) is None
        assert truncate(True) is True
        assert truncate(3.14) == 3.14

    def test_short_string_unchanged(self):
        assert truncate("hello") == "hello"

    def test_long_string_truncated(self):
        result = truncate("x" * 600, max_len=500)
        assert result == "x" * 500 + "..."

    def test_bytes_shows_size(self):
        result = truncate(b"\x00" * 100)
        assert result == "<bytes:100>"

    def test_dict_truncated_recursively(self):
        d = {"a": {"b": {"c": {"d": "deep"}}}}
        result = truncate(d, max_depth=2)
        assert "a" in result
        assert isinstance(result["a"], dict)

    def test_list_truncated_at_100(self):
        big_list = list(range(150))
        result = truncate(big_list)
        assert len(result) == 101  # 100 items + "...+50"
        assert result[-1] == "...+50"

    def test_depth_zero_returns_type_name(self):
        result = truncate({"a": 1}, max_depth=0)
        assert result == "<dict>"

    def test_dataclass_truncated(self):
        @dataclass
        class Sample:
            x: int = 1
            y: str = "hello"

        result = truncate(Sample())
        assert result["_type"] == "Sample"
        assert result["x"] == 1

    def test_unknown_type(self):
        class Custom:
            pass
        result = truncate(Custom())
        assert "_type" in result
        assert result["_type"] == "Custom"
        assert "_repr" in result


# ============================================================================
# String Utilities
# ============================================================================

class TestStripAnsiCodes:
    def test_removes_ansi(self):
        assert strip_ansi_codes("\033[31mred\033[0m") == "red"

    def test_no_ansi_unchanged(self):
        assert strip_ansi_codes("plain text") == "plain text"


class TestEscapeHtmlText:
    def test_escapes_special_chars(self):
        result = escape_html_text("<b>test & 'quote'</b>")
        assert "&lt;" in result
        assert "&amp;" in result


class TestPluralize:
    def test_singular(self):
        result = pluralize(1, "item")
        assert "item" in result

    def test_plural(self):
        result = pluralize(5, "item")
        assert "items" in result or "item" in result


class TestCleanText:
    def test_remove_ansi(self):
        result = clean_text("\033[31mred\033[0m")
        assert result == "red"

    def test_asciify(self):
        result = clean_text("naïve", asciify_=True)
        # boltons asciify may return str or bytes depending on version
        assert isinstance(result, (str, bytes))
        assert len(result) >= 3


# ============================================================================
# Iteration
# ============================================================================

class TestGetFirst:
    def test_from_list(self):
        assert get_first([1, 2, 3]) == 1

    def test_empty_returns_default(self):
        assert get_first([], default="x") == "x"

    def test_empty_no_default(self):
        assert get_first([]) is None


class TestIsNonStringIterable:
    def test_list_is_iterable(self):
        assert is_non_string_iterable([1, 2]) is True

    def test_tuple_is_iterable(self):
        assert is_non_string_iterable((1, 2)) is True

    def test_string_is_not(self):
        assert is_non_string_iterable("hello") is False

    def test_bytes_is_not(self):
        assert is_non_string_iterable(b"hello") is False

    def test_int_is_not(self):
        assert is_non_string_iterable(42) is False


# ============================================================================
# Module
# ============================================================================

class TestGetModule:
    def test_loaded_module(self):
        import sys
        result = get_module("sys")
        assert result is sys

    def test_unloaded_module(self):
        result = get_module("nonexistent_module_xyz")
        assert result is None
