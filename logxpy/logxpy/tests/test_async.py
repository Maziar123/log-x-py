"""Tests for eliot._async."""
from unittest import TestCase
import asyncio
from logxpy._async import action, aaction, scope, _emit_handlers

class AsyncActionTests(TestCase):
    def test_sync_action(self):
        """Sync action context manager works."""
        records = []
        def handler(r): records.append(r)
        _emit_handlers.append(handler)
        self.addCleanup(_emit_handlers.remove, handler)
        
        with action("test_action", x=1):
            pass
            
        self.assertEqual(len(records), 2)
        start, end = records
        self.assertEqual(start.action_status, "started")
        self.assertEqual(end.action_status, "succeeded")
        self.assertEqual(start.task_uuid, end.task_uuid)

    def test_async_action(self):
        """Async action context manager works."""
        records = []
        def handler(r): records.append(r)
        _emit_handlers.append(handler)
        self.addCleanup(_emit_handlers.remove, handler)
        
        async def run():
            async with aaction("test_async", y=2):
                pass
        
        asyncio.run(run())
        
        self.assertEqual(len(records), 2)
        start, end = records
        self.assertEqual(start.action_type, "test_async")
        self.assertEqual(end.action_status, "succeeded")

    def test_scope(self):
        """Scope context manager merges context."""
        records = []
        def handler(r): records.append(r)
        _emit_handlers.append(handler)
        self.addCleanup(_emit_handlers.remove, handler)
        
        with scope(a=1):
            with action("scoped"):
                pass
                
        self.assertEqual(records[0].context.get("a"), 1)

    def test_async_scope(self):
        """Scope works in async context."""
        records = []
        def handler(r): records.append(r)
        _emit_handlers.append(handler)
        self.addCleanup(_emit_handlers.remove, handler)
        
        async def run():
            with scope(b=2):
                async with aaction("async_scoped"):
                    pass
        
        asyncio.run(run())
        self.assertEqual(records[0].context.get("b"), 2)
