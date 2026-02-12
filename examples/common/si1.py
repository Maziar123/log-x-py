#!/usr/bin/env python3
"""Modern SI Units Toolkit Examples (Python 3.12+)

High-performance SI prefix handling with zero-allocation hot paths.
Supports: 10m, 100K, 1M, 2.5µ, etc.

Case-sensitive: m=milli, M=mega, k/K=kilo
"""

from __future__ import annotations

import sys
from typing import Any

# Add common directory to path
sys.path.insert(0, str(__file__).rsplit("/", 3)[0] if "/" in __file__ else "../..")
sys.path.insert(0, "../../common")

from common.si_eng1 import (
    SIError,
    SIValue,
    float_si,
    int_si,
    is_si,
    parse_si,
    si_aware,
    si_aware_method,
    si_convert,
    si_float,
    si_int,
    si_range,
    validate_si,
)


def example_01_basic_parsing() -> None:
    """Example 1: Basic SI string parsing."""
    print("=" * 60)
    print("Example 1: Basic SI String Parsing")
    print("=" * 60)

    # Parse simple values
    print("\n--- Simple Values ---")
    v1 = parse_si("10k")
    print(f"parse_si('10k') = {v1.value} (value), '{v1.unit}' (unit)")

    v2 = parse_si("5m")
    print(f"parse_si('5m') = {v2.value} (milli)")

    v3 = parse_si("100")
    print(f"parse_si('100') = {v3.value} (plain number)")

    # All SI prefixes
    print("\n--- All SI Prefixes ---")
    prefixes = [
        ("1y", "yocto"),
        ("1z", "zepto"),
        ("1a", "atto"),
        ("1f", "femto"),
        ("1p", "pico"),
        ("1n", "nano"),
        ("1µ", "micro"),
        ("1u", "micro (u alias)"),
        ("1m", "milli"),
        ("1k", "kilo"),
        ("1K", "kilo (K alias)"),
        ("1M", "mega"),
        ("1G", "giga"),
        ("1T", "tera"),
        ("1P", "peta"),
        ("1E", "exa"),
        ("1Z", "zetta"),
        ("1Y", "yotta"),
    ]
    for s, name in prefixes:
        v = parse_si(s)
        print(f"  {s:3} = {v.value:>15.2e} ({name})")

    # Compound units
    print("\n--- Compound Units ---")
    v_khz = parse_si("2.4GHz")
    print(f"parse_si('2.4GHz') = {v_khz.value:.2e} Hz")

    v_ma = parse_si("500mA")
    print(f"parse_si('500mA') = {v_ma.value:.2e} A")

    v_mv = parse_si("3.3kV")
    print(f"parse_si('3.3kV') = {v_mv.value:.2e} V")


def example_02_sivalue_class() -> None:
    """Example 2: SIValue dataclass usage."""
    print("\n" + "=" * 60)
    print("Example 2: SIValue Dataclass")
    print("=" * 60)

    # Create SIValue directly
    print("\n--- Creating SIValue ---")
    v1 = SIValue(1000, "Hz")
    print(f"SIValue(1000, 'Hz') = {v1}")
    print(f"  value={v1.value}, unit='{v1.unit}'")

    # Type conversions
    print("\n--- Type Conversions ---")
    print(f"float(SIValue(1000)) = {float(v1)}")
    print(f"int(SIValue(1000.9)) = {int(SIValue(1000.9))}")
    print(f"str(SIValue(1000, 'Hz')) = '{str(v1)}'")
    print(f"repr(SIValue(1000, 'Hz')) = {repr(v1)}")

    # Immutability (frozen dataclass)
    print("\n--- Immutability ---")
    try:
        v1.value = 2000  # type: ignore[misc]
        print("ERROR: Should not be able to modify frozen dataclass")
    except AttributeError:
        print("✓ Frozen dataclass prevents modification")


def example_03_arithmetic() -> None:
    """Example 3: Arithmetic operations."""
    print("\n" + "=" * 60)
    print("Example 3: Arithmetic Operations")
    print("=" * 60)

    v1 = SIValue(1000, "Hz")
    print(f"\nStarting value: {v1}")

    # Addition
    result = v1 + 500
    print(f"  + 500 = {result}")

    result = v1 + "0.5k"
    print(f"  + '0.5k' = {result}")

    # Subtraction
    result = v1 - 200
    print(f"  - 200 = {result}")

    # Multiplication
    result = v1 * 2.5
    print(f"  * 2.5 = {result}")

    # Division
    result = v1 / 4
    print(f"  / 4 = {result}")

    # Division by zero
    print("\n--- Division by Zero ---")
    try:
        v1 / 0
    except ZeroDivisionError:
        print("✓ Division by zero raises ZeroDivisionError")


def example_04_comparisons() -> None:
    """Example 4: Comparison operations."""
    print("\n" + "=" * 60)
    print("Example 4: Comparisons")
    print("=" * 60)

    v1 = SIValue(1000)
    v2 = SIValue(2000)

    print(f"\nv1 = {v1}, v2 = {v2}")
    print(f"  v1 == v2: {v1 == v2}")
    print(f"  v1 == 1000: {v1 == 1000}")
    print(f"  v1 < v2: {v1 < v2}")
    print(f"  v1 <= v2: {v1 <= v2}")
    print(f"  v1 > v2: {v1 > v2}")
    print(f"  v1 >= v2: {v1 >= v2}")

    # Compare with strings
    print(f"\n  v1 < '2k': {v1 < '2k'}")
    print(f"  v1 == '1k': {v1 == SIValue(1000)}")

    # Chaining
    print(f"\n  v1 < v2 < '3k': {v1 < v2 < parse_si('3k')}")


def example_05_conversion_functions() -> None:
    """Example 5: Conversion functions."""
    print("\n" + "=" * 60)
    print("Example 5: Conversion Functions")
    print("=" * 60)

    # si_float / si_int - convert to numbers
    print("\n--- si_float / si_int ---")
    print(f"si_float('1.5k') = {si_float('1.5k')}")
    print(f"si_int('1.5k') = {si_int('1.5k')} (truncates)")
    print(f"si_float(SIValue(500)) = {si_float(SIValue(500))}")

    # float_si / int_si - convert to strings
    print("\n--- float_si / int_si ---")
    print(f"float_si(1000) = '{float_si(1000)}'")
    print(f"float_si(1000, precision=0) = '{float_si(1000, precision=0)}'")
    print(f"float_si(1000, precision=3) = '{float_si(1000, precision=3)}'")
    print(f"float_si(1000, unit='Hz') = '{float_si(1000, unit='Hz')}'")
    print(f"int_si(1500) = '{int_si(1500)}' (rounds)")

    # si_convert - convert to specific prefix
    print("\n--- si_convert ---")
    print(f"si_convert(10000, 'k') = {si_convert(10000, 'k')}")
    print(f"si_convert('1M', 'k') = {si_convert('1M', 'k')}")
    print(f"si_convert(SIValue(1e6), 'M') = {si_convert(SIValue(1e6), 'M')}")
    print(f"si_convert('1k', '') = {si_convert('1k', '')} (to base unit)")


def example_06_validation() -> None:
    """Example 6: Validation functions."""
    print("\n" + "=" * 60)
    print("Example 6: Validation")
    print("=" * 60)

    # is_si - quick check
    print("\n--- is_si ---")
    test_inputs = ["1k", "100M", "3.14GHz", "abc", "", "123", "invalid"]
    for s in test_inputs:
        valid = "✓" if is_si(s) else "✗"
        print(f"  is_si('{s}') = {is_si(s)} {valid}")

    # validate_si - detailed error
    print("\n--- validate_si ---")
    for s in ["1k", "abc", ""]:
        ok, err = validate_si(s)
        status = "valid" if ok else f"invalid: {err}"
        print(f"  validate_si('{s}') = {status}")


def example_07_range_generation() -> None:
    """Example 7: Range generation."""
    print("\n" + "=" * 60)
    print("Example 7: Range Generation")
    print("=" * 60)

    # Basic range
    print("\n--- Basic Range ---")
    print("si_range(0, 10, 2):")
    for v in si_range(0, 10, 2):
        print(f"  {v.value}")

    # Range with SI strings
    print("\n--- SI String Range ---")
    print("si_range('0', '1k', '250'):")
    values = list(si_range("0", "1k", "250"))
    print(f"  Values: {[v.value for v in values]}")

    # Range with unit
    print("\n--- Range with Unit ---")
    print("si_range(0, 1000, 200, unit='Hz'):")
    for v in si_range(0, 1000, 200, unit="Hz"):
        print(f"  {v}")

    # Negative step
    print("\n--- Negative Step ---")
    print("si_range(10, 0, -2):")
    values = [v.value for v in si_range(10, 0, -2)]
    print(f"  {values}")


def example_08_decorators() -> None:
    """Example 8: Decorators for automatic conversion."""
    print("\n" + "=" * 60)
    print("Example 8: Decorators")
    print("=" * 60)

    # si_aware decorator
    print("\n--- @si_aware Decorator ---")

    @si_aware
    def calculate_power(voltage: Any, current: Any) -> float:
        """Calculate power from voltage and current."""
        return float(voltage) * float(current)

    # All these work automatically
    print(f"calculate_power('10V', '500mA') = {calculate_power('10', '500m'):.2f} W")
    print(f"calculate_power(10, '0.5') = {calculate_power(10, '0.5'):.2f} W")
    print(f"calculate_power(SIValue(10), SIValue(0.5)) = {calculate_power(SIValue(10), SIValue(0.5)):.2f} W")

    # Mixed args and kwargs
    @si_aware
    def calculate_energy(power: Any, time: Any, efficiency: Any = 1.0) -> float:
        return float(power) * float(time) * float(efficiency)

    result = calculate_energy("1kW", "2h", efficiency="0.9")
    print(f"\ncalculate_energy('1kW', '2h', efficiency='0.9') = {result:.2f} Wh")

    # si_aware_method for classes
    print("\n--- @si_aware_method Decorator ---")

    class Circuit:
        def __init__(self, name: str):
            self.name = name

        @si_aware_method
        def calculate_current(self, voltage: Any, resistance: Any) -> float:
            """Calculate current using Ohm's Law."""
            v = float(voltage)
            r = float(resistance)
            return v / r

    circuit = Circuit("Test Circuit")
    current = circuit.calculate_current("5V", "1k")
    print(f"Circuit({circuit.name}).calculate_current('5V', '1k') = {current:.3f} A")


def example_09_error_handling() -> None:
    """Example 9: Error handling."""
    print("\n" + "=" * 60)
    print("Example 9: Error Handling")
    print("=" * 60)

    errors_to_demo = [
        ("Empty string", lambda: parse_si("")),
        ("Invalid format", lambda: parse_si("abc")),
        ("Just prefix", lambda: parse_si("k")),
        ("Overflow", lambda: parse_si("1e999")),
        ("Unknown prefix", lambda: si_convert(1000, "x")),
        ("Zero step", lambda: list(si_range(0, 10, 0))),
    ]

    for name, fn in errors_to_demo:
        try:
            fn()
            print(f"  {name}: ERROR - should have raised!")
        except SIError as e:
            print(f"  {name}: ✓ SIError - {e}")
        except ValueError as e:
            print(f"  {name}: ✓ ValueError - {e}")
        except ZeroDivisionError as e:
            print(f"  {name}: ✓ ZeroDivisionError - {e}")


def example_10_real_world() -> None:
    """Example 10: Real-world use cases."""
    print("\n" + "=" * 60)
    print("Example 10: Real-World Use Cases")
    print("=" * 60)

    # Use case 1: Frequency band selection
    print("\n--- Frequency Bands ---")
    bands = [
        ("2.4GHz", "WiFi 2.4GHz"),
        ("5GHz", "WiFi 5GHz"),
        ("28GHz", "5G mmWave"),
        ("3.5GHz", "5G Mid-band"),
    ]

    for freq_str, name in bands:
        freq = parse_si(freq_str)
        print(f"  {name}: {float_si(freq.value, unit='Hz')} ({freq.value:.2e} Hz)")

    # Use case 2: Component values
    print("\n--- Component Values ---")
    components = [
        ("4.7k Resistor", "4.7k", "Ohm"),
        ("100µF Capacitor", "100µ", "F"),
        ("10nF Capacitor", "10n", "F"),
        ("1.5k Resistor", "1.5k", "Ohm"),
    ]

    for name, value, unit in components:
        v = parse_si(value + unit)
        print(f"  {name}: {v}")

    # Use case 3: File sizes
    print("\n--- File Size Conversion ---")
    sizes = [1024, 1536000, 1073741824, 5497558138880]
    for size in sizes:
        print(f"  {size} bytes = {float_si(float(size), unit='B')}")

    # Use case 4: Power calculations
    print("\n--- Power Budget ---")
    devices = [
        ("CPU", "65W"),
        ("GPU", "150W"),
        ("RAM", "10W"),
        ("SSD", "5W"),
    ]

    total = 0.0
    for device, power_str in devices:
        power = si_float(power_str)
        print(f"  {device}: {float_si(power, unit='W')}")
        total += power

    print(f"  Total: {float_si(total, unit='W')}")

    # Use case 5: Generate test frequencies
    print("\n--- Test Frequency Sweep ---")
    print("  Frequencies from 100Hz to 10kHz:")
    for freq in si_range("100", "10k", "500", unit="Hz"):
        print(f"    {freq}")


def main() -> None:
    """Run all examples."""
    examples = [
        example_01_basic_parsing,
        example_02_sivalue_class,
        example_03_arithmetic,
        example_04_comparisons,
        example_05_conversion_functions,
        example_06_validation,
        example_07_range_generation,
        example_08_decorators,
        example_09_error_handling,
        example_10_real_world,
    ]

    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"\n✗ Example {i} failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
