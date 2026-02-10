"""Tests for logxpy/src/decorators.py -- Logging decorators."""
from __future__ import annotations

import asyncio
import time

import pytest

from logxpy.src.decorators import (
    MASK_KEYS,
    _extract_args,
    aiterator,
    generator,
    logged,
    retry,
    timed,
    trace,
)


class TestLogged:
    def test_sync_function(self, captured_messages):
        @logged
        def add(x, y):
            return x + y

        result = add(1, 2)
        assert result == 3
        # The action context manager emits start + end records
        assert len(captured_messages) >= 2

    def test_async_function(self, captured_messages):
        @logged
        async def add(x, y):
            return x + y

        result = asyncio.run(add(1, 2))
        assert result == 3
        assert len(captured_messages) >= 2

    def test_capture_args(self, captured_messages):
        @logged(capture_args=True)
        def greet(name):
            return f"hello {name}"

        greet("world")
        # Start message should contain the arg (in fields, spread into the dict)
        start_msgs = [m for m in captured_messages if m.get("st") == "started"]
        assert any(m.get("name") == "world" for m in start_msgs)

    def test_capture_result(self, captured_messages):
        @logged(capture_result=True)
        def double(x):
            return x * 2

        double(5)
        end_msgs = [m for m in captured_messages if m.get("st") == "succeeded"]
        assert any(m.get("result") == 10 for m in end_msgs)

    def test_no_capture_result(self, captured_messages):
        @logged(capture_result=False)
        def double(x):
            return x * 2

        double(5)
        end_msgs = [m for m in captured_messages if m.get("st") == "succeeded"]
        assert not any("result" in m for m in end_msgs)

    def test_mask_sensitive_fields(self, captured_messages):
        """MASK_KEYS are merged into exclude, so 'password' args become '***'."""

        @logged(capture_args=True)
        def login(username, password):
            return True

        login("alice", "secret123")
        start_msgs = [m for m in captured_messages if m.get("st") == "started"]
        # password is in MASK_KEYS so should be masked
        assert any(m.get("password") == "***" for m in start_msgs)

    def test_exclude_fields(self, captured_messages):
        @logged(capture_args=True, exclude={"internal"})
        def func(x, internal):
            return x

        func(1, "hidden")
        start_msgs = [m for m in captured_messages if m.get("st") == "started"]
        assert any(m.get("internal") == "***" for m in start_msgs)

    def test_when_false_skips_logging(self, captured_messages):
        @logged(when=lambda f, a, kw: False)
        def func():
            return 42

        result = func()
        assert result == 42
        # When returns False => no action wrapper, so no start/end messages
        assert len(captured_messages) == 0

    def test_silent_errors_sync(self, captured_messages):
        @logged(silent_errors=True)
        def fail():
            raise ValueError("boom")

        result = fail()
        assert result is None
        end_msgs = [m for m in captured_messages if m.get("st") == "succeeded"]
        assert any("error_suppressed" in m for m in end_msgs)

    def test_silent_errors_async(self, captured_messages):
        @logged(silent_errors=True)
        async def fail():
            raise ValueError("boom")

        result = asyncio.run(fail())
        assert result is None

    def test_preserves_name(self):
        @logged
        def my_func():
            pass

        assert my_func.__name__ == "my_func"

    def test_exception_propagates(self, captured_messages):
        @logged
        def fail():
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            fail()

    def test_no_capture_args(self, captured_messages):
        """When capture_args=False, arguments should not appear in start message."""

        @logged(capture_args=False)
        def greet(name):
            return f"hello {name}"

        greet("world")
        start_msgs = [m for m in captured_messages if m.get("st") == "started"]
        assert not any("name" in m for m in start_msgs)


class TestTimed:
    def test_sync_timing(self, captured_messages):
        @timed()
        def slow():
            time.sleep(0.01)
            return 42

        result = slow()
        assert result == 42
        assert any("duration_ms" in m for m in captured_messages)

    def test_custom_metric_name(self, captured_messages):
        @timed(metric="my.metric")
        def func():
            return 1

        func()
        assert any(m.get("metric") == "my.metric" for m in captured_messages)

    def test_async_timing(self, captured_messages):
        @timed()
        async def slow():
            await asyncio.sleep(0.01)
            return 42

        result = asyncio.run(slow())
        assert result == 42
        assert any("duration_ms" in m for m in captured_messages)

    def test_preserves_name(self):
        @timed()
        def my_func():
            pass

        assert my_func.__name__ == "my_func"


class TestRetry:
    def test_succeeds_first_try(self, captured_messages):
        call_count = 0

        @retry(attempts=3, delay=0.001)
        def succeed():
            nonlocal call_count
            call_count += 1
            return 42

        result = succeed()
        assert result == 42
        assert call_count == 1

    def test_retries_on_failure(self, captured_messages):
        call_count = 0

        @retry(attempts=3, delay=0.001)
        def fail_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("not yet")
            return "ok"

        result = fail_twice()
        assert result == "ok"
        assert call_count == 3

    def test_max_attempts_exceeded(self, captured_messages):
        @retry(attempts=2, delay=0.001)
        def always_fail():
            raise ValueError("nope")

        with pytest.raises(ValueError, match="nope"):
            always_fail()

    def test_on_retry_callback(self, captured_messages):
        retries = []

        @retry(attempts=3, delay=0.001, on_retry=lambda i, e: retries.append(i))
        def fail_once():
            if len(retries) == 0:
                raise ValueError("first")
            return "ok"

        fail_once()
        assert len(retries) == 1

    def test_async_retry(self, captured_messages):
        call_count = 0

        @retry(attempts=3, delay=0.001)
        async def fail_once():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("not yet")
            return "ok"

        result = asyncio.run(fail_once())
        assert result == "ok"
        assert call_count == 2

    def test_backoff_multiplier(self, captured_messages):
        """Ensure the delay increases with backoff multiplier."""
        call_count = 0
        timestamps = []

        @retry(attempts=3, delay=0.01, backoff=2.0)
        def fail_twice():
            nonlocal call_count
            call_count += 1
            timestamps.append(time.monotonic())
            if call_count < 3:
                raise ValueError("not yet")
            return "ok"

        result = fail_twice()
        assert result == "ok"
        assert call_count == 3
        # Second delay should be longer than first
        if len(timestamps) == 3:
            gap1 = timestamps[1] - timestamps[0]
            gap2 = timestamps[2] - timestamps[1]
            assert gap2 > gap1


class TestGenerator:
    def test_yields_all_items(self, captured_messages):
        @generator(every=2)
        def gen():
            for i in range(5):
                yield i

        items = list(gen())
        assert items == [0, 1, 2, 3, 4]

    def test_logs_progress(self, captured_messages):
        @generator(every=2)
        def gen():
            for i in range(6):
                yield i

        list(gen())
        # Progress logged at count=2, 4, 6
        progress_msgs = [m for m in captured_messages if "count" in m]
        assert len(progress_msgs) >= 2

    def test_preserves_name(self):
        @generator(every=10)
        def my_gen():
            yield 1

        assert my_gen.__name__ == "my_gen"


class TestAiterator:
    def test_async_iteration(self, captured_messages):
        @aiterator(every=2)
        async def gen():
            for i in range(4):
                yield i

        async def run():
            return [item async for item in gen()]

        items = asyncio.run(run())
        assert items == [0, 1, 2, 3]

    def test_logs_progress(self, captured_messages):
        @aiterator(every=2)
        async def gen():
            for i in range(6):
                yield i

        async def run():
            return [item async for item in gen()]

        asyncio.run(run())
        progress_msgs = [m for m in captured_messages if "count" in m]
        assert len(progress_msgs) >= 2


class TestTrace:
    def test_works_without_opentelemetry(self, captured_messages):
        @trace()
        def func():
            return 42

        result = func()
        assert result == 42

    def test_preserves_name(self):
        @trace()
        def my_func():
            pass

        assert my_func.__name__ == "my_func"

    def test_async_trace(self, captured_messages):
        @trace()
        async def func():
            return 42

        result = asyncio.run(func())
        assert result == 42


class TestExtractArgs:
    def test_basic_extraction(self):
        def func(a, b, c=3):
            pass

        result = _extract_args(func, (1, 2), {}, False, set())
        assert result["a"] == 1
        assert result["b"] == 2
        assert result["c"] == 3

    def test_excludes_self(self):
        def method(self, x):
            pass

        result = _extract_args(method, ("instance", 10), {}, False, set())
        assert "self" not in result
        assert result["x"] == 10

    def test_includes_self_when_requested(self):
        def method(self, x):
            pass

        result = _extract_args(method, ("instance", 10), {}, True, set())
        assert "self" in result

    def test_masks_excluded_keys(self):
        def func(a, secret):
            pass

        result = _extract_args(func, (1, "hidden"), {}, False, {"secret"})
        assert result["secret"] == "***"


class TestMaskKeys:
    def test_default_mask_keys(self):
        assert "password" in MASK_KEYS
        assert "token" in MASK_KEYS
        assert "secret" in MASK_KEYS
        assert "key" in MASK_KEYS
        assert "auth" in MASK_KEYS
        assert "credential" in MASK_KEYS
