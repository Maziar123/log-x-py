"""Shared utilities to reduce code duplication.

Python 3.12+ features used:
- Type aliases (PEP 695): `type Name = ...`
- Pattern matching (PEP 634): Clean value routing
- Walrus operator (PEP 572): Assignment expressions
- Parameter specs (PEP 612): Generic callable types

Boltons features used:
- boltons.iterutils: Advanced iteration utilities
- boltons.cacheutils: Memoization decorators
- boltons.strutils: String manipulation utilities
"""

from __future__ import annotations

import asyncio
import inspect
import sys
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar
from uuid import uuid4

# Import boltons utilities
from boltons.cacheutils import cachedproperty
from boltons.iterutils import first, is_iterable
from boltons.strutils import (asciify, cardinalize, split_punct_ws,
                              strip_ansi)

# ============================================================================
# Type Aliases (PEP 695 - Python 3.12+)
# ============================================================================

type AnyCallable = Callable[..., Any]
type AsyncCallable = Callable[..., Any]  # Coroutine
type SyncCallable = Callable[..., Any]

P = ParamSpec("P")
T = TypeVar("T")


# ============================================================================
# Time Utilities
# ============================================================================

now: Callable[[], float] = time.time
monotonic: Callable[[], float] = time.monotonic


def uuid(use_sqid: bool | None = None) -> str:
    """
    Generate task ID.
    
    Args:
        use_sqid: Use short Sqid (True), UUID4 (False), or auto-detect (None).
                 Auto mode uses Sqid for single-process logs (default).
    
    Returns:
        Task identifier string. Sqids are 4-12 chars, UUID4 is 36 chars.
    
    Examples:
        >>> uuid()           # "Xa.b" (4 chars, Sqid)
        >>> uuid(use_sqid=False)  # "59b00749-eb24-4c31-a2c8-aac523d7bfd9" (36 chars)
    """
    if use_sqid is None:
        # Auto-detect: Check environment for distributed mode
        import os
        use_sqid = not os.environ.get("LOGXPY_DISTRIBUTED")
    
    if use_sqid:
        # Use hierarchical Sqid (ultra-short, logging-optimized)
        from ._sqid import sqid
        return sqid()
    
    # Fallback to UUID4 for distributed systems
    return str(uuid4())


# ============================================================================
# Async/Sync Wrapper Factory
# ============================================================================

def dual_wrapper(
    async_impl: AsyncCallable,
    sync_impl: SyncCallable | None = None,
) -> Callable[[AnyCallable], AnyCallable]:
    """Create wrapper that works for both async and sync functions.

    Args:
        async_impl: The async implementation to use.
        sync_impl: Optional sync implementation. If not provided,
            uses asyncio.run to execute the async impl.

    Returns:
        A decorator that returns the appropriate wrapper based on
        whether the decorated function is async or sync.
    """

    def decorator(func: AnyCallable) -> AnyCallable:
        is_async = inspect.iscoroutinefunction(func)

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await async_impl(func, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            impl = sync_impl or (lambda f, *a, **k: asyncio.run(async_impl(f, *a, **k)))  # type: ignore
            return impl(func, *args, **kwargs)

        return async_wrapper if is_async else sync_wrapper

    return decorator


# ============================================================================
# Value Truncation (enhanced with boltons)
# ============================================================================

def truncate(obj: Any, max_depth: int = 3, max_len: int = 500) -> Any:
    """Truncate nested objects for logging.

    Uses pattern matching (PEP 634) for clean type-based routing.

    Args:
        obj: The object to truncate.
        max_depth: Maximum nesting depth to preserve.
        max_len: Maximum string length before truncation.

    Returns:
        A truncated representation of the object.
    """
    if max_depth <= 0:
        return f"<{type(obj).__name__}>"

    match obj:
        # Primitives pass through unchanged
        case None | bool() | int() | float():
            return obj

        # Strings get truncated with ellipsis
        case str() if len(obj) > max_len:
            return obj[:max_len] + "..."
        case str():
            return obj

        # Bytes get size annotation
        case bytes():
            return f"<bytes:{len(obj)}>"

        # Dicts get truncated recursively (keys and values)
        case dict():
            return {
                str(k)[:50]: truncate(v, max_depth - 1, max_len)
                for k, v in list(obj.items())[:50]
            }

        # Lists/tuples get truncated (max 100 items)
        case list() | tuple():
            items = [truncate(x, max_depth - 1, max_len) for x in obj[:100]]
            if len(obj) > 100:
                items = items + [f"...+{len(obj) - 100}"]
            return items

        # Dataclasses get converted to dict
        case _ if hasattr(obj, "__dataclass_fields__"):
            return {
                "_type": type(obj).__name__,
                **{
                    f: truncate(getattr(obj, f), max_depth - 1, max_len)
                    for f in obj.__dataclass_fields__
                },
            }

        # Everything else gets type and repr
        case _:
            return {"_type": type(obj).__name__, "_repr": repr(obj)[:max_len]}


# ============================================================================
# String Utilities (using boltons.strutils)
# ============================================================================

def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text using boltons.

    Args:
        text: String potentially containing ANSI codes.

    Returns:
        String with ANSI codes removed.
    """
    return strip_ansi(text)


def escape_html_text(text: str) -> str:
    """Escape HTML special characters using html.escape.

    Args:
        text: Plain text string.

    Returns:
        HTML-escaped string.
    """
    from html import escape
    return escape(text)


def pluralize(count: int, word: str) -> str:
    """Pluralize a word based on count using boltons.

    Args:
        count: The number to check for plurality.
        word: The word to pluralize.

    Returns:
        "word" or "words" based on count.
    """
    return cardinalize(word, count)


def clean_text(text: str, *,
               remove_ansi: bool = True,
               asciify_: bool = False,
               split_punct: bool = False) -> str:
    """Clean text using boltons string utilities.

    Args:
        text: The text to clean.
        remove_ansi: Remove ANSI escape codes.
        asciify_: Convert unicode to ASCII approximation.
        split_punct: Split on punctuation and whitespace.

    Returns:
        Cleaned text string.
    """
    result = text

    if remove_ansi:
        result = strip_ansi(result)

    if asciify_:
        result = asciify(result)

    if split_punct:
        result = " ".join(split_punct_ws(result))

    return result


# ============================================================================
# Iteration Utilities (using boltons.iterutils)
# ============================================================================

def get_first(iterable: Any, default: T | None = None) -> Any | T | None:
    """Get first item from iterable using boltons.

    Args:
        iterable: Any iterable object.
        default: Default value if iterable is empty.

    Returns:
        First item or default value.
    """
    return first(iterable, default=default)


def is_non_string_iterable(obj: Any) -> bool:
    """Check if object is iterable but not a string.

    Args:
        obj: Object to check.

    Returns:
        True if object is iterable and not a string.
    """
    return is_iterable(obj) and not isinstance(obj, (str, bytes))


# ============================================================================
# Module Utilities
# ============================================================================

def get_module(name: str) -> Any | None:
    """Get a module from sys.modules if loaded.

    Args:
        name: Fully qualified module name.

    Returns:
        The module object if loaded, None otherwise.
    """
    return sys.modules.get(name)


# ============================================================================
# Cached Property (from boltons)
# ============================================================================

# Re-export boltons cachedproperty for convenience
__all__ = [
    "now",
    "monotonic",
    "uuid",
    "dual_wrapper",
    "truncate",
    "strip_ansi_codes",
    "escape_html_text",
    "pluralize",
    "clean_text",
    "get_first",
    "is_non_string_iterable",
    "get_module",
    "cachedproperty",
]
