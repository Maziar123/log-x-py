"""Compatibility utilities for eliot-tree."""

from __future__ import annotations

import json
import sys
from functools import wraps
from typing import Any, Callable, TypeVar, cast

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    import warnings
    from typing import ParamSpec

    P = ParamSpec("P")
    R = TypeVar("R")

    def deprecated(
        msg: str,
        /,
        *,
        category: type[Warning] = DeprecationWarning,
        stacklevel: int = 1,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Mark a function or class as deprecated."""
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                warnings.warn(msg, category, stacklevel=stacklevel + 1)
                return func(*args, **kwargs)
            return wrapper
        return decorator


F = TypeVar("F", bound=Callable[..., Any])


def dump_json_bytes(
    obj: Any,
    dumps: Callable[..., str] = json.dumps,
) -> bytes:
    """Serialize obj to JSON formatted UTF-8 encoded bytes."""
    return dumps(obj).encode("utf-8")


def catch_errors(
    *exceptions: type[Exception],
    reraise_as: type[Exception] | None = None,
    default: Any = None,
) -> Callable[[F], F]:
    """Decorator to catch and optionally rewrap exceptions."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if reraise_as is not None:
                    raise reraise_as(f"Error in {func.__name__}: {e}") from e
                return default
        return cast("F", wrapper)
    return decorator


__all__ = ["catch_errors", "deprecated", "dump_json_bytes"]
