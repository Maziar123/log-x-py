"""Shared utilities to reduce code duplication."""

from __future__ import annotations

import asyncio
import inspect
import sys
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar
from uuid import uuid4

P = ParamSpec("P")
T = TypeVar("T")

# === Time utilities ===
now = time.time
monotonic = time.monotonic


def uuid() -> str:
    return str(uuid4())


# === Async/sync wrapper factory ===
def dual_wrapper(
    async_impl: Callable[..., Any],
    sync_impl: Callable[..., Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Create wrapper that works for both async and sync functions."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
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


# === Value truncation ===
def truncate(obj: Any, max_depth: int = 3, max_len: int = 500) -> Any:
    """Truncate nested objects for logging."""
    if max_depth <= 0:
        return f"<{type(obj).__name__}>"
    match obj:
        case None | bool() | int() | float():
            return obj
        case str() if len(obj) > max_len:
            return obj[:max_len] + "..."
        case str():
            return obj
        case bytes():
            return f"<bytes:{len(obj)}>"
        case dict():
            return {str(k)[:50]: truncate(v, max_depth - 1, max_len) for k, v in list(obj.items())[:50]}
        case list() | tuple():
            items = [truncate(x, max_depth - 1, max_len) for x in obj[:100]]
            return items + [f"...+{len(obj) - 100}"] if len(obj) > 100 else items
        case _ if hasattr(obj, "__dataclass_fields__"):
            return {
                "_type": type(obj).__name__,
                **{f: truncate(getattr(obj, f), max_depth - 1, max_len) for f in obj.__dataclass_fields__},
            }
        case _:
            return {"_type": type(obj).__name__, "_repr": repr(obj)[:max_len]}


# === Module lazy import ===
def get_module(name: str) -> Any | None:
    return sys.modules.get(name)
