"""Tests for eliot._config."""
from unittest import TestCase
import os
from logxpy._config import Config

class ConfigTests(TestCase):
    def test_defaults(self):
        """Default config is sane."""
        cfg = Config()
        self.assertEqual(cfg.format, "rich")
        self.assertEqual(cfg.destinations, ["console"])

    def test_env_override(self):
        """Environment variables override defaults."""
        os.environ["LOGGERX_LEVEL"] = "ERROR"
        try:
            cfg = Config.load()
            from eliot._types import Level
            self.assertEqual(cfg.level, Level.ERROR)
        finally:
            del os.environ["LOGGERX_LEVEL"]
