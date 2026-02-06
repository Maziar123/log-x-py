"""Utility functions for logxpy-cli-view."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class _Namespace:
    """Represents a namespaced field."""

    prefix: str
    name: str

    def __str__(self) -> str:
        return f"{self.prefix}/{self.name}"


def namespaced(prefix: str) -> Callable[[str], _Namespace]:
    """Create a namespaced field factory."""
    def _namespace(name: str) -> _Namespace:
        return _Namespace(prefix, name)
    _namespace.__doc__ = f"Create a {prefix} namespaced field"
    return _namespace


def format_namespace(ns: _Namespace) -> str:
    """Format a namespace as a string."""
    return str(ns)


def is_namespace(value: Any) -> bool:
    """Check if a value is a namespace."""
    return isinstance(value, _Namespace)


# Pre-defined logxpy namespace factory
logxpy_ns = namespaced("logxpy")
eliot_ns = logxpy_ns  # Backwards compatibility alias


@runtime_checkable
class Writable(Protocol):
    """Protocol for objects that can be written to."""

    def write(self, s: str) -> Any:
        """Write string to the output."""
        ...


__all__ = ["Writable", "_Namespace", "eliot_ns", "format_namespace", "is_namespace", "namespaced"]
