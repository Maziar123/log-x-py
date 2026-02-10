"""Shared fixtures for logxpy core library tests."""
from __future__ import annotations

import pytest

from logxpy.src._output import Logger, MemoryLogger, Destinations, to_file
from logxpy.src._async import _emit_handlers
from logxpy.src._types import Level, Record
from logxpy.src.logx import Logger as LogxLogger, set_global_masker


@pytest.fixture(autouse=True)
def _reset_global_state():
    """Reset global state between tests to prevent leakage.

    NOTE: Does NOT touch Logger._destinations -- that is handled
    exclusively by the ``fresh_destinations`` fixture to avoid
    double-save/restore conflicts.
    """
    # Reset masker
    set_global_masker(None)

    # Clear emit handlers
    original_handlers = _emit_handlers[:]
    _emit_handlers.clear()

    yield

    # Restore
    _emit_handlers.clear()
    _emit_handlers.extend(original_handlers)
    set_global_masker(None)


@pytest.fixture
def fresh_destinations():
    """Provide isolated Destinations instance for tests."""
    original = Logger._destinations
    Logger._destinations = Destinations()
    yield Logger._destinations
    Logger._destinations = original


@pytest.fixture
def memory_logger():
    """Provide a fresh MemoryLogger instance."""
    return MemoryLogger()


@pytest.fixture
def captured_messages(fresh_destinations):
    """Add a capturing callable as sole destination; return messages list."""
    messages: list[dict] = []
    fresh_destinations.add(lambda msg: messages.append(msg.copy()))
    return messages


@pytest.fixture
def log_file(tmp_path, fresh_destinations):
    """Create temp log file wired as destination; yield path."""
    log_path = tmp_path / "test.log"
    f = open(log_path, "w", encoding="utf-8")
    to_file(f)
    yield log_path
    f.close()


@pytest.fixture
def fresh_logger():
    """New LogxLogger instance (not the global singleton)."""
    return LogxLogger("test")


@pytest.fixture
def sample_record():
    """Known Record instance for assertions."""
    return Record(
        timestamp=1700000000.0,
        level=Level.INFO,
        message="test message",
        fields={"key": "value"},
        context={"ctx_key": "ctx_value"},
        task_uuid="Xa.1",
        task_level=(1,),
        message_type="info",
    )
