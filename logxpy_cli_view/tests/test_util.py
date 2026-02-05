"""Tests for util module."""

from __future__ import annotations

from logxpy_cli_view._util import (
    eliot_ns,
    format_namespace,
    is_namespace,
    namespaced,
)


class TestNamespaced:
    """Tests for namespaced function."""

    def test_creates_namespace(self):
        """Creates namespaced field."""
        ns = namespaced("prefix")
        result = ns("name")
        assert result.prefix == "prefix"
        assert result.name == "name"


class TestFormatNamespace:
    """Tests for format_namespace function."""

    def test_formats_namespace(self):
        """Formats as prefix/name."""
        ns = namespaced("foo")("bar")
        result = format_namespace(ns)
        assert result == "foo/bar"


class TestIsNamespace:
    """Tests for is_namespace function."""

    def test_true_for_namespace(self):
        """Returns True for namespace."""
        ns = namespaced("foo")("bar")
        assert is_namespace(ns) is True

    def test_false_for_string(self):
        """Returns False for string."""
        assert is_namespace("not a namespace") is False


class TestEliotNs:
    """Tests for eliot_ns factory."""

    def test_creates_eliot_namespace(self):
        """Creates eliot-prefixed namespace."""
        result = eliot_ns("timestamp")
        assert result.prefix == "eliot"
        assert result.name == "timestamp"
