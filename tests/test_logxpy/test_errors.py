"""Tests for logxpy/src/_errors.py -- Error extraction."""
from __future__ import annotations
from logxpy.src._errors import ErrorExtraction, register_exception_extractor

class TestErrorExtraction:
    def test_register_and_extract(self):
        ee = ErrorExtraction()
        ee.register_exception_extractor(ValueError, lambda e: {"code": 42})
        fields = ee.get_fields_for_exception(None, ValueError("test"))
        assert fields["code"] == 42

    def test_subclass_extraction(self):
        ee = ErrorExtraction()
        ee.register_exception_extractor(Exception, lambda e: {"msg": str(e)})
        fields = ee.get_fields_for_exception(None, ValueError("sub"))
        assert fields["msg"] == "sub"

    def test_unregistered_returns_empty(self):
        ee = ErrorExtraction()
        fields = ee.get_fields_for_exception(None, ValueError("test"))
        assert fields == {}

    def test_default_oserror_handler(self):
        from logxpy.src._errors import _error_extraction
        import errno
        err = OSError(errno.ENOENT, "Not found")
        fields = _error_extraction.get_fields_for_exception(None, err)
        assert "errno" in fields
