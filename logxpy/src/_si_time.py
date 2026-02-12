"""Time parsing with SI unit support (e.g., '1ms', '10µs', '5m').

Integrates with common/si_eng1.py for SI unit parsing.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

# Add common/ to path for SI toolkit
_COMMON_PATH = Path(__file__).parent.parent.parent / "common"
if str(_COMMON_PATH) not in sys.path:
    sys.path.insert(0, str(_COMMON_PATH))

try:
    from si_eng1 import parse_si, si_float, SIError
    _HAS_SI = True
except ImportError:
    _HAS_SI = False


# Time unit multipliers (fallback if SI not available)
_TIME_UNITS: Final[dict[str, float]] = {
    "ns": 1e-9,
    "us": 1e-6,
    "µs": 1e-6,
    "ms": 1e-3,
    "s": 1.0,
    "m": 60.0,
    "h": 3600.0,
    "d": 86400.0,
}


def parse_time(value: float | str | None) -> float | None:
    """Parse time value to seconds.
    
    Accepts:
        - float: seconds directly (e.g., 0.01, 5.0)
        - str with SI prefix: "1ms", "10µs"
        - str with time unit: "5m" (minutes), "1h" (hours), "1s"
        - None: returns None
    
    Examples:
        >>> parse_time(0.01)      # 0.01 seconds
        0.01
        >>> parse_time("1ms")     # 1 millisecond
        0.001
        >>> parse_time("10µs")    # 10 microseconds  
        1e-05
        >>> parse_time("5m")      # 5 minutes
        300.0
    
    Returns:
        Time in seconds, or None if input was None
    
    Raises:
        ValueError: If string format is invalid
    """
    if value is None:
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if not isinstance(value, str):
        raise ValueError(f"Time must be float or str, got {type(value)}")
    
    value = value.strip()
    
    # Check time units first (higher priority than SI)
    # Sort by longest unit first to match 'ms' before 'm'
    for unit in sorted(_TIME_UNITS.keys(), key=len, reverse=True):
        if value.endswith(unit):
            num_part = value[:-len(unit)].strip()
            try:
                return float(num_part) * _TIME_UNITS[unit]
            except ValueError:
                raise ValueError(f"Invalid time value: {value}")
    
    # Try SI parsing (for pure SI like "10m" = 10 milli without unit)
    if _HAS_SI:
        try:
            return si_float(value)
        except SIError:
            pass
    
    # Plain number (assumed seconds)
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid time format: {value!r}. Use like '1ms', '10µs', '5m', or 0.01")


def format_time(seconds: float, precision: int = 2) -> str:
    """Format seconds to human-readable SI time string.
    
    Examples:
        >>> format_time(0.001)    # '1.00ms'
        >>> format_time(1e-05)    # '10.00µs'
        >>> format_time(300)      # '5.00m'
    """
    if _HAS_SI:
        from si_eng1 import float_si
        # Find appropriate unit
        abs_sec = abs(seconds)
        if abs_sec >= 60:
            return float_si(seconds / 60, precision) + "m"
        elif abs_sec >= 1:
            return float_si(seconds, precision) + "s"
        elif abs_sec >= 1e-3:
            return float_si(seconds * 1e3, precision) + "ms"
        elif abs_sec >= 1e-6:
            return float_si(seconds * 1e6, precision) + "µs"
        else:
            return float_si(seconds * 1e9, precision) + "ns"
    
    # Fallback formatting
    if abs(seconds) >= 60:
        return f"{seconds/60:.{precision}f}m"
    elif abs(seconds) >= 1:
        return f"{seconds:.{precision}f}s"
    elif abs(seconds) >= 1e-3:
        return f"{seconds*1e3:.{precision}f}ms"
    elif abs(seconds) >= 1e-6:
        return f"{seconds*1e6:.{precision}f}µs"
    else:
        return f"{seconds*1e9:.{precision}f}ns"


__all__ = ["parse_time", "format_time"]
