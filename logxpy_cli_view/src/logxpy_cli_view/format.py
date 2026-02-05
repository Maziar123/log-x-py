"""Formatting utilities for Eliot task values."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from functools import singledispatch
from typing import Any

from toolz import merge

_control_equivalents = {i: chr(0x2400 + i) for i in range(0x20)}
_control_equivalents[0x7F] = "\u2421"


def escape_control_characters(
    s: str,
    overrides: dict[int, str] | None = None,
) -> str:
    """Replace terminal control characters with Unicode equivalents."""
    overrides = overrides or {}
    return str(s).translate(merge(_control_equivalents, overrides))


def some(*fs: Callable[..., Any]) -> Callable[..., Any | None]:
    """Return first non-None result from applying arguments to each function."""
    def _some(*a: Any, **kw: Any) -> Any | None:
        for f in fs:
            result = f(*a, **kw)
            if result is not None:
                return result
        return None
    return _some


@singledispatch
def format_any(value: Any, field_name: str | None = None) -> str:
    """Format any value using repr (default handler)."""
    result = repr(value)
    if isinstance(result, bytes):
        result = result.decode("utf-8", "replace")
    return result


@format_any.register
def _(value: str, field_name: str | None = None) -> str:
    return value


@format_any.register
def _(value: bytes, field_name: str | None = None) -> str:
    return value.decode("utf-8", "replace")


@format_any.register
def _(value: bool, field_name: str | None = None) -> str:
    return "true" if value else "false"


def binary(encoding: str) -> Callable[[Any, str | None], str | None]:
    """Create a formatter for bytes values."""
    def _format(value: Any, field_name: str | None = None) -> str | None:
        if isinstance(value, bytes):
            return value.decode(encoding, "replace")
        return None
    return _format


def text() -> Callable[[Any, str | None], str | None]:
    """Create a formatter for str values."""
    def _format(value: Any, field_name: str | None = None) -> str | None:
        return value if isinstance(value, str) else None
    return _format


def fields(
    format_mapping: dict[str, Callable[[Any, str], Any]],
) -> Callable[[Any, str | None], Any | None]:
    """Create a formatter for specific fields."""
    def _format(value: Any, field_name: str | None = None) -> Any | None:
        f = format_mapping.get(field_name) if field_name else None
        return f(value, field_name) if f else None
    return _format


def timestamp(
    include_microsecond: bool = True,
    utc_timestamps: bool = True,
) -> Callable[[Any, str | None], str | None]:
    """Create a formatter for POSIX timestamp values."""
    def _format(value: Any, field_name: str | None = None) -> str | None:
        from_timestamp = (
            datetime.utcfromtimestamp if utc_timestamps else datetime.fromtimestamp
        )
        result = from_timestamp(float(value))
        if not include_microsecond:
            result = result.replace(microsecond=0)
        result_str = result.isoformat(" ")
        if isinstance(result_str, bytes):
            result_str = result_str.decode("ascii")
        return result_str + ("Z" if utc_timestamps else "")
    return _format


def duration() -> Callable[[Any, str | None], str | None]:
    """Create a formatter for duration values in seconds."""
    def _format(value: Any, field_name: str | None = None) -> str | None:
        return f"{value:.3f}s"
    return _format


def anything(encoding: str) -> Callable[[Any, str | None], str]:
    """Create a formatter for any value using repr (legacy, use format_any)."""
    def _format(value: Any, field_name: str | None = None) -> str:
        result = repr(value)
        if isinstance(result, bytes):
            result = result.decode(encoding, "replace")
        return result
    return _format


def truncate_value(limit: int, value: str) -> str:
    """Truncate value to maximum limit characters."""
    values = value.split("\n")
    first_line = values[0]
    if len(first_line) > limit or len(values) > 1:
        return f"{first_line[:limit]}\u2026"
    return value


__all__ = [
    "anything",
    "binary",
    "duration",
    "escape_control_characters",
    "fields",
    "format_any",
    "some",
    "text",
    "timestamp",
    "truncate_value",
]
