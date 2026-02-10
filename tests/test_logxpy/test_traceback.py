"""Tests for logxpy/src/_traceback.py -- Traceback logging."""
from __future__ import annotations

import sys
import warnings

from logxpy.src._output import MemoryLogger
from logxpy.src._traceback import TRACEBACK_MESSAGE, write_traceback


class TestWriteTraceback:
    """Test write_traceback using MemoryLogger to avoid recursion.

    The standard Logger.write calls write_traceback on serialization
    failure, which can cause infinite recursion.  MemoryLogger stores
    messages without that retry loop, making it safe for testing.

    Note: MemoryLogger stores raw (unserialized) values, so the
    ``reason`` field holds the actual Exception object and
    ``exception`` holds the exception class.
    """

    def test_writes_traceback_message(self, fresh_destinations):
        logger = MemoryLogger()
        try:
            raise ValueError("test error")
        except ValueError:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                write_traceback(logger)
        assert len(logger.messages) >= 1
        tb_msg = logger.messages[-1]
        # reason is the raw exception object in MemoryLogger
        assert str(tb_msg["reason"]) == "test error"

    def test_exception_type_recorded(self, fresh_destinations):
        logger = MemoryLogger()
        try:
            raise RuntimeError("runtime problem")
        except RuntimeError:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                write_traceback(logger)
        assert len(logger.messages) >= 1
        tb_msg = logger.messages[-1]
        # exception is the raw class object in MemoryLogger
        exc_value = tb_msg.get("exc", tb_msg.get("exception", ""))
        assert exc_value is RuntimeError or "RuntimeError" in str(exc_value)

    def test_exc_info_parameter(self, fresh_destinations):
        logger = MemoryLogger()
        try:
            raise RuntimeError("explicit")
        except RuntimeError:
            exc_info = sys.exc_info()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            write_traceback(logger, exc_info=exc_info)
        assert len(logger.messages) >= 1
        tb_msg = logger.messages[-1]
        exc_value = tb_msg.get("exc", tb_msg.get("exception", ""))
        assert exc_value is RuntimeError or "RuntimeError" in str(exc_value)

    def test_traceback_contains_trace_text(self, fresh_destinations):
        logger = MemoryLogger()
        try:
            raise ValueError("with trace")
        except ValueError:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                write_traceback(logger)
        assert len(logger.messages) >= 1
        tb_msg = logger.messages[-1]
        tb_text = tb_msg.get("traceback", "")
        assert "ValueError" in tb_text or "Traceback" in tb_text

    def test_traceback_message_stored(self, fresh_destinations):
        """MemoryLogger tracks traceback messages separately."""
        logger = MemoryLogger()
        try:
            raise ValueError("tracked")
        except ValueError:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                write_traceback(logger)
        assert len(logger.tracebackMessages) >= 1

    def test_flush_tracebacks(self, fresh_destinations):
        """MemoryLogger.flushTracebacks clears expected tracebacks."""
        logger = MemoryLogger()
        try:
            raise ValueError("flushable")
        except ValueError:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                write_traceback(logger)
        flushed = logger.flushTracebacks(ValueError)
        assert len(flushed) >= 1
        assert len(logger.tracebackMessages) == 0

    def test_reason_is_exception_instance(self, fresh_destinations):
        """The raw reason field holds the actual exception instance."""
        logger = MemoryLogger()
        try:
            raise TypeError("type problem")
        except TypeError:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                write_traceback(logger)
        tb_msg = logger.messages[-1]
        assert isinstance(tb_msg["reason"], TypeError)


class TestTracebackMessage:
    def test_message_type(self):
        assert TRACEBACK_MESSAGE.message_type == "eliot:traceback"

    def test_has_serializer(self):
        assert TRACEBACK_MESSAGE._serializer is not None

    def test_allows_additional_fields(self):
        """Traceback serializer allows additional fields for exception extraction."""
        assert TRACEBACK_MESSAGE._serializer.allow_additional_fields is True
