"""Tests for eliot.decorators."""
from unittest import TestCase
import asyncio
from logxpy.decorators import logged, timed, retry
from logxpy._async import _emit_handlers

class DecoratorTests(TestCase):
    def setUp(self):
        self.records = []
        _emit_handlers.append(self.records.append)
    
    def tearDown(self):
        _emit_handlers.remove(self.records.append)

    def test_logged_sync(self):
        """@logged works on sync functions."""
        @logged
        def func(x): return x + 1
        
        func(1)
        self.assertEqual(len(self.records), 2) # start, end
        self.assertEqual(self.records[0].fields["x"], 1)
        self.assertEqual(self.records[1].fields["result"], 2)

    def test_logged_async(self):
        """@logged works on async functions."""
        @logged
        async def func(x): return x + 1
        
        asyncio.run(func(1))
        self.assertEqual(len(self.records), 2)
        self.assertEqual(self.records[1].fields["result"], 2)

    def test_timed(self):
        """@timed emits metric."""
        @timed("my_metric")
        def func(): pass
        
        func()
        self.assertEqual(self.records[0].fields["metric"], "my_metric")
        self.assertIn("duration_ms", self.records[0].fields)

    def test_retry(self):
        """@retry retries on failure."""
        count = 0
        @retry(attempts=2, delay=0)
        def func():
            nonlocal count
            count += 1
            if count < 2: raise ValueError("fail")
            return "ok"
            
        self.assertEqual(func(), "ok")
        self.assertEqual(count, 2)
