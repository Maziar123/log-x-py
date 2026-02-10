"""Tests for logxpy/src/_types.py -- Core types, enums, constants."""
from __future__ import annotations

import pytest
from dataclasses import FrozenInstanceError

from logxpy.src._types import (
    TS, TID, LVL, MT, AT, ST, DUR, MSG,
    TASK_UUID, TASK_LEVEL, TIMESTAMP, MESSAGE_TYPE,
    ACTION_TYPE, ACTION_STATUS, DURATION_NS,
    Level, LevelName, ActionStatusStr,
    TaskLevel, Record,
    get_level_name, get_level_value,
)


# ============================================================================
# Field Constants
# ============================================================================

class TestFieldConstants:
    def test_compact_field_names(self):
        assert TS == "ts"
        assert TID == "tid"
        assert LVL == "lvl"
        assert MT == "mt"
        assert AT == "at"
        assert ST == "st"
        assert DUR == "dur"
        assert MSG == "msg"

    def test_legacy_aliases_match_compact(self):
        assert TASK_UUID == TID
        assert TASK_LEVEL == LVL
        assert TIMESTAMP == TS
        assert MESSAGE_TYPE == MT
        assert ACTION_TYPE == AT
        assert ACTION_STATUS == ST
        assert DURATION_NS == DUR


# ============================================================================
# Level Enum
# ============================================================================

class TestLevel:
    def test_level_values(self):
        assert Level.DEBUG == 10
        assert Level.INFO == 20
        assert Level.SUCCESS == 25
        assert Level.NOTE == 26
        assert Level.WARNING == 30
        assert Level.ERROR == 40
        assert Level.CRITICAL == 50

    def test_level_ordering(self):
        assert Level.DEBUG < Level.INFO
        assert Level.INFO < Level.SUCCESS
        assert Level.SUCCESS < Level.NOTE
        assert Level.NOTE < Level.WARNING
        assert Level.WARNING < Level.ERROR
        assert Level.ERROR < Level.CRITICAL

    def test_level_is_intenum(self):
        assert isinstance(Level.DEBUG, int)

    def test_level_by_name(self):
        assert Level["DEBUG"] == Level.DEBUG
        assert Level["CRITICAL"] == Level.CRITICAL

    def test_level_by_value(self):
        assert Level(10) == Level.DEBUG
        assert Level(50) == Level.CRITICAL


class TestLevelName:
    def test_level_name_values(self):
        assert LevelName.DEBUG == "debug"
        assert LevelName.INFO == "info"
        assert LevelName.SUCCESS == "success"
        assert LevelName.NOTE == "note"
        assert LevelName.WARNING == "warning"
        assert LevelName.ERROR == "error"
        assert LevelName.CRITICAL == "critical"

    def test_level_name_is_strenum(self):
        assert isinstance(LevelName.DEBUG, str)


class TestActionStatusStr:
    def test_status_values(self):
        assert ActionStatusStr.STARTED == "started"
        assert ActionStatusStr.SUCCEEDED == "succeeded"
        assert ActionStatusStr.FAILED == "failed"

    def test_status_is_strenum(self):
        assert isinstance(ActionStatusStr.STARTED, str)


# ============================================================================
# TaskLevel
# ============================================================================

class TestTaskLevel:
    def test_init_empty(self):
        tl = TaskLevel()
        assert tl.as_list() == []

    def test_init_with_level(self):
        tl = TaskLevel([1, 2, 3])
        assert tl.as_list() == [1, 2, 3]

    def test_as_list_returns_copy(self):
        tl = TaskLevel([1, 2])
        result = tl.as_list()
        result.append(99)
        assert tl.as_list() == [1, 2]

    def test_level_property_returns_pvector(self):
        from pyrsistent import pvector
        tl = TaskLevel([1, 2])
        assert tl.level == pvector([1, 2])

    def test_from_string_root(self):
        tl = TaskLevel.from_string("/1")
        assert tl.as_list() == [1]

    def test_from_string_nested(self):
        tl = TaskLevel.from_string("/1/2/3")
        assert tl.as_list() == [1, 2, 3]

    def test_to_string(self):
        tl = TaskLevel([1, 2, 3])
        assert tl.to_string() == "/1/2/3"

    def test_roundtrip_from_string_to_string(self):
        for s in ("/1", "/1/2", "/1/2/3", "/5/10/15"):
            assert TaskLevel.from_string(s).to_string() == s

    def test_next_sibling(self):
        tl = TaskLevel([1, 2])
        assert tl.next_sibling().as_list() == [1, 3]

    def test_child(self):
        tl = TaskLevel([1, 2])
        assert tl.child().as_list() == [1, 2, 1]

    def test_parent(self):
        tl = TaskLevel([1, 2, 3])
        assert tl.parent().as_list() == [1, 2]

    def test_parent_of_empty(self):
        tl = TaskLevel([])
        assert tl.parent() is None

    def test_is_sibling_of_true(self):
        tl1 = TaskLevel([1, 2])
        tl2 = TaskLevel([1, 3])
        assert tl1.is_sibling_of(tl2)

    def test_is_sibling_of_false(self):
        tl1 = TaskLevel([1, 2])
        tl2 = TaskLevel([2, 3])
        assert not tl1.is_sibling_of(tl2)

    def test_comparison_operators(self):
        assert TaskLevel([1]) < TaskLevel([2])
        assert TaskLevel([1, 1]) <= TaskLevel([1, 1])
        assert TaskLevel([2]) > TaskLevel([1])
        assert TaskLevel([1, 1]) >= TaskLevel([1, 1])

    def test_equality(self):
        assert TaskLevel([1, 2]) == TaskLevel([1, 2])

    def test_inequality(self):
        assert TaskLevel([1, 2]) != TaskLevel([1, 3])

    def test_hash_equal_objects_same_hash(self):
        assert hash(TaskLevel([1, 2])) == hash(TaskLevel([1, 2]))

    def test_not_equal_to_non_tasklevel(self):
        assert TaskLevel([1]) != "not a task level"


# ============================================================================
# Record
# ============================================================================

class TestRecord:
    def test_record_creation(self):
        r = Record(
            timestamp=1.0,
            level=Level.INFO,
            message="hello",
            fields={"k": "v"},
            context={},
            task_uuid="Xa.1",
            task_level=(1,),
        )
        assert r.timestamp == 1.0
        assert r.level == Level.INFO
        assert r.message == "hello"
        assert r.task_uuid == "Xa.1"

    def test_record_is_frozen(self):
        r = Record(
            timestamp=1.0, level=Level.INFO, message="",
            fields={}, context={}, task_uuid="X.1", task_level=(1,),
        )
        with pytest.raises(FrozenInstanceError):
            r.timestamp = 2.0

    def test_record_to_dict_basic(self):
        r = Record(
            timestamp=1.0, level=Level.INFO, message="hi",
            fields={"x": 1}, context={"env": "test"},
            task_uuid="Xa.1", task_level=(1,),
            message_type="info",
        )
        d = r.to_dict()
        assert d["ts"] == 1.0
        assert d["tid"] == "Xa.1"
        assert d["mt"] == "info"
        assert d["msg"] == "hi"
        assert d["x"] == 1
        assert d["env"] == "test"

    def test_record_to_dict_without_action_type(self):
        r = Record(
            timestamp=1.0, level=Level.INFO, message="",
            fields={}, context={}, task_uuid="X.1", task_level=(1,),
        )
        d = r.to_dict()
        assert "at" not in d
        assert "st" not in d

    def test_record_to_dict_with_action_status(self):
        r = Record(
            timestamp=1.0, level=Level.INFO, message="",
            fields={}, context={}, task_uuid="X.1", task_level=(1,),
            action_type="test:action", action_status=ActionStatusStr.SUCCEEDED,
        )
        d = r.to_dict()
        assert d["at"] == "test:action"
        assert d["st"] == "succeeded"


# ============================================================================
# Type Helpers
# ============================================================================

class TestGetLevelName:
    def test_from_level_enum(self):
        assert get_level_name(Level.DEBUG) == "debug"
        assert get_level_name(Level.CRITICAL) == "critical"

    def test_from_string(self):
        assert get_level_name("WARNING") == "warning"
        assert get_level_name("debug") == "debug"

    def test_invalid_type_raises_typeerror(self):
        with pytest.raises(TypeError):
            get_level_name(123)


class TestGetLevelValue:
    def test_from_string(self):
        assert get_level_value("debug") == Level.DEBUG
        assert get_level_value("WARNING") == Level.WARNING

    def test_from_int(self):
        assert get_level_value(10) == Level.DEBUG

    def test_from_level_enum(self):
        assert get_level_value(Level.DEBUG) == Level.DEBUG

    def test_unknown_string_raises_valueerror(self):
        with pytest.raises(ValueError, match="Unknown level"):
            get_level_value("nonexistent")

    def test_invalid_type_raises_typeerror(self):
        with pytest.raises(TypeError):
            get_level_value([])
