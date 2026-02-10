"""Tests for common/sqid.py and logxpy/src/_sqid.py -- Sqid generation and parsing."""
from __future__ import annotations

import re
import threading
import pytest

from common.sqid import (
    SqidGenerator, sqid, child_sqid, generate_task_id,
    _encode_base62, _decode_base62,
    SqidParser, SqidInfo, parse_sqid,
    sqid_parent, sqid_depth, sqid_root,
)


# ============================================================================
# Base62 Encoding
# ============================================================================

class TestEncodeBase62:
    def test_zero(self):
        assert _encode_base62(0) == "0"

    def test_small_values(self):
        assert _encode_base62(1) == "1"
        assert _encode_base62(9) == "9"

    def test_boundary_62(self):
        assert _encode_base62(62) == "10"

    def test_large_value(self):
        result = _encode_base62(999999)
        assert isinstance(result, str)
        assert len(result) > 0


class TestDecodeBase62:
    def test_zero(self):
        assert _decode_base62("0") == 0

    def test_roundtrip(self):
        for n in [0, 1, 10, 61, 62, 100, 999, 12345, 999999]:
            assert _decode_base62(_encode_base62(n)) == n


# ============================================================================
# SqidGenerator
# ============================================================================

class TestSqidGenerator:
    def test_generate_returns_string(self):
        gen = SqidGenerator()
        result = gen.generate()
        assert isinstance(result, str)

    def test_generate_format(self):
        gen = SqidGenerator()
        result = gen.generate()
        assert "." in result
        parts = result.split(".")
        assert len(parts) == 2
        assert len(parts[0]) >= 2  # PID prefix

    def test_sequential_ids_increment(self):
        gen = SqidGenerator()
        id1 = gen.generate()
        id2 = gen.generate()
        assert id1 != id2

    def test_child_appends_index(self):
        gen = SqidGenerator()
        root = gen.generate()
        child = gen.child(root, 2)
        assert child == f"{root}.2"

    def test_thread_safety(self):
        gen = SqidGenerator()
        ids = []
        lock = threading.Lock()

        def generate_ids():
            for _ in range(100):
                result = gen.generate()
                with lock:
                    ids.append(result)

        threads = [threading.Thread(target=generate_ids) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(ids) == 1000
        assert len(set(ids)) == 1000  # All unique


# ============================================================================
# Module-level Functions
# ============================================================================

class TestSqidFunction:
    def test_returns_string(self):
        result = sqid()
        assert isinstance(result, str)
        assert "." in result

    def test_uniqueness(self):
        ids = {sqid() for _ in range(100)}
        assert len(ids) == 100


class TestChildSqid:
    def test_appends_index(self):
        parent = sqid()
        result = child_sqid(parent, 3)
        assert result == f"{parent}.3"

    def test_nested_child(self):
        parent = sqid()
        child = child_sqid(parent, 1)
        grandchild = child_sqid(child, 2)
        assert grandchild == f"{parent}.1.2"


class TestGenerateTaskId:
    def test_sqid_mode(self):
        result = generate_task_id(use_sqid=True)
        assert "." in result
        assert len(result) < 20

    def test_uuid4_mode(self):
        result = generate_task_id(use_sqid=False)
        assert len(result) == 36
        assert "-" in result


# ============================================================================
# SqidParser
# ============================================================================

class TestSqidParser:
    def test_parse_root(self):
        info = SqidParser.parse("Xa.1")
        assert info.pid_prefix == "Xa"
        assert info.is_root is True

    def test_parse_child(self):
        info = SqidParser.parse("Xa.1.2")
        assert info.depth == 2
        assert info.parent == "Xa.1"

    def test_parse_deep(self):
        info = SqidParser.parse("Xa.1.2.3")
        assert info.depth == 3
        assert info.child_indices == (1, 2, 3)

    def test_parse_invalid_no_dot(self):
        with pytest.raises(ValueError):
            SqidParser.parse("invalid")

    def test_parse_invalid_empty(self):
        with pytest.raises(ValueError):
            SqidParser.parse("")

    def test_parent_of_root(self):
        assert SqidParser.parent("Xa.1") is None

    def test_parent_of_child(self):
        assert SqidParser.parent("Xa.1.2.3") == "Xa.1.2"

    def test_depth(self):
        assert SqidParser.depth("Xa.1") == 1
        assert SqidParser.depth("Xa.1.2.3") == 3

    def test_is_child_of_true(self):
        assert SqidParser.is_child_of("Xa.1", "Xa.1.2") is True

    def test_is_child_of_false_same(self):
        assert SqidParser.is_child_of("Xa.1", "Xa.1") is False

    def test_is_child_of_false_different(self):
        assert SqidParser.is_child_of("Xa.1", "Xb.1") is False

    def test_is_sibling_of(self):
        assert SqidParser.is_sibling_of("Xa.1.1", "Xa.1.2") is True

    def test_is_sibling_of_roots(self):
        # Roots have None parent, so they're not siblings
        assert SqidParser.is_sibling_of("Xa.1", "Xa.2") is False

    def test_root_extraction(self):
        assert SqidParser.root("Xa.1.2.3") == "Xa.1"

    def test_children_generation(self):
        children = SqidParser.children("Xa.1")
        assert len(children) == 9
        assert children[0] == "Xa.1.1"
        assert children[8] == "Xa.1.9"


class TestConvenienceFunctions:
    def test_parse_sqid(self):
        info = parse_sqid("Xa.1")
        assert isinstance(info, SqidInfo)

    def test_sqid_parent(self):
        assert sqid_parent("Xa.1.2") == "Xa.1"

    def test_sqid_depth(self):
        assert sqid_depth("Xa.1.2") == 2

    def test_sqid_root(self):
        assert sqid_root("Xa.1.2.3") == "Xa.1"


# ============================================================================
# Re-exports from logxpy._sqid
# ============================================================================

class TestLogxpySqidReexports:
    def test_imports_work(self):
        from logxpy.src._sqid import SqidGenerator, sqid, child_sqid, generate_task_id, _encode
        assert callable(sqid)
        assert callable(child_sqid)
        assert callable(generate_task_id)
        assert callable(_encode)

    def test_encode_alias(self):
        from logxpy.src._sqid import _encode
        assert _encode(0) == "0"
        assert _encode(62) == "10"
