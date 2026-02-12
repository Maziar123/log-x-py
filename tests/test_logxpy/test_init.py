"""Tests for logxpy/src/__init__.py -- Public API exports."""
from __future__ import annotations
import warnings

class TestPublicAPI:
    def test_core_imports(self):
        from logxpy.src import (
            Message, Action, start_action, startTask, current_action,
            preserve_context, log, to_file, write_traceback,
        )
        # Verify all are callable or classes
        assert callable(start_action)
        assert callable(current_action)

    def test_level_imports(self):
        from logxpy.src import Level, LevelName, ActionStatusStr
        assert Level.DEBUG == 10
        assert LevelName.INFO == "info"
        assert ActionStatusStr.STARTED == "started"

    def test_compact_field_imports(self):
        from logxpy.src import TS, TID, LVL, MT, AT, ST, DUR, MSG
        assert TS == "ts"
        assert TID == "tid"

    def test_sqid_imports(self):
        from logxpy.src import SqidGenerator, sqid, child_sqid, generate_task_id
        assert callable(sqid)

    def test_async_imports(self):
        from logxpy.src import (
            QueuePolicy, AsyncWriter, Mode, WriterType,
            BaseFileWriterThread, create_writer, Q,
        )
        assert QueuePolicy.BLOCK == "block"
        assert Mode.TRIGGER == "trigger"
        assert WriterType.BLOCK == "block"

    def test_validation_imports(self):
        from logxpy.src import Field, fields, MessageType, ActionType, ValidationError
        assert callable(fields)

    def test_all_names_importable(self):
        import logxpy.src as mod
        for name in mod.__all__:
            if name.startswith("_"):
                continue
            assert hasattr(mod, name), f"{name} not found in logxpy.src"

class TestBackwardCompatAliases:
    def test_add_destination_deprecated(self, fresh_destinations):
        from logxpy.src import add_destination
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            add_destination(lambda m: None)
            assert any("deprecated" in str(warning.message).lower() for warning in w)

    def test_use_asyncio_deprecated(self):
        from logxpy.src import use_asyncio_context
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            use_asyncio_context()
            assert any(issubclass(warning.category, DeprecationWarning) for warning in w)

    def test_pep8_aliases_exist(self):
        from logxpy.src import (
            start_action, start_task, write_traceback, write_failure,
            add_destinations, remove_destination, add_global_fields,
        )
        assert callable(start_action)
        assert callable(start_task)

class TestLazyExports:
    def test_truncate(self):
        from logxpy.src import truncate
        assert callable(truncate)

    def test_memoize(self):
        from logxpy.src import memoize
        assert callable(memoize)

    def test_cache_stats(self):
        from logxpy.src import CacheStats
        stats = CacheStats()
        assert stats.hits == 0

    def test_invalid_attr_raises(self):
        import pytest
        import logxpy.src as mod
        with pytest.raises(AttributeError):
            mod.nonexistent_attribute_xyz
