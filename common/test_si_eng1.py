"""Comprehensive tests for si_eng1.py."""

from __future__ import annotations

import math
import sys
from typing import Any

# Add parent to path for import
sys.path.insert(0, str(__file__).rsplit("/", 2)[0] if "/" in __file__ else ".")

from si_eng1 import (
    SIError,
    SIValue,
    float_si,
    int_si,
    is_si,
    parse_si,
    si_aware,
    si_convert,
    si_float,
    si_int,
    si_range,
    validate_si,
)


class TestSIValue:
    """Test SIValue dataclass."""

    def test_creation(self) -> None:
        """Test basic creation."""
        v = SIValue(1000)
        assert v.value == 1000
        assert v.unit == ""

        v2 = SIValue(1000, "Hz")
        assert v2.unit == "Hz"

    def test_immutable(self) -> None:
        """Test frozen dataclass."""
        v = SIValue(1000)
        try:
            v.value = 2000  # type: ignore[misc]
            raise AssertionError("Should be frozen")
        except AttributeError:
            pass

    def test_slots(self) -> None:
        """Test slots reduce memory."""
        v = SIValue(1000)
        try:
            v.new_attr = 1  # type: ignore[attr-defined]
            raise AssertionError("Should use slots")
        except AttributeError:
            pass

    def test_float_conversion(self) -> None:
        """Test __float__."""
        v = SIValue(1000)
        assert float(v) == 1000.0

    def test_int_conversion(self) -> None:
        """Test __int__."""
        v = SIValue(1000.7)
        assert int(v) == 1000

    def test_str(self) -> None:
        """Test __str__."""
        v = SIValue(1000, "Hz")
        assert str(v) == "1.00kHz"

    def test_repr(self) -> None:
        """Test __repr__."""
        v = SIValue(1000, "Hz")
        assert repr(v) == "SIValue(1000.0, 'Hz')"

    def test_equality(self) -> None:
        """Test __eq__ with various types."""
        v = SIValue(1000)
        assert v == SIValue(1000)
        assert v == 1000
        assert v == 1000.0
        assert not (v == SIValue(2000))
        assert not (v == "not a number")

    def test_comparison(self) -> None:
        """Test __lt__ and __total_ordering__."""
        v = SIValue(1000)
        assert v < SIValue(2000)
        assert v < 2000
        assert v < "2k"
        assert v <= SIValue(1000)
        assert v > SIValue(500)
        assert v >= SIValue(1000)

    def test_arithmetic(self) -> None:
        """Test arithmetic operations."""
        v = SIValue(1000, "Hz")

        # Addition
        assert (v + SIValue(500)).value == 1500
        assert (v + 500).value == 1500
        assert (v + "500").value == 1500

        # Subtraction
        assert (v - 500).value == 500

        # Multiplication
        assert (v * 2).value == 2000

        # Division
        assert (v / 2).value == 500

        # Division by zero
        try:
            v / 0
            raise AssertionError("Should raise ZeroDivisionError")
        except ZeroDivisionError:
            pass


class TestParseSI:
    """Test parse_si function."""

    def test_basic_numbers(self) -> None:
        """Test parsing plain numbers."""
        assert parse_si("100").value == 100
        assert parse_si("-100").value == -100
        assert parse_si("3.14").value == 3.14
        assert parse_si(".5").value == 0.5
        assert parse_si("5.").value == 5.0

    def test_scientific_notation(self) -> None:
        """Test scientific notation."""
        assert parse_si("1e3").value == 1000
        assert parse_si("1E3").value == 1000
        assert parse_si("1e-3").value == 0.001
        assert parse_si("1.5e2").value == 150

    def test_si_prefixes(self) -> None:
        """Test all SI prefixes."""
        tests = [
            ("1y", 1e-24), ("1z", 1e-21), ("1a", 1e-18), ("1f", 1e-15),
            ("1p", 1e-12), ("1n", 1e-9), ("1µ", 1e-6), ("1u", 1e-6),
            ("1m", 1e-3), ("1k", 1e3), ("1K", 1e3), ("1M", 1e6),
            ("1G", 1e9), ("1T", 1e12), ("1P", 1e15), ("1E", 1e18),
            ("1Z", 1e21), ("1Y", 1e24),
        ]
        for s, expected in tests:
            result = parse_si(s).value
            assert math.isclose(result, expected, rel_tol=1e-9), f"Failed for {s}: {result} != {expected}"

    def test_compound_units(self) -> None:
        """Test compound units like kV, mA."""
        v = parse_si("5kV")
        assert v.value == 5000
        assert v.unit == "V"

        v = parse_si("10mA")
        assert v.value == 0.01
        assert v.unit == "A"

    def test_full_names(self) -> None:
        """Test full name prefixes."""
        assert parse_si("1kilo").value == 1000
        assert parse_si("1mega").value == 1e6
        assert parse_si("1milli").value == 1e-3
        assert parse_si("1MILLI").value == 1e-3  # Case insensitive

    def test_whitespace(self) -> None:
        """Test whitespace handling."""
        assert parse_si("  100  ").value == 100
        assert parse_si("10 k").value == 10000  # Space between number and prefix

    def test_errors(self) -> None:
        """Test error cases."""
        try:
            parse_si("")
            raise AssertionError("Should raise SIError")
        except SIError as e:
            assert "Empty" in str(e)

        try:
            parse_si("abc")
            raise AssertionError("Should raise SIError")
        except SIError as e:
            assert "Invalid format" in str(e)

        try:
            parse_si("nan")
            raise AssertionError("Should raise SIError")
        except SIError as e:
            assert "NaN" in str(e) or "Invalid" in str(e)


class TestConversion:
    """Test conversion functions."""

    def test_si_float(self) -> None:
        """Test si_float."""
        assert si_float("1k") == 1000
        assert si_float(SIValue(1000)) == 1000
        assert si_float(1000) == 1000

    def test_si_int(self) -> None:
        """Test si_int."""
        assert si_int("1k") == 1000
        assert si_int("1.9k") == 1900

    def test_float_si(self) -> None:
        """Test float_si."""
        assert float_si(1000) == "1.00k"
        assert float_si(0.001) == "1.00m"
        assert float_si(0) == "0"
        assert float_si(1000, precision=0) == "1k"
        assert float_si(1000, unit="Hz") == "1.00kHz"
        assert float_si(-1000) == "-1.00k"

    def test_int_si(self) -> None:
        """Test int_si."""
        assert int_si(1000) == "1k"
        assert int_si(1000, unit="Hz") == "1Hz"


class TestValidation:
    """Test validation functions."""

    def test_validate_si(self) -> None:
        """Test validate_si."""
        assert validate_si("1k") == (True, None)
        assert validate_si("100") == (True, None)
        assert validate_si("") == (False, "Empty")
        assert validate_si("abc") == (False, "Invalid format")
        assert validate_si(123) == (False, "Not string")  # type: ignore[arg-type]

    def test_is_si(self) -> None:
        """Test is_si."""
        assert is_si("1k") is True
        assert is_si("abc") is False


class TestRange:
    """Test si_range."""

    def test_basic_range(self) -> None:
        """Test basic range generation."""
        result = list(si_range(0, 10, 2))
        assert len(result) == 6
        assert [v.value for v in result] == [0, 2, 4, 6, 8, 10]

    def test_string_range(self) -> None:
        """Test range with SI strings."""
        result = list(si_range("0", "1k", "250"))
        assert len(result) == 5
        assert [v.value for v in result] == [0, 250, 500, 750, 1000]

    def test_negative_step(self) -> None:
        """Test negative step."""
        result = list(si_range(10, 0, -2))
        assert len(result) == 6
        assert [v.value for v in result] == [10, 8, 6, 4, 2, 0]

    def test_zero_step_error(self) -> None:
        """Test zero step raises error."""
        try:
            list(si_range(0, 10, 0))
            raise AssertionError("Should raise ValueError")
        except ValueError as e:
            assert "zero" in str(e).lower()

    def test_unit(self) -> None:
        """Test unit propagation."""
        result = list(si_range(0, 10, 5, "Hz"))
        assert all(v.unit == "Hz" for v in result)


class TestSiConvert:
    """Test si_convert."""

    def test_basic(self) -> None:
        """Test basic conversion."""
        assert si_convert(1000, "k") == 1.0
        assert si_convert(1000000, "M") == 1.0
        assert si_convert(0.001, "m") == 1.0

    def test_si_value(self) -> None:
        """Test with SIValue."""
        assert si_convert(SIValue(1000), "k") == 1.0

    def test_string(self) -> None:
        """Test with string."""
        assert si_convert("1k", "") == 1000  # to base unit

    def test_unknown_prefix(self) -> None:
        """Test unknown prefix raises error."""
        try:
            si_convert(1000, "x")
            raise AssertionError("Should raise SIError")
        except SIError as e:
            assert "Unknown" in str(e)


class TestSiAware:
    """Test si_aware decorator."""

    def test_basic(self) -> None:
        """Test basic auto-conversion."""
        @si_aware
        def add(a: Any, b: Any) -> float:
            return float(a) + float(b)

        assert add("1k", "2k") == 3000.0
        assert add(1000, "2k") == 3000.0
        assert add(SIValue(1000), "2k") == 3000.0

    def test_kwargs(self) -> None:
        """Test kwargs auto-conversion."""
        @si_aware
        def calc(a: Any, b: Any = 0) -> float:
            return float(a) + float(b)

        assert calc("1k", b="2k") == 3000.0

    def test_mixed(self) -> None:
        """Test mixed args."""
        @si_aware
        def process(value: Any, unit: str = "") -> str:
            return f"{float(value)}{unit}"

        assert process("1k") == "1000.0"
        assert process("1k", "Hz") == "1000.0Hz"

    def test_preserves_metadata(self) -> None:
        """Test @wraps preserves function metadata."""
        @si_aware
        def my_func(a: Any) -> float:
            """My docstring."""
            return float(a)

        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "My docstring."


class TestEdgeCases:
    """Test edge cases and boundaries."""

    def test_extreme_values(self) -> None:
        """Test extreme SI values."""
        # Smallest
        v = parse_si("1y")
        assert v.value == 1e-24

        # Largest
        v = parse_si("1Y")
        assert v.value == 1e24

    def test_very_small_numbers(self) -> None:
        """Test very small numbers."""
        result = float_si(1e-25)  # Below minimum
        # Should not crash, uses min exponent
        assert isinstance(result, str)

    def test_very_large_numbers(self) -> None:
        """Test very large numbers."""
        result = float_si(1e25)  # Above maximum
        # Should not crash, uses max exponent
        assert isinstance(result, str)

    def test_micro_sign(self) -> None:
        """Test both µ and u work."""
        assert parse_si("10µ").value == 1e-5
        assert parse_si("10u").value == 1e-5


class TestPerformance:
    """Basic performance sanity checks."""

    def test_lambda_cached(self) -> None:
        """Verify si_aware lambda is created once, not per call."""
        call_count = [0]

        original_parse_si = parse_si

        def counting_parse_si(s: str) -> SIValue:
            call_count[0] += 1
            return original_parse_si(s)

        # Create a simple test by checking behavior
        @si_aware
        def test_fn(a: Any, b: Any, c: Any) -> tuple[Any, Any, Any]:
            return (a, b, c)

        # Call multiple times - the lambda should be the same object
        # (we can't easily test this directly, but we can test correctness)
        for _ in range(100):
            result = test_fn("1k", "2k", "3k")
            assert float(result[0]) == 1000
            assert float(result[1]) == 2000
            assert float(result[2]) == 3000


def run_tests() -> None:
    """Run all tests."""
    test_classes = [
        TestSIValue,
        TestParseSI,
        TestConversion,
        TestValidation,
        TestRange,
        TestSiConvert,
        TestSiAware,
        TestEdgeCases,
        TestPerformance,
    ]

    total = 0
    passed = 0
    failed = 0

    for cls in test_classes:
        instance = cls()
        methods = [m for m in dir(instance) if m.startswith("test_")]
        for method in methods:
            total += 1
            try:
                getattr(instance, method)()
                print(f"✓ {cls.__name__}.{method}")
                passed += 1
            except Exception as e:
                print(f"✗ {cls.__name__}.{method}: {e}")
                failed += 1

    print(f"\n{'='*50}")
    print(f"Total: {total}, Passed: {passed}, Failed: {failed}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
