"""Tests for logxpy/src/_si_time.py -- SI time value parsing."""
from __future__ import annotations

import pytest

from logxpy.src._si_time import parse_time, format_time


class TestParseTime:
    """Test parse_time() function."""

    def test_none_returns_none(self):
        """None input returns None."""
        assert parse_time(None) is None

    def test_float_returns_float(self):
        """Float input returns same value."""
        assert parse_time(0.01) == 0.01
        assert parse_time(5.0) == 5.0
        assert parse_time(0) == 0.0

    def test_int_returns_float(self):
        """Int input converts to float."""
        assert parse_time(10) == 10.0

    def test_nanoseconds(self):
        """Parse nanoseconds."""
        assert abs(parse_time("100ns") - 1e-7) < 1e-15
        assert abs(parse_time("1ns") - 1e-9) < 1e-15

    def test_microseconds(self):
        """Parse microseconds (µs or us)."""
        assert abs(parse_time("10µs") - 1e-5) < 1e-15
        assert abs(parse_time("100µs") - 1e-4) < 1e-15
        assert abs(parse_time("1us") - 1e-6) < 1e-15  # ASCII fallback

    def test_milliseconds(self):
        """Parse milliseconds."""
        assert parse_time("1ms") == 0.001
        assert parse_time("10ms") == 0.01
        assert parse_time("100ms") == 0.1
        assert parse_time("500ms") == 0.5

    def test_seconds(self):
        """Parse seconds."""
        assert parse_time("1s") == 1.0
        assert parse_time("5s") == 5.0
        assert parse_time("0.5s") == 0.5

    def test_minutes(self):
        """Parse minutes."""
        assert parse_time("1m") == 60.0
        assert parse_time("5m") == 300.0
        assert parse_time("0.5m") == 30.0

    def test_hours(self):
        """Parse hours."""
        assert parse_time("1h") == 3600.0
        assert parse_time("2h") == 7200.0

    def test_days(self):
        """Parse days."""
        assert parse_time("1d") == 86400.0
        assert parse_time("0.5d") == 43200.0

    def test_plain_number_as_seconds(self):
        """Plain number without unit is seconds."""
        assert parse_time("5") == 5.0
        assert parse_time("0.01") == 0.01
        assert parse_time("100") == 100.0

    def test_whitespace_stripped(self):
        """Whitespace around value is stripped."""
        assert parse_time("  10ms  ") == 0.01
        assert parse_time("  5s") == 5.0

    def test_invalid_type_raises(self):
        """Non-string, non-number raises ValueError."""
        with pytest.raises(ValueError, match="float or str"):
            parse_time([])  # type: ignore

    def test_invalid_format_raises(self):
        """Invalid string format raises ValueError."""
        with pytest.raises(ValueError):
            parse_time("xyz")
        with pytest.raises(ValueError):
            parse_time("ms")  # No number
        with pytest.raises(ValueError):
            parse_time("5.5.5ms")  # Bad number

    def test_milli_vs_minute_priority(self):
        """'ms' should be milliseconds, not milli-seconds."""
        # 'ms' is longer match than 'm', so milliseconds wins
        assert parse_time("5ms") == 0.005  # 5 milliseconds
        assert parse_time("5m") == 300.0   # 5 minutes


class TestFormatTime:
    """Test format_time() function."""

    def test_nanoseconds(self):
        """Format very small values as nanoseconds."""
        result = format_time(1e-9)
        assert "ns" in result

    def test_microseconds(self):
        """Format small values as microseconds."""
        result = format_time(1e-5)
        assert "µs" in result or "us" in result

    def test_milliseconds(self):
        """Format medium values as milliseconds."""
        result = format_time(0.001)
        assert "ms" in result

    def test_seconds(self):
        """Format second-range values as seconds."""
        result = format_time(1.0)
        assert "s" in result

    def test_minutes(self):
        """Format large values as minutes."""
        result = format_time(300.0)
        assert "m" in result

    def test_precision(self):
        """Precision parameter works."""
        result = format_time(0.001, precision=3)
        assert "." in result  # Has decimal


class TestRoundTrip:
    """Test parse and format round-trip."""

    def test_roundtrip_milliseconds(self):
        """Parse and format milliseconds."""
        original = "10ms"
        parsed = parse_time(original)
        formatted = format_time(parsed)
        # formatted is like "10.00ms", parse it back
        reparsed = parse_time(formatted.replace(" ", ""))
        assert abs(parsed - reparsed) < 0.001  # Allow small rounding

    def test_roundtrip_seconds(self):
        """Parse and format seconds."""
        original = "5s"
        parsed = parse_time(original)
        formatted = format_time(parsed)
        assert "s" in formatted


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero(self):
        """Zero is handled correctly."""
        assert parse_time(0) == 0.0
        assert parse_time("0s") == 0.0
        assert parse_time("0ms") == 0.0

    def test_negative_values(self):
        """Negative values (if supported)."""
        assert parse_time(-5) == -5.0
        assert parse_time("-10ms") == -0.01

    def test_very_small_values(self):
        """Very small values don't underflow."""
        assert parse_time("1ns") == 1e-9

    def test_very_large_values(self):
        """Very large values don't overflow."""
        assert parse_time("100d") == 8640000.0
