"""Shared dict utilities using boltons.

Provides convenient re-exports of commonly used boltons dictutils
for use across logxpy, logxpy_cli_view, and logxy-log-parser.

Reference: docs/boltons-ref.md
"""

from __future__ import annotations

import boltons.dictutils as du

__all__ = [
    # Core boltons dictutils classes
    "OrderedMultiDict",
    "OneToOne",
    "ManyToMany",
    "FrozenDict",
    # Common functions if needed
]


# Re-export commonly used classes
OrderedMultiDict = du.OrderedMultiDict
OneToOne = du.OneToOne
ManyToMany = du.ManyToMany
FrozenDict = du.FrozenDict


def get_nested(dct: dict, *keys, default=None):
    """Get nested dict value using key path.

    Args:
        dct: Dictionary to get value from
        *keys: Keys in path (e.g., get_nested(d, "a", "b", "c"))
        default: Default value if key not found

    Returns:
        Value at key path or default

    Example:
        >>> d = {"a": {"b": {"c": 1}}}
        >>> get_nested(d, "a", "b", "c")
        1
    """
    for key in keys:
        if isinstance(dct, dict):
            dct = dct.get(key)
        else:
            return default
    return dct


def set_nested(dct: dict, value, *keys):
    """Set nested dict value using key path.

    Args:
        dct: Dictionary to set value in
        value: Value to set
        *keys: Keys in path (e.g., set_nested(d, 1, "a", "b", "c"))

    Example:
        >>> d = {}
        >>> set_nested(d, 1, "a", "b", "c")
        >>> d
        {'a': {'b': {'c': 1}}}
    """
    for key in keys[:-1]:
        if key not in dct:
            dct[key] = {}
        dct = dct[key]
    dct[keys[-1]] = value
    return dct
