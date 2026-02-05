"""Tests for eliot._compat."""
from unittest import TestCase
import warnings
from logxpy import log_message

class CompatTests(TestCase):
    def test_deprecations(self):
        """Old APIs emit warnings."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            log_message("test_msg")
            self.assertTrue(len(w) > 0)
            self.assertIn("deprecated", str(w[0].message))
