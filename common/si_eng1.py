"""High-performance SI units toolkit (Python 3.12+).

Optimized for zero-allocation hot paths and mypy --strict compliance.
Supports: 10m, 100K, 1M, 2.5µ, etc. Case-sensitive: m=milli, M=mega, k/K=kilo.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from functools import total_ordering, wraps
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

__all__ = [
    "SIError",
    "SIValue",
    "float_si",
    "int_si",
    "is_si",
    "parse_si",
    "si_aware",
    "si_convert",
    "si_float",
    "si_int",
    "si_range",
    "validate_si",
]

# Pre-compiled tables for O(1) lookup
_SI_TABLE: Final[tuple[tuple[int, str, str, float], ...]] = (
    (-24, "y", "yocto", 1e-24), (-21, "z", "zepto", 1e-21),
    (-18, "a", "atto", 1e-18), (-15, "f", "femto", 1e-15),
    (-12, "p", "pico", 1e-12), (-9, "n", "nano", 1e-9),
    (-6, "µ", "micro", 1e-6), (-3, "m", "milli", 1e-3),
    (0, "", "", 1.0), (3, "k", "kilo", 1e3), (6, "M", "mega", 1e6),
    (9, "G", "giga", 1e9), (12, "T", "tera", 1e12),
    (15, "P", "peta", 1e15), (18, "E", "exa", 1e18),
    (21, "Z", "zetta", 1e21), (24, "Y", "yotta", 1e24),
)

_EXP_TO_SYM: Final[dict[int, str]] = {e: s for e, s, _, _ in _SI_TABLE}
_EXP_TO_FACT: Final[dict[int, float]] = {e: f for e, _, _, f in _SI_TABLE}
_SYM_TO_EXP: Final[dict[str, int]] = {}
_NAME_TO_EXP: Final[dict[str, int]] = {}
for _e, _s, _n, _ in _SI_TABLE:
    if _s:
        _SYM_TO_EXP[_s] = _e
        if _s == "µ":
            _SYM_TO_EXP["u"] = _e
        if _s == "k":
            _SYM_TO_EXP["K"] = _e
    if _n:
        _NAME_TO_EXP[_n.lower()] = _e

_SI_RE: Final[re.Pattern[str]] = re.compile(
    r"^([+-]?(?:\d+\.?\d*|\d*\.\d+)(?:[eE][+-]?\d+)?)\s*([a-zA-Zµ]*)$"
)
_MIN_EXP: Final[int] = -24
_MAX_EXP: Final[int] = 24


class SIError(ValueError):
    """Invalid SI unit operation."""


@total_ordering
@dataclass(frozen=True, slots=True)
class SIValue:
    """Immutable SI value with arithmetic support."""
    value: float
    unit: str = ""

    def __float__(self) -> float:
        return float(self.value)

    def __int__(self) -> int:
        return int(self.value)

    def __str__(self) -> str:
        return float_si(self.value) + self.unit

    def __repr__(self) -> str:
        return f"SIValue({self.value}, {self.unit!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SIValue):
            return math.isclose(self.value, other.value, rel_tol=1e-9)
        if isinstance(other, (int, float)):
            return math.isclose(self.value, float(other), rel_tol=1e-9)
        return NotImplemented

    def __lt__(self, other: SIValue | float | str) -> bool:
        match other:
            case SIValue(v, _):
                return self.value < v
            case int() | float():
                return self.value < float(other)
            case str():
                return self.value < parse_si(other).value
            case _:
                return NotImplemented  # type: ignore[return-value]

    def __add__(self, other: SIValue | float | str) -> SIValue:
        return SIValue(self.value + _to_float(other), self.unit)

    def __sub__(self, other: SIValue | float | str) -> SIValue:
        return SIValue(self.value - _to_float(other), self.unit)

    def __mul__(self, other: SIValue | float | str) -> SIValue:
        return SIValue(self.value * _to_float(other), self.unit)

    def __truediv__(self, other: SIValue | float | str) -> SIValue:
        d = _to_float(other)
        if d == 0:
            raise ZeroDivisionError
        return SIValue(self.value / d, self.unit)


def _to_float(x: SIValue | float | str) -> float:
    """Fast internal conversion."""
    match x:
        case SIValue(v, _):
            return v
        case float() | int():
            return float(x)
        case str():
            return parse_si(x).value
        case _:
            raise TypeError(f"Unsupported operand: {type(x)}")


def parse_si(s: str) -> SIValue:
    """Parse SI string (e.g., '10m', '5kV', '-2.5µ') into SIValue."""
    if not (s := s.strip()):
        raise SIError("Empty string")

    m = _SI_RE.match(s)
    if not m:
        raise SIError(f"Invalid format: {s!r}")

    num_str, prefix = m.groups()
    try:
        val = float(num_str)
    except ValueError as e:
        raise SIError(f"Invalid number: {num_str}") from e

    # Check for NaN/Inf (catches cases like 'nan', 'inf', '1e1000' overflow)
    if math.isnan(val) or math.isinf(val):
        raise SIError("NaN/Inf not supported")

    if not prefix:
        return SIValue(val, "")

    # Direct symbol lookup (fast path)
    if prefix in _SYM_TO_EXP:
        exp = _SYM_TO_EXP[prefix]
        return SIValue(val * _EXP_TO_FACT[exp], "")

    # Compound (e.g., "kV", "mA")
    if prefix[0] in _SYM_TO_EXP:
        exp = _SYM_TO_EXP[prefix[0]]
        return SIValue(val * _EXP_TO_FACT[exp], prefix[1:])

    # Full name (case insensitive)
    if (p_lower := prefix.lower()) in _NAME_TO_EXP:
        exp = _NAME_TO_EXP[p_lower]
        return SIValue(val * _EXP_TO_FACT[exp], "")

    # No prefix recognized, treat as unit
    return SIValue(val, prefix)


def si_float(x: str | SIValue | float) -> float:
    """Convert SI input to float."""
    return _to_float(x)


def si_int(x: str | SIValue | float) -> int:
    """Convert SI input to int (truncates)."""
    return int(_to_float(x))


def float_si(x: float, precision: int = 2, unit: str = "") -> str:
    """Convert float to SI string (e.g., 0.01 -> '10.00m')."""
    if x == 0:
        return f"0{unit}"

    ax = abs(x)
    sign = "-" if x < 0 else ""

    # Engineering exponent (multiple of 3)
    exp = int(math.log10(ax) // 3 * 3)
    exp = max(_MIN_EXP, min(_MAX_EXP, exp))

    # Adjust to nearest valid exponent
    while exp not in _EXP_TO_SYM:
        exp -= 3

    factor = _EXP_TO_FACT[exp]
    scaled = ax / factor
    sym = _EXP_TO_SYM[exp]

    if precision == 0:
        return f"{sign}{round(scaled)}{sym}{unit}"
    return f"{sign}{scaled:.{precision}f}{sym}{unit}"


def int_si(x: int, precision: int = 0, unit: str = "") -> str:
    """Convert int to SI string."""
    return float_si(float(x), precision, unit)


def validate_si(s: str) -> tuple[bool, str | None]:
    """Validate SI string. Returns (ok, error_or_none)."""
    if not isinstance(s, str):
        return False, "Not string"
    if not (s := s.strip()):
        return False, "Empty"
    if not (m := _SI_RE.match(s)):
        return False, "Invalid format"

    num, pref = m.groups()
    try:
        float(num)
    except ValueError:
        return False, "Bad number"

    if (
        pref
        and pref not in _SYM_TO_EXP
        and pref[0] not in _SYM_TO_EXP
        and pref.lower() not in _NAME_TO_EXP
    ):
        return False, f"Bad prefix: {pref}"
    return True, None


def is_si(s: str) -> bool:
    """Quick validation."""
    return validate_si(s)[0]


def si_range(
    start: str | float,
    stop: str | float,
    step: str | float,
    unit: str = "",
) -> Iterator[SIValue]:
    """Generate arithmetic progression of SI values."""
    s, e, d = _to_float(start), _to_float(stop), _to_float(step)
    if d == 0:
        raise ValueError("Step zero")

    eps = abs(d) * 1e-12
    curr = s
    if d > 0:
        while curr <= e + eps:
            yield SIValue(curr, unit)
            curr += d
    else:
        while curr >= e - eps:
            yield SIValue(curr, unit)
            curr += d


def si_convert(val: SIValue | float | str, to_prefix: str) -> float:
    """Convert to specific prefix scale (e.g., si_convert(10000, 'k') -> 10.0)."""
    base = _to_float(val)
    if to_prefix == "":
        return base  # No conversion needed for base unit
    if (exp := _SYM_TO_EXP.get(to_prefix)) is None:
        raise SIError(f"Unknown prefix: {to_prefix}")
    return base / _EXP_TO_FACT[exp]


def si_aware(fn: Callable) -> Callable:
    """Decorator: auto-convert string args to SIValue."""
    def conv(a: object) -> object:
        return parse_si(a) if isinstance(a, str) else a

    @wraps(fn)
    def wrapper(*args: object, **kwargs: object) -> object:
        return fn(*(conv(a) for a in args), **{k: conv(v) for k, v in kwargs.items()})
    return wrapper


def si_aware_method(fn: Callable) -> Callable:
    """Decorator: auto-convert string args to SIValue."""
    def conv(a: object) -> object:
        return parse_si(a) if isinstance(a, str) else a

    @wraps(fn)
    def wrapper(self: object, *args: object, **kwargs: object) -> object:
        return fn(self, *(conv(a) for a in args), **{k: conv(v) for k, v in kwargs.items()})
    return wrapper
