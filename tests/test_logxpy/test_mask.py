"""Tests for logxpy/src/_mask.py -- Field masking."""
from __future__ import annotations

from logxpy.src._mask import Masker


class TestMasker:
    def test_mask_by_name(self):
        m = Masker(["password"], [])
        result = m.mask({"password": "secret", "user": "alice"})
        assert result["password"] == "***"
        assert result["user"] == "alice"

    def test_case_insensitive(self):
        m = Masker(["Password"], [])
        result = m.mask({"password": "secret"})
        assert result["password"] == "***"

    def test_case_insensitive_reverse(self):
        m = Masker(["password"], [])
        result = m.mask({"PASSWORD": "secret"})
        assert result["PASSWORD"] == "***"

    def test_nested_dict(self):
        m = Masker(["token"], [])
        result = m.mask({"config": {"token": "abc123"}})
        assert result["config"]["token"] == "***"

    def test_deeply_nested_dict(self):
        m = Masker(["secret"], [])
        result = m.mask({"a": {"b": {"secret": "hidden"}}})
        assert result["a"]["b"]["secret"] == "***"

    def test_pattern_masking(self):
        m = Masker([], [r"\d{4}-\d{4}-\d{4}-\d{4}"])
        result = m.mask({"card": "1234-5678-9012-3456"})
        assert result["card"] == "***"

    def test_pattern_partial_match(self):
        """Pattern replaces only matching part of string."""
        m = Masker([], [r"\d{4}-\d{4}-\d{4}-\d{4}"])
        result = m.mask({"info": "Card: 1234-5678-9012-3456 end"})
        assert "1234" not in result["info"]
        assert "***" in result["info"]

    def test_unchanged_fields(self):
        m = Masker(["password"], [])
        result = m.mask({"name": "alice", "age": 30})
        assert result["name"] == "alice"
        assert result["age"] == 30

    def test_empty_masker(self):
        m = Masker([], [])
        result = m.mask({"password": "secret"})
        assert result["password"] == "secret"

    def test_list_of_dicts_with_masked_key(self):
        """Lists are iterated with the parent key for masking."""
        m = Masker(["items"], [])
        result = m.mask({"items": [{"a": 1}, {"b": 2}]})
        # The key "items" is in the mask list, so the whole value is masked
        assert result["items"] == "***"

    def test_list_values_non_masked_key(self):
        """Lists under non-masked keys recurse into contained dicts."""
        m = Masker(["secret"], [])
        result = m.mask({"users": [{"secret": "x"}, {"ok": 1}]})
        # The list items that are dicts get recursed into via _mask -> mask()
        # So "secret" key inside nested dicts IS masked
        assert result["users"][0]["secret"] == "***"
        assert result["users"][1]["ok"] == 1

    def test_multiple_mask_fields(self):
        m = Masker(["password", "token", "api_key"], [])
        result = m.mask({
            "password": "p123",
            "token": "t456",
            "api_key": "k789",
            "name": "test",
        })
        assert result["password"] == "***"
        assert result["token"] == "***"
        assert result["api_key"] == "***"
        assert result["name"] == "test"

    def test_multiple_patterns(self):
        m = Masker([], [r"\b\d{3}-\d{2}-\d{4}\b", r"\b\d{16}\b"])
        result = m.mask({
            "ssn": "123-45-6789",
            "card": "1234567890123456",
        })
        assert result["ssn"] == "***"
        assert result["card"] == "***"

    def test_non_string_non_dict_non_list(self):
        """Non-string, non-dict, non-list values are returned as-is."""
        m = Masker([], [r"\d+"])
        result = m.mask({"count": 42, "flag": True, "nothing": None})
        assert result["count"] == 42
        assert result["flag"] is True
        assert result["nothing"] is None

    def test_empty_dict(self):
        m = Masker(["password"], [])
        result = m.mask({})
        assert result == {}

    def test_original_not_mutated(self):
        """Masking should not mutate the original dict."""
        m = Masker(["password"], [])
        original = {"password": "secret", "user": "alice"}
        result = m.mask(original)
        assert original["password"] == "secret"
        assert result["password"] == "***"
