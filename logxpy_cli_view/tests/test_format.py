"""Tests for format module."""

from __future__ import annotations

from logxpy_cli_view import format


class TestEscapeControlCharacters:
    """Tests for escape_control_characters."""

    def test_escapes_control_chars(self):
        """Control characters are escaped to Unicode symbols."""
        result = format.escape_control_characters("hello\x01world")
        assert result == "hello\u2401world"

    def test_no_change_for_normal_text(self):
        """Normal text passes through unchanged."""
        result = format.escape_control_characters("hello world")
        assert result == "hello world"


class TestBinary:
    """Tests for binary formatter."""

    def test_decodes_bytes(self):
        """Decodes bytes to string."""
        formatter = format.binary("utf-8")
        result = formatter(b"hello", None)
        assert result == "hello"

    def test_returns_none_for_non_bytes(self):
        """Returns None for non-bytes values."""
        formatter = format.binary("utf-8")
        result = formatter("not bytes", None)
        assert result is None


class TestText:
    """Tests for text formatter."""

    def test_returns_string(self):
        """Returns string value unchanged."""
        formatter = format.text()
        result = formatter("hello", None)
        assert result == "hello"

    def test_returns_none_for_non_string(self):
        """Returns None for non-string values."""
        formatter = format.text()
        result = formatter(123, None)
        assert result is None


class TestTruncateValue:
    """Tests for truncate_value."""

    def test_no_truncation_needed(self):
        """No truncation if within limit."""
        result = format.truncate_value(10, "hello")
        assert result == "hello"

    def test_truncates_long_string(self):
        """Truncates strings exceeding limit."""
        result = format.truncate_value(5, "hello world")
        assert result == "hello\u2026"

    def test_truncates_at_newline(self):
        """Truncates at newline."""
        result = format.truncate_value(100, "hello\nworld")
        assert result == "hello\u2026"


class TestSome:
    """Tests for some combinator."""

    def test_returns_first_non_none(self):
        """Returns first non-None result."""
        combined = format.some(
            lambda x: None,
            lambda x: x * 2,
            lambda x: x * 3,
        )
        assert combined(5) == 10

    def test_returns_none_if_all_none(self):
        """Returns None if all return None."""
        combined = format.some(
            lambda x: None,
            lambda x: None,
        )
        assert combined(5) is None
