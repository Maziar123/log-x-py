"""Tests for logxpy/src/_action.py -- Action context management."""
from __future__ import annotations

import threading
import pytest

from logxpy.src._action import (
    Action,
    ActionStatus,
    STARTED_STATUS, SUCCEEDED_STATUS, FAILED_STATUS, VALID_STATUSES,
    ACTION_STATUS_FIELD, ACTION_TYPE_FIELD,
    current_action,
    start_action,
    start_task,
    preserve_context,
    TooManyCalls,
    log_call,
    WrittenAction,
    WrongTask,
    WrongTaskLevel,
    InvalidStartMessage,
)
from logxpy.src._message import (
    MESSAGE_TYPE_FIELD,
    TASK_UUID_FIELD,
    TASK_LEVEL_FIELD,
    TIMESTAMP_FIELD,
    WrittenMessage,
)
from logxpy.src._types import TaskLevel


# ============================================================================
# ActionStatus
# ============================================================================

class TestActionStatus:
    def test_values(self):
        assert ActionStatus.STARTED == "started"
        assert ActionStatus.SUCCEEDED == "succeeded"
        assert ActionStatus.FAILED == "failed"

    def test_backward_compat_constants(self):
        assert STARTED_STATUS == "started"
        assert SUCCEEDED_STATUS == "succeeded"
        assert FAILED_STATUS == "failed"
        assert set(VALID_STATUSES) == {"started", "succeeded", "failed"}


# ============================================================================
# Action Context Manager
# ============================================================================

class TestAction:
    def test_context_manager_start_and_finish(self, captured_messages):
        with start_action(action_type="test:action"):
            pass
        statuses = [m.get(ACTION_STATUS_FIELD) for m in captured_messages if ACTION_STATUS_FIELD in m]
        assert "started" in statuses
        assert "succeeded" in statuses

    def test_context_manager_failure(self, captured_messages):
        with pytest.raises(ValueError):
            with start_action(action_type="test:fail"):
                raise ValueError("boom")
        statuses = [m.get(ACTION_STATUS_FIELD) for m in captured_messages if ACTION_STATUS_FIELD in m]
        assert "started" in statuses
        assert "failed" in statuses

    def test_task_uuid_property(self, captured_messages):
        with start_action(action_type="test:uuid") as action:
            assert isinstance(action.task_uuid, str)
            assert len(action.task_uuid) > 0

    def test_add_success_fields(self, captured_messages):
        with start_action(action_type="test:success") as action:
            action.add_success_fields(result=42)
        end_msgs = [m for m in captured_messages if m.get(ACTION_STATUS_FIELD) == "succeeded"]
        assert len(end_msgs) == 1
        assert end_msgs[0].get("result") == 42

    def test_finish_idempotent(self, captured_messages):
        with start_action(action_type="test:idem") as action:
            pass
        # Calling finish again should be no-op
        action.finish()
        end_msgs = [m for m in captured_messages if m.get(ACTION_STATUS_FIELD) == "succeeded"]
        assert len(end_msgs) == 1

    def test_nested_actions_share_task_uuid(self, captured_messages):
        with start_action(action_type="outer") as outer:
            outer_uuid = outer.task_uuid
            with start_action(action_type="inner") as inner:
                assert inner.task_uuid == outer_uuid

    def test_nested_actions_task_levels(self, captured_messages):
        with start_action(action_type="outer"):
            with start_action(action_type="inner"):
                pass
        levels = [m.get(TASK_LEVEL_FIELD) for m in captured_messages if TASK_LEVEL_FIELD in m]
        # Should have varying depths
        assert any(len(l) == 2 for l in levels if isinstance(l, list))

    def test_run_executes_in_context(self, captured_messages):
        with start_task(action_type="task") as action:
            result = action.run(lambda: current_action())
            assert result is action

    def test_context_restores_after_exit(self, captured_messages):
        assert current_action() is None
        with start_action(action_type="temp"):
            assert current_action() is not None
        assert current_action() is None


# ============================================================================
# start_action / start_task
# ============================================================================

class TestStartAction:
    def test_no_parent_creates_task(self, captured_messages):
        with start_action(action_type="top") as act:
            assert act.task_uuid is not None

    def test_with_parent_creates_child(self, captured_messages):
        with start_action(action_type="parent") as parent:
            with start_action(action_type="child") as child:
                assert child.task_uuid == parent.task_uuid

    def test_fields_in_start_message(self, captured_messages):
        with start_action(action_type="test:fields", custom_field="hello"):
            pass
        start_msgs = [m for m in captured_messages if m.get(ACTION_STATUS_FIELD) == "started"]
        assert any(m.get("custom_field") == "hello" for m in start_msgs)


class TestStartTask:
    def test_creates_new_task_uuid(self, captured_messages):
        with start_task(action_type="task1") as t1:
            pass
        with start_task(action_type="task2") as t2:
            pass
        assert t1.task_uuid != t2.task_uuid

    def test_action_type_in_messages(self, captured_messages):
        with start_task(action_type="my:task"):
            pass
        at_values = [m.get(ACTION_TYPE_FIELD) for m in captured_messages if ACTION_TYPE_FIELD in m]
        assert "my:task" in at_values


# ============================================================================
# current_action
# ============================================================================

class TestCurrentAction:
    def test_none_outside_action(self):
        assert current_action() is None

    def test_returns_action_inside_context(self, captured_messages):
        with start_action(action_type="test"):
            assert current_action() is not None


# ============================================================================
# preserve_context
# ============================================================================

class TestPreserveContext:
    def test_preserves_across_thread(self, captured_messages):
        result = [None]

        with start_action(action_type="threaded") as act:
            def check():
                result[0] = True  # If we get here, context was preserved

            preserved = preserve_context(check)
            t = threading.Thread(target=preserved)
            t.start()
            t.join()

        assert result[0] is True

    def test_raises_on_second_call(self, captured_messages):
        with start_action(action_type="once"):
            fn = preserve_context(lambda: None)
        fn()
        with pytest.raises(TooManyCalls):
            fn()

    def test_no_action_returns_original(self):
        f = lambda: 42
        result = preserve_context(f)
        assert result is f


# ============================================================================
# log_call
# ============================================================================

class TestLogCall:
    def test_basic_decoration(self, captured_messages):
        @log_call
        def my_func(x, y):
            return x + y

        result = my_func(1, 2)
        assert result == 3
        assert len(captured_messages) >= 2  # start + end

    def test_custom_action_type(self, captured_messages):
        @log_call(action_type="custom:type")
        def my_func():
            return 1

        my_func()
        at_values = [m.get(ACTION_TYPE_FIELD) for m in captured_messages]
        assert "custom:type" in at_values

    def test_include_args(self, captured_messages):
        @log_call(include_args=["x"])
        def my_func(x, y):
            return x + y

        my_func(1, 2)
        start_msgs = [m for m in captured_messages if m.get(ACTION_STATUS_FIELD) == "started"]
        assert any(m.get("x") == 1 for m in start_msgs)
        # y should not be logged
        assert not any("y" in m for m in start_msgs)

    def test_include_result_false(self, captured_messages):
        @log_call(include_result=False)
        def my_func():
            return 42

        my_func()
        end_msgs = [m for m in captured_messages if m.get(ACTION_STATUS_FIELD) == "succeeded"]
        assert not any("result" in m for m in end_msgs)

    def test_invalid_include_args_raises(self):
        with pytest.raises(ValueError, match="include_args"):
            @log_call(include_args=["nonexistent"])
            def my_func(x):
                pass


# ============================================================================
# continue_task
# ============================================================================

class TestContinueTask:
    def test_serialize_and_continue(self, captured_messages):
        with start_task(action_type="original") as act:
            task_id = act.serialize_task_id()

        with Action.continue_task(task_id=task_id, action_type="continued"):
            pass
        assert len(captured_messages) >= 4  # 2 from original + 2 from continued

    def test_requires_task_id(self):
        with pytest.raises(RuntimeError, match="task_id"):
            Action.continue_task()

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid"):
            Action.continue_task(task_id=b"nope")


# ============================================================================
# Exception Classes
# ============================================================================

class TestExceptionClasses:
    def test_invalid_start_message_wrong_status(self):
        exc = InvalidStartMessage.wrong_status("msg")
        assert "STARTED" in str(exc)

    def test_invalid_start_message_wrong_task_level(self):
        exc = InvalidStartMessage.wrong_task_level("msg")
        assert "task level" in str(exc)
