"""
Caching utilities using boltons.cacheutils.

This module provides memoization and caching helpers for performance
optimization throughout the LogXPy ecosystem.

Python 3.12+ features used:
- Type aliases (PEP 695): `type Name = ...`
- Decorator patterns with boltons
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

from boltons.cacheutils import cached, cachedproperty

# ============================================================================
# Type Aliases (PEP 695 - Python 3.12+)
# ============================================================================

type CacheKey = tuple[Any, ...]
type CachedFunc = Callable[..., Any]
T = TypeVar("T")


# ============================================================================
# Memoization Decorators
# ============================================================================

def memoize(func: Callable[..., T] | None = None, *, size: int = 128) -> Callable[..., T]:
    """
    Memoize a function with an LRU cache.

    Uses boltons.cacheutils.cached for efficient memoization.

    @param func: The function to memoize, or None if used as a factory.
    @param size: Maximum number of results to cache.
    @return: Memoized function or decorator factory.

    Example:
        @memoize
        def expensive_calc(x):
            return x ** 2

        @memoize(size=256)
        def heavy_computation(a, b):
            return a * b + a / b
    """
    def decorator(f: Callable[..., T]) -> Callable[..., T]:
        cache: dict[CacheKey, T] = {}

        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Create cache key from args and sorted kwargs
            key = (args, tuple(sorted(kwargs.items())))
            if key not in cache:
                if len(cache) >= size:
                    # Simple FIFO eviction - for LRU, use functools.lru_cache
                    cache.pop(next(iter(cache)))
                cache[key] = f(*args, **kwargs)
            return cache[key]

        # Add cache management methods
        wrapper.cache_clear = lambda: cache.clear()  # type: ignore
        wrapper.cache_info = lambda: f"Cache size: {len(cache)}/{size}"  # type: ignore

        return wrapper

    if func is None:
        return decorator  # type: ignore
    return decorator(func)


def memoize_method(func: Callable[..., T]) -> property:
    """
    Create a cached property for a class method.

    Uses boltons.cacheutils.cachedproperty for efficient per-instance caching.

    @param func: The method to cache.
    @return: A property that caches the result per instance.

    Example:
        class MyClass:
            @memoize_method
            def expensive_property(self):
                return calculate_something()
    """
    return cachedproperty(func)


# ============================================================================
# Cache-Control Decorators
# ============================================================================

def cache_until_invalidation(
    func: Callable[..., T] | None = None,
    *,
    attr_name: str = "_cache_invalidated",
) -> Callable[..., T] | Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Cache a function's result until explicitly invalidated.

    Useful for expensive computations that need to be recomputed
    on demand rather than by time or size.

    @param func: The function to cache, or None if used as a factory.
    @param attr_name: Attribute name to track invalidation.
    @return: Cached function or decorator factory.

    Example:
        class DataProcessor:
            @cache_until_invalidation
            def process_data(self):
                return expensive_operation()

            def invalidate(self):
                self._cache_invalidated = True
    """

    def decorator(f: Callable[..., T]) -> Callable[..., T]:
        @wraps(f)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> T:
            # Check if cache is invalidated
            if getattr(self, attr_name, False):
                result = f(self, *args, **kwargs)
                setattr(self, f"_cached_{f.__name__}", result)
                setattr(self, attr_name, False)
                return result

            # Return cached result if available
            cached_attr = f"_cached_{f.__name__}"
            if hasattr(self, cached_attr):
                return getattr(self, cached_attr)

            # Compute and cache
            result = f(self, *args, **kwargs)
            setattr(self, cached_attr, result)
            return result

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


# ============================================================================
# Throttling Decorators
# ============================================================================

def throttle(
    func: Callable[..., T] | None = None,
    *,
    max_calls: int = 1,
    period: float = 1.0,
) -> Callable[..., T] | Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Throttle a function so it can only be called a maximum number of times
    within a given period.

    @param func: The function to throttle, or None if used as a factory.
    @param max_calls: Maximum number of calls allowed in the period.
    @param period: Time period in seconds.
    @return: Throttled function or decorator factory.

    Example:
        @throttle(max_calls=5, period=60)
        def send_notification(message):
            api.send(message)
    """
    import time

    def decorator(f: Callable[..., T]) -> Callable[..., T]:
        call_times: list[float] = []

        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            now = time.time()

            # Remove old call times outside the period
            call_times[:] = [t for t in call_times if now - t < period]

            # Check if we've exceeded the limit
            if len(call_times) >= max_calls:
                raise RuntimeError(
                    f"Function {f.__name__} throttled: "
                    f"{max_calls} calls per {period} seconds allowed"
                )

            call_times.append(now)
            return f(*args, **kwargs)

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


# ============================================================================
# Cache Statistics
# ============================================================================

class CacheStats:
    """
    Simple cache statistics tracker.

    Useful for monitoring cache effectiveness during development
    and testing.
    """

    __slots__ = ("hits", "misses", "size")

    def __init__(self) -> None:
        self.hits: int = 0
        self.misses: int = 0
        self.size: int = 0

    def record_hit(self) -> None:
        """Record a cache hit."""
        self.hits += 1

    def record_miss(self) -> None:
        """Record a cache miss."""
        self.misses += 1

    def set_size(self, size: int) -> None:
        """Set the current cache size."""
        self.size = size

    @property
    def hit_rate(self) -> float:
        """Calculate the cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def __repr__(self) -> str:
        return f"CacheStats(hits={self.hits}, misses={self.misses}, size={self.size}, hit_rate={self.hit_rate:.2%})"


# ============================================================================
# Exported Symbols
# ============================================================================

__all__ = [
    "memoize",
    "memoize_method",
    "cache_until_invalidation",
    "throttle",
    "CacheStats",
    # Re-export from boltons
    "cached",
    "cachedproperty",
]
