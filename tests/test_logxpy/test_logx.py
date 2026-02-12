"""Tests for logxpy/src/logx.py -- Main Logger fluent API.

Tests cover:
- Logger init, level methods, callable, send, data types
- System methods, file methods, context, color, configure, span
- Async methods: flush(), enable_adaptive(), disable_adaptive()
- Real file I/O verification for async flush techniques
"""
from __future__ import annotations

import datetime as _dt
import json
from enum import Enum
from io import BytesIO, StringIO
from pathlib import Path

from logxpy.src._types import Level
from logxpy.src.logx import Logger


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_log(path: Path) -> list[dict]:
    """Read a log file and return parsed JSON lines."""
    text = path.read_text().strip()
    if not text:
        return []
    return [json.loads(line) for line in text.splitlines() if line.strip()]


# ============================================================================
# Logger Init
# ============================================================================

class TestLoggerInit:
    def test_default_name(self):
        l = Logger()
        assert l._name == "root"

    def test_custom_name(self):
        l = Logger("app")
        assert l._name == "app"

    def test_default_level(self):
        l = Logger()
        assert l._level == Level.DEBUG


# ============================================================================
# Level Methods - Fluent Return
# ============================================================================

class TestLevelMethods:
    def test_debug_returns_self(self, fresh_logger, captured_messages):
        assert fresh_logger.debug("msg") is fresh_logger

    def test_info_returns_self(self, fresh_logger, captured_messages):
        assert fresh_logger.info("msg") is fresh_logger

    def test_success_returns_self(self, fresh_logger, captured_messages):
        assert fresh_logger.success("msg") is fresh_logger

    def test_note_returns_self(self, fresh_logger, captured_messages):
        assert fresh_logger.note("msg") is fresh_logger

    def test_warning_returns_self(self, fresh_logger, captured_messages):
        assert fresh_logger.warning("msg") is fresh_logger

    def test_error_returns_self(self, fresh_logger, captured_messages):
        assert fresh_logger.error("msg") is fresh_logger

    def test_critical_returns_self(self, fresh_logger, captured_messages):
        assert fresh_logger.critical("msg") is fresh_logger

    def test_checkpoint_adds_emoji_prefix(self, captured_messages):
        l = Logger("test")
        l.checkpoint("step1")
        msgs = [m for m in captured_messages if "📍" in m.get("msg", "")]
        assert len(msgs) == 1

    def test_exception_includes_traceback(self, captured_messages):
        l = Logger("test")
        try:
            raise ValueError("test error")
        except ValueError:
            l.exception("caught error")
        msgs = [m for m in captured_messages if "logxpy:traceback" in m]
        assert len(msgs) >= 1

    def test_fluent_chaining(self, captured_messages):
        l = Logger("test")
        result = l.debug("a").info("b").warning("c")
        assert result is l
        assert len(captured_messages) == 3


# ============================================================================
# Level Filtering
# ============================================================================

class TestLevelFiltering:
    def test_below_level_suppressed(self, captured_messages):
        l = Logger("test")
        l._level = Level.WARNING
        l.debug("should not appear")
        l.info("should not appear")
        assert len(captured_messages) == 0

    def test_at_level_emitted(self, captured_messages):
        l = Logger("test")
        l._level = Level.WARNING
        l.warning("should appear")
        assert len(captured_messages) == 1

    def test_above_level_emitted(self, captured_messages):
        l = Logger("test")
        l._level = Level.WARNING
        l.error("should appear")
        assert len(captured_messages) == 1


# ============================================================================
# Callable
# ============================================================================

class TestCallable:
    def test_call_with_string(self, captured_messages):
        l = Logger("test")
        result = l("hello")
        assert result is l
        assert len(captured_messages) == 1

    def test_call_with_string_and_simple_value(self, captured_messages):
        l = Logger("test")
        l("title", 42)
        assert len(captured_messages) == 1

    def test_call_with_string_and_data(self, captured_messages):
        l = Logger("test")
        l("title", {"key": "val"})
        assert len(captured_messages) == 1

    def test_call_with_dict(self, captured_messages):
        l = Logger("test")
        l({"key": "val"})
        assert len(captured_messages) == 1

    def test_call_with_none_returns_self(self, captured_messages):
        l = Logger("test")
        result = l(None)
        assert result is l
        assert len(captured_messages) == 0


# ============================================================================
# Send
# ============================================================================

class TestSend:
    def test_send_formats_data(self, captured_messages):
        l = Logger("test")
        l.send("test msg", {"x": 1})
        assert len(captured_messages) == 1


# ============================================================================
# Data Type Methods
# ============================================================================

class TestDataTypeMethods:
    def test_color_rgb_tuple(self, captured_messages):
        l = Logger("test")
        result = l.color((255, 0, 0))
        assert result is l
        assert len(captured_messages) == 1

    def test_color_hex_string(self, captured_messages):
        l = Logger("test")
        l.color("#ff0000")
        assert len(captured_messages) == 1

    def test_color_int(self, captured_messages):
        l = Logger("test")
        l.color(0xFF0000)
        assert len(captured_messages) == 1

    def test_currency(self, captured_messages):
        l = Logger("test")
        result = l.currency("19.99", "USD")
        assert result is l
        assert len(captured_messages) == 1

    def test_datetime_from_object(self, captured_messages):
        l = Logger("test")
        dt = _dt.datetime(2024, 1, 15, 12, 0, 0)
        result = l.datetime(dt)
        assert result is l
        assert len(captured_messages) == 1

    def test_datetime_none_uses_now(self, captured_messages):
        l = Logger("test")
        l.datetime()
        assert len(captured_messages) == 1

    def test_enum_value(self, captured_messages):
        class Color(Enum):
            RED = 1

        l = Logger("test")
        result = l.enum(Color.RED)
        assert result is l
        assert len(captured_messages) == 1

    def test_enum_non_enum_warns(self, captured_messages):
        l = Logger("test")
        l.enum("not_enum")
        assert len(captured_messages) == 1

    def test_ptr(self, captured_messages):
        l = Logger("test")
        obj = object()
        result = l.ptr(obj)
        assert result is l
        assert len(captured_messages) == 1

    def test_variant(self, captured_messages):
        l = Logger("test")
        result = l.variant(42)
        assert result is l
        assert len(captured_messages) == 1

    def test_sset(self, captured_messages):
        l = Logger("test")
        result = l.sset({1, 2, 3})
        assert result is l
        assert len(captured_messages) == 1

    def test_json_method(self, captured_messages):
        l = Logger("test")
        result = l.json({"k": "v"})
        assert result is l
        assert len(captured_messages) == 1

    def test_table(self, captured_messages):
        l = Logger("test")
        result = l.table([{"a": 1}])
        assert result is l

    def test_tree(self, captured_messages):
        l = Logger("test")
        result = l.tree({"a": {"b": 1}})
        assert result is l


# ============================================================================
# System Methods
# ============================================================================

class TestSystemMethods:
    def test_system_info(self, captured_messages):
        l = Logger("test")
        result = l.system_info()
        assert result is l
        assert len(captured_messages) == 1

    def test_memory_status(self, captured_messages):
        l = Logger("test")
        result = l.memory_status()
        assert result is l
        assert len(captured_messages) == 1

    def test_memory_hex(self, captured_messages):
        l = Logger("test")
        result = l.memory_hex(b"\x00\x01\x02\x03")
        assert result is l
        assert len(captured_messages) == 1

    def test_memory_hex_non_bytes(self, captured_messages):
        l = Logger("test")
        l.memory_hex("not bytes")
        # Should log a warning instead
        assert len(captured_messages) == 1

    def test_stack_trace(self, captured_messages):
        l = Logger("test")
        result = l.stack_trace()
        assert result is l
        assert len(captured_messages) == 1


# ============================================================================
# File Methods
# ============================================================================

class TestFileMethods:
    def test_file_hex(self, tmp_path, captured_messages):
        p = tmp_path / "test.bin"
        p.write_bytes(b"\xDE\xAD\xBE\xEF")
        l = Logger("test")
        result = l.file_hex(p)
        assert result is l
        assert len(captured_messages) == 1

    def test_file_hex_not_found(self, captured_messages):
        l = Logger("test")
        l.file_hex("/nonexistent/path")
        assert len(captured_messages) == 1

    def test_file_text(self, tmp_path, captured_messages):
        p = tmp_path / "test.txt"
        p.write_text("hello\nworld\n")
        l = Logger("test")
        result = l.file_text(p)
        assert result is l
        assert len(captured_messages) == 1

    def test_file_text_not_found(self, captured_messages):
        l = Logger("test")
        l.file_text("/nonexistent/path")
        assert len(captured_messages) == 1

    def test_stream_hex(self, captured_messages):
        l = Logger("test")
        result = l.stream_hex(BytesIO(b"\x00\x01\x02"))
        assert result is l
        assert len(captured_messages) == 1

    def test_stream_text(self, captured_messages):
        l = Logger("test")
        result = l.stream_text(StringIO("line1\nline2\n"))
        assert result is l
        assert len(captured_messages) == 1


# ============================================================================
# Context
# ============================================================================

class TestContext:
    def test_scope_context_manager(self, captured_messages):
        l = Logger("test")
        with l.scope(user_id=123):
            l.info("inside scope")
        msgs = [m for m in captured_messages if m.get("user_id") == 123]
        assert len(msgs) == 1

    def test_scope_nested(self, captured_messages):
        l = Logger("test")
        with l.scope(a=1):
            with l.scope(b=2):
                l.info("nested")
        msgs = [m for m in captured_messages if m.get("a") == 1 and m.get("b") == 2]
        assert len(msgs) == 1

    def test_ctx_returns_new_logger(self):
        l = Logger("test")
        child = l.ctx(user=1)
        assert child is not l
        assert child._context["user"] == 1

    def test_ctx_adds_context_to_messages(self, captured_messages):
        l = Logger("test")
        child = l.ctx(user_id=42)
        child.info("with context")
        msgs = [m for m in captured_messages if m.get("user_id") == 42]
        assert len(msgs) == 1

    def test_new_creates_child_name(self):
        l = Logger("root")
        child = l.new("db")
        assert child._name == "root.db"

    def test_new_inherits_context(self):
        l = Logger("root", context={"env": "test"})
        child = l.new("db")
        assert child._context["env"] == "test"


# ============================================================================
# Color Methods
# ============================================================================

class TestColorMethods:
    def test_set_foreground_returns_self(self):
        l = Logger("test")
        assert l.set_foreground("red") is l

    def test_set_foreground_adds_to_context(self):
        l = Logger("test")
        l.set_foreground("red")
        assert l._context["fg"] == "red"

    def test_set_background_returns_self(self):
        l = Logger("test")
        assert l.set_background("yellow") is l

    def test_reset_foreground(self):
        l = Logger("test")
        l.set_foreground("red").reset_foreground()
        assert "fg" not in l._context

    def test_reset_background(self):
        l = Logger("test")
        l.set_background("yellow").reset_background()
        assert "bg" not in l._context

    def test_colored_one_shot(self, captured_messages):
        l = Logger("test")
        result = l.colored("msg", "red", "yellow")
        assert result is l
        msgs = [m for m in captured_messages if m.get("fg") == "red"]
        assert len(msgs) == 1


# ============================================================================
# Configure
# ============================================================================

class TestConfigure:
    def test_sets_level(self):
        l = Logger("test")
        result = l.configure(level="WARNING")
        assert l._level == Level.WARNING
        assert result is l

    def test_sets_mask_fields(self):
        l = Logger("test")
        l.configure(mask_fields=["password"])
        assert l._masker is not None

    def test_returns_self(self):
        l = Logger("test")
        assert l.configure() is l


# ============================================================================
# Span
# ============================================================================

class TestSpan:
    def test_span_without_opentelemetry(self):
        l = Logger("test")
        with l.span("test_span") as span:
            assert hasattr(span, "set_attribute")
            assert hasattr(span, "add_event")


# ============================================================================
# Async Methods (unit)
# ============================================================================

class TestAsyncMethods:
    def test_is_async_default_false(self):
        l = Logger("test")
        assert l.is_async is False

    def test_get_async_metrics_no_writer(self):
        l = Logger("test")
        metrics = l.get_async_metrics()
        assert metrics["enqueued"] == 0
        assert metrics["written"] == 0

    def test_sync_mode_context(self, captured_messages):
        l = Logger("test")
        with l.sync_mode():
            l.info("sync message")
        assert len(captured_messages) >= 1


# ============================================================================
# Async Flush - Real File I/O
# ============================================================================

class TestAsyncFlushRealFile:
    """Logger.flush() with real async writer and file verification."""

    def test_flush_writes_to_file(self, tmp_path: Path):
        """log.flush() forces all pending messages to disk."""
        log_file = tmp_path / "flush.log"
        logger = Logger()
        logger.init(str(log_file), size=10000, flush=60.0)

        for i in range(15):
            logger.info(f"flush-{i}")

        logger.flush(timeout=5.0)

        entries = _parse_log(log_file)
        assert len(entries) == 15
        assert entries[0]["msg"] == "flush-0"
        assert entries[14]["msg"] == "flush-14"
        assert all(e["mt"] == "info" for e in entries)

        logger.shutdown_async()

    def test_flush_returns_self(self, tmp_path: Path):
        """flush() returns self for method chaining."""
        log_file = tmp_path / "chain.log"
        logger = Logger()
        logger.init(str(log_file), size=10000, flush=60.0)

        result = logger.info("msg").flush()
        assert result is logger

        logger.shutdown_async()

    def test_flush_multiple_levels(self, tmp_path: Path):
        """flush() persists messages from different log levels."""
        log_file = tmp_path / "levels.log"
        logger = Logger()
        logger.init(str(log_file), size=10000, flush=60.0)

        logger.debug("d-msg")
        logger.info("i-msg")
        logger.warning("w-msg")
        logger.error("e-msg")
        logger.success("s-msg")
        logger.flush(timeout=5.0)

        entries = _parse_log(log_file)
        assert len(entries) == 5
        types = [e["mt"] for e in entries]
        assert "debug" in types
        assert "info" in types
        assert "warning" in types
        assert "error" in types
        assert "success" in types

        logger.shutdown_async()

    def test_flush_noop_without_async(self):
        """flush() on non-async logger is safe no-op."""
        logger = Logger()
        result = logger.flush()
        assert result is logger


# ============================================================================
# Async Adaptive - Real File I/O
# ============================================================================

class TestAsyncAdaptiveRealFile:
    """Logger.enable_adaptive() / disable_adaptive() with real file."""

    def test_adaptive_logs_to_file(self, tmp_path: Path):
        """Adaptive mode logs all messages correctly to disk."""
        log_file = tmp_path / "adaptive.log"
        logger = Logger()
        logger.init(str(log_file), size=100, flush=0.1)
        logger.enable_adaptive(min_batch=5, max_batch=500)

        for i in range(25):
            logger.info(f"adapt-{i}")

        logger.flush(timeout=5.0)

        entries = _parse_log(log_file)
        assert len(entries) == 25
        assert entries[0]["msg"] == "adapt-0"
        assert entries[24]["msg"] == "adapt-24"

        logger.disable_adaptive()
        logger.shutdown_async()

    def test_adaptive_enable_returns_self(self, tmp_path: Path):
        """enable_adaptive() returns self for chaining."""
        log_file = tmp_path / "chain.log"
        logger = Logger()
        logger.init(str(log_file), size=100, flush=0.1)

        result = logger.enable_adaptive()
        assert result is logger

        logger.shutdown_async()

    def test_adaptive_disable_returns_self(self, tmp_path: Path):
        """disable_adaptive() returns self for chaining."""
        log_file = tmp_path / "chain2.log"
        logger = Logger()
        logger.init(str(log_file), size=100, flush=0.1)

        logger.enable_adaptive()
        result = logger.disable_adaptive()
        assert result is logger

        logger.shutdown_async()

    def test_adaptive_then_static(self, tmp_path: Path):
        """Switch from adaptive to static — all messages persist."""
        log_file = tmp_path / "toggle.log"
        logger = Logger()
        logger.init(str(log_file), size=10000, flush=60.0)

        logger.enable_adaptive()
        for i in range(10):
            logger.info(f"a-{i}")
        logger.flush(timeout=5.0)

        logger.disable_adaptive()
        for i in range(10):
            logger.warning(f"s-{i}")
        logger.flush(timeout=5.0)

        entries = _parse_log(log_file)
        assert len(entries) == 20
        assert entries[0]["msg"] == "a-0"
        assert entries[0]["mt"] == "info"
        assert entries[10]["msg"] == "s-0"
        assert entries[10]["mt"] == "warning"

        logger.shutdown_async()

    def test_adaptive_noop_without_async(self):
        """enable/disable adaptive on non-async logger is safe no-op."""
        logger = Logger()
        result = logger.enable_adaptive()
        assert result is logger
        result = logger.disable_adaptive()
        assert result is logger


# ============================================================================
# Async Metrics with Real File
# ============================================================================

class TestAsyncMetricsRealFile:
    """Verify metrics reflect actual writes to disk."""

    def test_metrics_after_flush(self, tmp_path: Path):
        """Metrics track enqueued/written after flush."""
        log_file = tmp_path / "metrics.log"
        logger = Logger()
        logger.init(str(log_file), size=10000, flush=60.0)

        for i in range(10):
            logger.info(f"m-{i}")

        logger.flush(timeout=5.0)

        metrics = logger.get_async_metrics()
        assert metrics["enqueued"] >= 10
        assert metrics["written"] >= 10
        assert metrics["errors"] == 0

        entries = _parse_log(log_file)
        assert len(entries) == 10

        logger.shutdown_async()
