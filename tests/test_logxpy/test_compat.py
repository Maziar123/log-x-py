"""Tests for logxpy/src/_compat.py -- Backward compatibility."""
from __future__ import annotations
import warnings

class TestBackwardCompatibility:
    def test_start_action_alias(self):
        from logxpy.src._compat import startAction, start_action
        assert startAction is start_action

    def test_write_traceback_alias(self):
        from logxpy.src._compat import writeTraceback, write_traceback
        assert writeTraceback is write_traceback

    def test_add_destination_deprecated(self, fresh_destinations):
        from logxpy.src._compat import add_destination
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            add_destination(lambda msg: None)
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)

    def test_use_asyncio_context_deprecated(self):
        from logxpy.src._compat import use_asyncio_context
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            use_asyncio_context()
            assert len(w) == 1

    def test_log_call_deprecated(self, captured_messages):
        from logxpy.src._compat import log_call
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            @log_call
            def my_func():
                return 42
            result = my_func()
            assert result == 42
            assert any("deprecated" in str(warning.message).lower() for warning in w)

    def test_log_message_deprecated(self, captured_messages):
        from logxpy.src._compat import log_message
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            log_message(message_type="test:compat")
            assert any("deprecated" in str(warning.message).lower() for warning in w)
