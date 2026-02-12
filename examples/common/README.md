# SI Units Toolkit Examples

Modern Python 3.12+ examples for the high-performance SI units toolkit.

## Running Examples

```bash
# Run all examples
python3 si1.py

# Run specific example
python3 -c "from si1 import example_01_basic_parsing; example_01_basic_parsing()"
```

## Examples Overview

| Example | Description |
|---------|-------------|
| `example_01_basic_parsing` | Parse SI strings like "10k", "5m", "2.4GHz" |
| `example_02_sivalue_class` | SIValue dataclass usage and immutability |
| `example_03_arithmetic` | Add, subtract, multiply, divide with SI values |
| `example_04_comparisons` | Compare SIValues with each other and numbers |
| `example_05_conversion_functions` | Convert between formats (si_float, float_si, etc.) |
| `example_06_validation` | Validate SI strings with is_si and validate_si |
| `example_07_range_generation` | Generate ranges with si_range |
| `example_08_decorators` | Use @si_aware and @si_aware_method decorators |
| `example_09_error_handling` | Handle SIError and other exceptions |
| `example_10_real_world` | Real-world use cases: frequency bands, component values, file sizes, power budgets |

## Quick Reference

### Parsing
```python
from common.si_eng1 import parse_si

freq = parse_si("2.4GHz")  # SIValue(2400000000.0, 'Hz')
current = parse_si("500mA")  # SIValue(0.5, 'A')
```

### Conversion
```python
from common.si_eng1 import si_float, float_si

value = si_float("1.5k")  # 1500.0
text = float_si(1000, unit="Hz")  # "1.00kHz"
```

### Decorators
```python
from common.si_eng1 import si_aware

@si_aware
def calculate_power(voltage, current):
    return float(voltage) * float(current)

# All these work:
calculate_power("10V", "500mA")
calculate_power(10, 0.5)
calculate_power(SIValue(10), SIValue(0.5))
```
