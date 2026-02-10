"""Tests for logxpy/src/logx.py -- Main Logger fluent API."""
from __future__ import annotations

import datetime as _dt
import json
from enum import Enum
from io import BytesIO, StringIO
from pathlib import Path

import pytest

from logxpy.src._types import Level
from logxpy.src.logx import Logger, log, set_global_masker, get_global_masker


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
# Async
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
