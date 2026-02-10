"""Tests for logxpy/src/_cache.py -- Caching utilities."""
from __future__ import annotations
import time
import pytest
from logxpy.src._cache import memoize, throttle, CacheStats

class TestMemoize:
    def test_caches_result(self):
        call_count = 0
        @memoize
        def func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        assert func(5) == 10
        assert func(5) == 10
        assert call_count == 1

    def test_different_args(self):
        call_count = 0
        @memoize
        def func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        func(1)
        func(2)
        assert call_count == 2

    def test_cache_clear(self):
        call_count = 0
        @memoize
        def func(x):
            nonlocal call_count
            call_count += 1
            return x
        func(1)
        func.cache_clear()
        func(1)
        assert call_count == 2

    def test_size_limit(self):
        @memoize(size=2)
        def func(x):
            return x * 2
        func(1)
        func(2)
        func(3)  # Should evict oldest
        # Just verify it doesn't crash
        assert func(3) == 6

    def test_factory_usage(self):
        @memoize(size=10)
        def func(x):
            return x
        assert func(1) == 1

class TestThrottle:
    def test_within_limit(self):
        @throttle(max_calls=5, period=1.0)
        def func():
            return "ok"
        for _ in range(5):
            assert func() == "ok"

    def test_over_limit(self):
        @throttle(max_calls=2, period=10.0)
        def func():
            return "ok"
        func()
        func()
        with pytest.raises(RuntimeError, match="throttled"):
            func()

class TestCacheStats:
    def test_initial_values(self):
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.size == 0

    def test_record_hit(self):
        stats = CacheStats()
        stats.record_hit()
        assert stats.hits == 1

    def test_record_miss(self):
        stats = CacheStats()
        stats.record_miss()
        assert stats.misses == 1

    def test_hit_rate(self):
        stats = CacheStats()
        stats.record_hit()
        stats.record_hit()
        stats.record_miss()
        assert abs(stats.hit_rate - 2/3) < 0.01

    def test_hit_rate_empty(self):
        stats = CacheStats()
        assert stats.hit_rate == 0.0

    def test_repr(self):
        stats = CacheStats()
        assert "CacheStats" in repr(stats)
