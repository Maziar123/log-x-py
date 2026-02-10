"""Tests for logxpy/src/_message.py -- Message logging."""
from __future__ import annotations

import warnings
import pytest

from logxpy.src._message import (
    MESSAGE_TYPE_FIELD,
    TASK_UUID_FIELD,
    TASK_LEVEL_FIELD,
    TIMESTAMP_FIELD,
    EXCEPTION_FIELD,
    REASON_FIELD,
    Message,
    WrittenMessage,
    merge_messages,
    extract_fields,
    log_message,
)


# ============================================================================
# Field Constants
# ============================================================================

class TestFieldConstants:
    def test_message_type_field(self):
        assert MESSAGE_TYPE_FIELD == "mt"

    def test_task_uuid_field(self):
        assert TASK_UUID_FIELD == "tid"

    def test_task_level_field(self):
        assert TASK_LEVEL_FIELD == "lvl"

    def test_timestamp_field(self):
        assert TIMESTAMP_FIELD == "ts"

    def test_exception_field(self):
        assert EXCEPTION_FIELD == "exc"

    def test_reason_field(self):
        assert REASON_FIELD == "reason"


# ============================================================================
# Message
# ============================================================================

class TestMessage:
    def test_init(self):
        msg = Message({"key": "val"})
        assert msg.contents()["key"] == "val"

    def test_contents_returns_copy(self):
        msg = Message({"key": "val"})
        c = msg.contents()
        c["key"] = "modified"
        assert msg.contents()["key"] == "val"

    def test_bind_returns_new_message(self):
        msg = Message({"a": 1})
        msg2 = msg.bind(b=2)
        assert msg2 is not msg
        assert msg2.contents()["b"] == 2
        assert "b" not in msg.contents()

    def test_bind_merges_fields(self):
        msg = Message({"a": 1}).bind(b=2).bind(c=3)
        c = msg.contents()
        assert c["a"] == 1
        assert c["b"] == 2
        assert c["c"] == 3

    def test_bind_overrides_existing(self):
        msg = Message({"a": 1}).bind(a=2)
        assert msg.contents()["a"] == 2

    def test_write_with_memory_logger(self, captured_messages):
        msg = Message({"info": "test"})
        msg.write()
        assert len(captured_messages) >= 1

    def test_write_includes_timestamp(self, captured_messages):
        msg = Message({"info": "test"})
        msg.write()
        last = captured_messages[-1]
        assert TIMESTAMP_FIELD in last

    def test_write_includes_task_fields(self, captured_messages):
        msg = Message({"info": "test"})
        msg.write()
        last = captured_messages[-1]
        assert TASK_UUID_FIELD in last
        assert TASK_LEVEL_FIELD in last

    def test_log_classmethod_warns_deprecated(self, captured_messages):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            Message.log(info="x")
            assert any(issubclass(x.category, DeprecationWarning) for x in w)

    def test_new_classmethod_warns_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            Message.new(info="x")
            assert any(issubclass(x.category, DeprecationWarning) for x in w)


# ============================================================================
# WrittenMessage
# ============================================================================

class TestWrittenMessage:
    def _make_written(self, **extra):
        d = {
            TIMESTAMP_FIELD: 1700000000.0,
            TASK_UUID_FIELD: "Xa.1",
            TASK_LEVEL_FIELD: [1, 2],
            MESSAGE_TYPE_FIELD: "info",
            **extra,
        }
        return WrittenMessage.from_dict(d)

    def test_from_dict(self):
        wm = self._make_written()
        assert wm is not None

    def test_timestamp_property(self):
        wm = self._make_written()
        assert wm.timestamp == 1700000000.0

    def test_task_uuid_property(self):
        wm = self._make_written()
        assert wm.task_uuid == "Xa.1"

    def test_task_level_property(self):
        wm = self._make_written()
        tl = wm.task_level
        assert tl.as_list() == [1, 2]

    def test_contents_strips_metadata(self):
        wm = self._make_written(custom="value")
        contents = wm.contents
        assert TIMESTAMP_FIELD not in contents
        assert TASK_UUID_FIELD not in contents
        assert TASK_LEVEL_FIELD not in contents
        assert contents["custom"] == "value"

    def test_as_dict_returns_full(self):
        wm = self._make_written(custom="value")
        d = wm.as_dict()
        assert TIMESTAMP_FIELD in d
        assert d["custom"] == "value"

    def test_with_fields_returns_new(self):
        wm = self._make_written()
        wm2 = wm.with_fields(extra="new")
        assert wm2 is not wm
        assert wm2.as_dict()["extra"] == "new"


# ============================================================================
# Merge / Extract
# ============================================================================

class TestMergeMessages:
    def test_merge_two_messages(self):
        m1 = Message({"a": 1})
        m2 = Message({"b": 2})
        merged = merge_messages(m1, m2)
        c = merged.contents()
        assert c["a"] == 1
        assert c["b"] == 2

    def test_merge_later_overrides(self):
        m1 = Message({"a": 1})
        m2 = Message({"a": 2})
        merged = merge_messages(m1, m2)
        assert merged.contents()["a"] == 2


class TestExtractFields:
    def test_extract_from_message(self):
        msg = Message({"a": 1, "b": 2, "c": 3})
        result = extract_fields(msg, "a", "c")
        assert result == {"a": 1, "c": 3}


# ============================================================================
# log_message
# ============================================================================

class TestLogMessage:
    def test_creates_action_if_none(self, captured_messages):
        log_message("test:event", data="hello")
        assert len(captured_messages) >= 1
        last = captured_messages[-1]
        assert last[MESSAGE_TYPE_FIELD] == "test:event"
        assert TASK_UUID_FIELD in last

    def test_uses_current_action(self, captured_messages):
        from logxpy.src._action import start_action
        with start_action(action_type="parent"):
            log_message("child:msg", info="inside")
        # Should have start, child msg, and end
        assert len(captured_messages) >= 3
        child_msg = [m for m in captured_messages if m.get(MESSAGE_TYPE_FIELD) == "child:msg"]
        assert len(child_msg) == 1
