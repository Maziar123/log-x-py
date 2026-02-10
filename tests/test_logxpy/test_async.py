"""Tests for logxpy/src/_async.py -- Async action and scope."""
from __future__ import annotations

import asyncio
import pytest

from logxpy.src._async import (
    AsyncAction,
    action,
    aaction,
    scope,
    current_scope,
    _emit,
    register_emitter,
)
from logxpy.src._types import Level, Record


# ============================================================================
# AsyncAction
# ============================================================================

class TestAsyncAction:
    def test_sync_context_manager(self, captured_messages):
        act = AsyncAction("test:sync", "X.1", (1,))
        with act:
            pass
        statuses = [m.get("st") for m in captured_messages if "st" in m]
        assert "started" in statuses
        assert "succeeded" in statuses

    def test_async_context_manager(self, captured_messages):
        async def run():
            act = AsyncAction("test:async", "X.1", (1,))
            async with act:
                pass

        asyncio.run(run())
        statuses = [m.get("st") for m in captured_messages if "st" in m]
        assert "started" in statuses
        assert "succeeded" in statuses

    def test_failure_records_exception(self, captured_messages):
        with pytest.raises(ValueError):
            with AsyncAction("test:fail", "X.1", (1,)):
                raise ValueError("boom")
        end_msgs = [m for m in captured_messages if m.get("st") == "failed"]
        assert len(end_msgs) == 1
        assert "ValueError" in end_msgs[0].get("exception", "")
        assert end_msgs[0].get("reason") == "boom"

    def test_child_level(self):
        act = AsyncAction("test", "X.1", (1,))
        child1 = act.child_level()
        child2 = act.child_level()
        assert child1 == (1, 1)
        assert child2 == (1, 2)

    def test_fields_in_records(self, captured_messages):
        with AsyncAction("test:fields", "X.1", (1,), custom="value"):
            pass
        start_msgs = [m for m in captured_messages if m.get("st") == "started"]
        assert any(m.get("custom") == "value" for m in start_msgs)


# ============================================================================
# action (sync context manager)
# ============================================================================

class TestActionFunc:
    def test_action_creates_start_end(self, captured_messages):
        with action("test:func"):
            pass
        statuses = [m.get("st") for m in captured_messages if "st" in m]
        assert "started" in statuses
        assert "succeeded" in statuses

    def test_action_level_from_string(self, captured_messages):
        with action("test:level", level="WARNING"):
            pass
        # Should not raise - level string converted to Level enum
        assert len(captured_messages) >= 2


# ============================================================================
# aaction (async context manager)
# ============================================================================

class TestAaction:
    def test_aaction_creates_start_end(self, captured_messages):
        async def run():
            async with aaction("test:async"):
                pass

        asyncio.run(run())
        statuses = [m.get("st") for m in captured_messages if "st" in m]
        assert "started" in statuses
        assert "succeeded" in statuses

    def test_aaction_nesting(self, captured_messages):
        async def run():
            async with aaction("outer") as outer_act:
                outer_uuid = outer_act.task_uuid
                async with aaction("inner") as inner_act:
                    assert inner_act.task_uuid == outer_uuid

        asyncio.run(run())


# ============================================================================
# scope
# ============================================================================

class TestScope:
    def test_scope_adds_context(self):
        with scope(user=1):
            assert current_scope()["user"] == 1

    def test_scope_nests(self):
        with scope(a=1):
            with scope(b=2):
                s = current_scope()
                assert s["a"] == 1
                assert s["b"] == 2

    def test_scope_restores(self):
        original = current_scope().copy()
        with scope(temp=True):
            pass
        assert current_scope() == original

    def test_scope_inner_overrides(self):
        with scope(x=1):
            with scope(x=2):
                assert current_scope()["x"] == 2
            assert current_scope()["x"] == 1


# ============================================================================
# _emit
# ============================================================================

class TestEmit:
    def test_emit_sends_to_destinations(self, captured_messages):
        record = Record(
            timestamp=1.0, level=Level.INFO, message="test",
            fields={}, context={}, task_uuid="X.1", task_level=(1,),
            message_type="info",
        )
        _emit(record)
        assert len(captured_messages) >= 1

    def test_emit_calls_handlers(self, captured_messages):
        received = []
        register_emitter(lambda r: received.append(r))
        record = Record(
            timestamp=1.0, level=Level.INFO, message="handler test",
            fields={}, context={}, task_uuid="X.1", task_level=(1,),
            message_type="info",
        )
        _emit(record)
        assert len(received) == 1
