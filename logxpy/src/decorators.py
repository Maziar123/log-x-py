"""Logging decorators - @logged, @timed, @retry, @generator."""

from __future__ import annotations

import asyncio
import inspect
import time
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

from ._async import aaction, action
from ._base import truncate

P = ParamSpec("P")
T = TypeVar("T")

MASK_KEYS = {"password", "token", "secret", "key", "auth", "credential"}


def _extract_args(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    capture_self: bool,
    exclude: set[str],
) -> dict[str, Any]:
    sig = inspect.signature(func)
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()
    return {
        k: "***" if k in exclude else truncate(v)
        for k, v in bound.arguments.items()
        if not (k == "self" and not capture_self)
    }


def logged(
    fn: Callable[P, T] | None = None,
    *,
    level: str = "INFO",
    capture_args: bool = True,
    capture_result: bool = True,
    capture_self: bool = False,
    exclude: set[str] | None = None,
    timer: bool = True,
    when: Callable[..., bool] | None = None,
    max_depth: int = 3,
    max_length: int = 500,
    silent_errors: bool = False,
) -> Any:
    """Universal logging decorator for entry/exit/timing/args/result."""
    exclude = (exclude or set()) | MASK_KEYS

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        name = f"{func.__module__}.{func.__qualname__}"
        is_async = inspect.iscoroutinefunction(func)

        @wraps(func)
        async def async_impl(*a: P.args, **kw: P.kwargs) -> T:
            if when and not when(func, a, kw):
                # We know func is async if we are here
                return await cast("Awaitable[T]", func(*a, **kw))

            log_args: dict[str, Any] = {}
            if capture_args:
                try:
                    log_args = _extract_args(func, a, kw, capture_self, exclude)
                except Exception:
                    pass  # Best effort arg capture

            async with aaction(name, level=level, **log_args) as act:
                try:
                    result = await cast("Awaitable[T]", func(*a, **kw))
                    if capture_result and result is not None:
                        act.fields["result"] = truncate(result, max_depth, max_length)
                    return result
                except Exception as e:
                    if silent_errors:
                        act.fields["error_suppressed"] = str(e)
                        # We have to return something. Since we don't know T, we return None and cast it.
                        return cast("T", None)
                    raise

        @wraps(func)
        def sync_impl(*a: P.args, **kw: P.kwargs) -> T:
            if when and not when(func, a, kw):
                return func(*a, **kw)

            log_args: dict[str, Any] = {}
            if capture_args:
                try:
                    log_args = _extract_args(func, a, kw, capture_self, exclude)
                except Exception:
                    pass

            with action(name, level=level, **log_args) as act:
                try:
                    result = func(*a, **kw)
                    if capture_result and result is not None:
                        act.fields["result"] = truncate(result, max_depth, max_length)
                    return result
                except Exception as e:
                    if silent_errors:
                        act.fields["error_suppressed"] = str(e)
                        return cast("T", None)
                    raise

        return cast("Callable[P, T]", async_impl if is_async else sync_impl)

    return decorator(fn) if fn else decorator


def timed(metric: str | None = None) -> Any:
    """Timing-only decorator."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        name = metric or f"{func.__module__}.{func.__qualname__}"
        is_async = inspect.iscoroutinefunction(func)

        @wraps(func)
        async def async_impl(*a: P.args, **kw: P.kwargs) -> T:
            start = time.monotonic()
            try:
                return await cast("Awaitable[T]", func(*a, **kw))
            finally:
                from .loggerx import log

                log.debug(f"⏱ {func.__name__}", metric=name, duration_ms=round((time.monotonic() - start) * 1000, 2))

        @wraps(func)
        def sync_impl(*a: P.args, **kw: P.kwargs) -> T:
            start = time.monotonic()
            try:
                return func(*a, **kw)
            finally:
                from .loggerx import log

                log.debug(f"⏱ {func.__name__}", metric=name, duration_ms=round((time.monotonic() - start) * 1000, 2))

        return cast("Callable[P, T]", async_impl if is_async else sync_impl)

    return decorator


def retry(
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    on_retry: Callable[[int, Exception], None] | None = None,
) -> Any:
    """Retry with exponential backoff."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        is_async = inspect.iscoroutinefunction(func)

        @wraps(func)
        async def async_impl(*a: P.args, **kw: P.kwargs) -> T:
            d, last = delay, None
            for i in range(1, attempts + 1):
                try:
                    return await cast("Awaitable[T]", func(*a, **kw))
                except Exception as e:
                    last = e
                    if i == attempts:
                        raise
                    if on_retry:
                        on_retry(i, e)
                    await asyncio.sleep(d)
                    d *= backoff
            # Should be unreachable if attempts > 0 and we raise on last attempt
            raise last or Exception("Retry failed")

        @wraps(func)
        def sync_impl(*a: P.args, **kw: P.kwargs) -> T:
            d, last = delay, None
            for i in range(1, attempts + 1):
                try:
                    return func(*a, **kw)
                except Exception as e:
                    last = e
                    if i == attempts:
                        raise
                    if on_retry:
                        on_retry(i, e)
                    time.sleep(d)
                    d *= backoff
            raise last or Exception("Retry failed")

        return cast("Callable[P, T]", async_impl if is_async else sync_impl)

    return decorator


def generator(name: str | None = None, every: int = 100) -> Any:
    """Generator progress tracking."""

    def decorator(func: Callable[..., Iterator[T]]) -> Callable[..., Iterator[T]]:
        label = name or func.__name__

        @wraps(func)
        def wrapper(*a: Any, **kw: Any) -> Iterator[T]:
            from .loggerx import log

            for i, item in enumerate(func(*a, **kw), 1):
                if i % every == 0:
                    log.info(f"📦 {label}", count=i)
                yield item

        return wrapper

    return decorator


def aiterator(name: str | None = None, every: int = 100) -> Any:
    """Async iterator progress tracking."""

    def decorator(func: Callable[..., AsyncIterator[T]]) -> Callable[..., AsyncIterator[T]]:
        label = name or func.__name__

        @wraps(func)
        async def wrapper(*a: Any, **kw: Any) -> AsyncIterator[T]:
            from .loggerx import log

            i = 0
            async for item in func(*a, **kw):
                i += 1
                if i % every == 0:
                    log.info(f"📦 {label}", count=i)
                yield item

        return wrapper

    return decorator


def trace(name: str | None = None, kind: str = "internal", attributes: dict[str, Any] | None = None) -> Any:
    """OpenTelemetry trace decorator."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        span_name = name or f"{func.__module__}.{func.__qualname__}"
        is_async = inspect.iscoroutinefunction(func)

        @wraps(func)
        async def async_impl(*a: P.args, **kw: P.kwargs) -> T:
            try:
                from opentelemetry import trace as otel

                tracer = otel.get_tracer(__name__)
                with tracer.start_as_current_span(span_name, attributes=attributes):
                    return await cast("Awaitable[T]", func(*a, **kw))
            except ImportError:
                return await cast("Awaitable[T]", func(*a, **kw))

        @wraps(func)
        def sync_impl(*a: P.args, **kw: P.kwargs) -> T:
            try:
                from opentelemetry import trace as otel

                tracer = otel.get_tracer(__name__)
                with tracer.start_as_current_span(span_name, attributes=attributes):
                    return func(*a, **kw)
            except ImportError:
                return func(*a, **kw)

        return cast("Callable[P, T]", async_impl if is_async else sync_impl)

    return decorator
