"""Tests for eliot.loggerx."""
from unittest import TestCase
from logxpy.loggerx import Logger, log
from logxpy._async import _emit_handlers
from logxpy._types import Level

class LoggerTests(TestCase):
    def setUp(self):
        self.records = []
        _emit_handlers.append(self.records.append)
    
    def tearDown(self):
        _emit_handlers.remove(self.records.append)

    def test_levels(self):
        """Logger methods emit correct levels."""
        log.info("info msg")
        log.error("error msg")
        
        self.assertEqual(len(self.records), 2)
        self.assertEqual(self.records[0].level, Level.INFO)
        self.assertEqual(self.records[1].level, Level.ERROR)

    def test_fluent(self):
        """Logger methods return self."""
        l = Logger()
        self.assertIs(l.info("msg"), l)

    def test_context(self):
        """Logger respects scope."""
        with log.scope(ctx=1):
            log.info("msg")
            
        self.assertEqual(self.records[0].context["ctx"], 1)

    def test_types(self):
        """Type methods format data."""
        log.json({"a": 1})
        self.assertIn('"a": 1', self.records[0].fields["content"])

    def test_child(self):
        """Child logger inherits settings."""
        child = log.new("child")
        self.assertEqual(child._name, "root.child")
