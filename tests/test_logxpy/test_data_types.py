"""Tests for logxpy/src/data_types.py -- Data type logging functions."""
from __future__ import annotations
import datetime
from decimal import Decimal
from enum import Enum
from logxpy.src.data_types import (
    send_color, send_currency, send_datetime, send_datetime_if,
    send_enum, send_set, send_pointer, send_variant,
    send_if, send_assigned, send_fmt_msg,
)

class TestSendColor:
    def test_rgb_tuple(self, captured_messages):
        send_color((255, 0, 0))
        assert len(captured_messages) >= 1

    def test_hex_string(self, captured_messages):
        send_color("#ff0000")
        assert len(captured_messages) >= 1

    def test_int_color(self, captured_messages):
        send_color(0xFF0000)
        assert len(captured_messages) >= 1

    def test_named_color(self, captured_messages):
        send_color("red")
        assert len(captured_messages) >= 1

class TestSendCurrency:
    def test_decimal(self, captured_messages):
        send_currency(Decimal("19.99"), "USD")
        assert len(captured_messages) >= 1

    def test_float(self, captured_messages):
        send_currency(19.99, "EUR")
        assert len(captured_messages) >= 1

    def test_string(self, captured_messages):
        send_currency("19.99", "GBP")
        assert len(captured_messages) >= 1

class TestSendDatetime:
    def test_datetime_object(self, captured_messages):
        dt = datetime.datetime(2024, 1, 15, 12, 0, 0)
        send_datetime(dt)
        assert len(captured_messages) >= 1

    def test_none_uses_now(self, captured_messages):
        send_datetime()
        assert len(captured_messages) >= 1

    def test_timestamp(self, captured_messages):
        send_datetime(1700000000.0)
        assert len(captured_messages) >= 1

class TestSendDatetimeIf:
    def test_true_condition(self, captured_messages):
        send_datetime_if(True)
        assert len(captured_messages) >= 1

    def test_false_condition(self, captured_messages):
        send_datetime_if(False)
        assert len(captured_messages) == 0

class TestSendEnum:
    def test_enum_value(self, captured_messages):
        class Color(Enum):
            RED = 1
        send_enum(Color.RED)
        assert len(captured_messages) >= 1

class TestSendSet:
    def test_set(self, captured_messages):
        send_set({1, 2, 3})
        assert len(captured_messages) >= 1

    def test_frozenset(self, captured_messages):
        send_set(frozenset([1, 2, 3]))
        assert len(captured_messages) >= 1

class TestSendPointer:
    def test_pointer(self, captured_messages):
        obj = object()
        send_pointer(obj)
        assert len(captured_messages) >= 1

class TestSendVariant:
    def test_int(self, captured_messages):
        send_variant(42)
        assert len(captured_messages) >= 1

    def test_string(self, captured_messages):
        send_variant("hello")
        assert len(captured_messages) >= 1

    def test_dict(self, captured_messages):
        send_variant({"key": "value"})
        assert len(captured_messages) >= 1

    def test_none(self, captured_messages):
        send_variant(None)
        assert len(captured_messages) >= 1

class TestSendIf:
    def test_true_sends(self, captured_messages):
        send_if(True, "test", key="value")
        assert len(captured_messages) >= 1

    def test_false_skips(self, captured_messages):
        send_if(False, "test", key="value")
        assert len(captured_messages) == 0

class TestSendAssigned:
    def test_not_none_sends(self, captured_messages):
        result = send_assigned(42)
        assert result is True
        assert len(captured_messages) >= 1

    def test_none_skips(self, captured_messages):
        result = send_assigned(None)
        assert result is False
        assert len(captured_messages) == 0

class TestSendFmtMsg:
    def test_format_string(self, captured_messages):
        send_fmt_msg("Hello {}", "world")
        assert len(captured_messages) >= 1
