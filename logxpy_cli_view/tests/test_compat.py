"""Tests for compat module."""

from __future__ import annotations

from logxpy_cli_view._compat import dump_json_bytes


class TestDumpJsonBytes:
    """Tests for dump_json_bytes."""

    def test_returns_bytes(self):
        """Returns UTF-8 encoded bytes."""
        result = dump_json_bytes({"a": 42})
        assert isinstance(result, bytes)
        assert result == b'{"a": 42}'

    def test_encodes_unicode(self):
        """Properly encodes Unicode characters."""
        result = dump_json_bytes({"msg": "hello \u2603"})
        assert isinstance(result, bytes)
        assert b"\xe2\x98\x83" in result  # Snowman UTF-8
