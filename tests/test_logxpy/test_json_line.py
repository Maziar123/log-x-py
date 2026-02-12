"""Tests for _json_line module - fast JSON serialization.

This module tests edge cases, error handling, and output quality
for the optimized JSON line builder.
"""

import json
import sys
from typing import Any

import pytest

sys.path.insert(0, "/mnt/N1/MZ/AMZ/Projects/Prog/a_cross/log-x-py")

from logxpy.src._json_line import build_json_line, _format_task_level, _format_fields


class TestFormatTaskLevel:
    """Test task level formatting."""
    
    def test_single_level(self):
        """Single level tuple."""
        assert _format_task_level((1,)) == "[1]"
        assert _format_task_level((5,)) == "[5]"
    
    def test_multi_level(self):
        """Multi-level hierarchy."""
        assert _format_task_level((1, 2)) == "[1,2]"
        assert _format_task_level((1, 2, 3)) == "[1,2,3]"
        assert _format_task_level((3, 2, 1, 4)) == "[3,2,1,4]"
    
    def test_deep_nesting(self):
        """Deep nesting (7 levels)."""
        level = (1, 2, 3, 4, 5, 6, 7)
        assert _format_task_level(level) == "[1,2,3,4,5,6,7]"


class TestFormatFields:
    """Test field formatting."""
    
    def test_empty_dict(self):
        """Empty fields returns None."""
        assert _format_fields({}) is None
    
    def test_none_values_skipped(self):
        """None values are skipped."""
        result = _format_fields({"a": 1, "b": None, "c": 3})
        assert result is not None
        assert '"a":1' in result
        assert '"c":3' in result
        assert "b" not in result
    
    def test_all_none_values(self):
        """All None values returns None."""
        assert _format_fields({"a": None, "b": None}) is None
    
    def test_string_field(self):
        """String field formatting."""
        result = _format_fields({"name": "Alice"})
        assert result == '"name":"Alice"'
    
    def test_string_with_quotes(self):
        """String with quotes is properly escaped."""
        result = _format_fields({"msg": 'Say "hello"'})
        # json.dumps should escape the quotes
        assert '"msg":' in result
        assert "hello" in result
    
    def test_integer_field(self):
        """Integer field formatting."""
        result = _format_fields({"count": 42})
        assert result == '"count":42'
    
    def test_float_field(self):
        """Float field formatting."""
        result = _format_fields({"price": 19.99})
        assert result == '"price":19.99'
    
    def test_boolean_true(self):
        """Boolean true formatting."""
        result = _format_fields({"active": True})
        assert result == '"active":true'
    
    def test_boolean_false(self):
        """Boolean false formatting."""
        result = _format_fields({"active": False})
        assert result == '"active":false'
    
    def test_list_field(self):
        """List field formatting."""
        result = _format_fields({"items": [1, 2, 3]})
        assert result == '"items":[1, 2, 3]'
    
    def test_nested_dict(self):
        """Nested dict formatting."""
        result = _format_fields({"data": {"nested": "value"}})
        assert '"data":' in result
        # json.dumps may add spaces, so parse to verify
        parsed = json.loads("{" + result + "}")
        assert parsed["data"]["nested"] == "value"
    
    def test_multiple_fields(self):
        """Multiple fields of different types."""
        result = _format_fields({
            "id": 123,
            "name": "test",
            "active": True,
            "score": 95.5,
        })
        assert '"id":123' in result
        assert '"name":"test"' in result
        assert '"active":true' in result
        assert '"score":95.5' in result
    
    def test_complex_nested(self):
        """Complex nested structures."""
        result = _format_fields({
            "user": {
                "id": 1,
                "tags": ["admin", "active"],
            },
            "count": 42,
        })
        parsed = json.loads("{" + result + "}")
        assert parsed["user"]["id"] == 1
        assert parsed["user"]["tags"] == ["admin", "active"]
        assert parsed["count"] == 42
    
    def test_arbitrary_object(self):
        """Arbitrary objects are converted to string."""
        class CustomObj:
            def __str__(self):
                return "custom"
        
        result = _format_fields({"obj": CustomObj()})
        assert '"obj":"custom"' in result


class TestBuildJsonLine:
    """Test main JSON line builder function."""
    
    def test_basic_message(self):
        """Basic message with no fields."""
        line = build_json_line(
            message="Hello",
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1,),
        )
        parsed = json.loads(line)
        assert parsed["msg"] == "Hello"
        assert parsed["mt"] == "info"
        assert parsed["tid"] == "Xa.1"
        assert parsed["lvl"] == [1]
        assert "ts" in parsed
    
    def test_message_with_fields(self):
        """Message with additional fields."""
        line = build_json_line(
            message="User action",
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1,),
            fields={"user_id": 123, "action": "login"},
        )
        parsed = json.loads(line)
        assert parsed["msg"] == "User action"
        assert parsed["user_id"] == 123
        assert parsed["action"] == "login"
    
    def test_message_with_quotes(self):
        """Message containing quotes."""
        line = build_json_line(
            message='He said "hello"',
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1,),
        )
        parsed = json.loads(line)
        assert parsed["msg"] == 'He said "hello"'
    
    def test_message_with_backslash(self):
        """Message containing backslash."""
        line = build_json_line(
            message="Path: C:\\Users\\test",
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1,),
        )
        parsed = json.loads(line)
        assert parsed["msg"] == "Path: C:\\Users\\test"
    
    def test_message_with_newline(self):
        """Message containing newline."""
        line = build_json_line(
            message="Line 1\nLine 2",
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1,),
        )
        parsed = json.loads(line)
        assert parsed["msg"] == "Line 1\nLine 2"
    
    def test_unicode_message(self):
        """Unicode characters in message."""
        line = build_json_line(
            message="Hello 世界 🌍",
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1,),
        )
        parsed = json.loads(line)
        assert parsed["msg"] == "Hello 世界 🌍"
    
    def test_empty_message(self):
        """Empty message string."""
        line = build_json_line(
            message="",
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1,),
        )
        parsed = json.loads(line)
        assert parsed["msg"] == ""
    
    def test_long_message(self):
        """Very long message."""
        long_msg = "x" * 10000
        line = build_json_line(
            message=long_msg,
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1,),
        )
        parsed = json.loads(line)
        assert parsed["msg"] == long_msg
    
    def test_fields_with_none(self):
        """Fields containing None values."""
        line = build_json_line(
            message="test",
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1,),
            fields={"a": 1, "b": None, "c": 3},
        )
        parsed = json.loads(line)
        assert parsed["a"] == 1
        assert parsed["c"] == 3
        assert "b" not in parsed
    
    def test_all_none_fields(self):
        """All fields are None - should not have trailing comma."""
        line = build_json_line(
            message="test",
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1,),
            fields={"a": None, "b": None},
        )
        # Should be valid JSON
        parsed = json.loads(line)
        assert parsed["msg"] == "test"
        assert "a" not in parsed
        assert "b" not in parsed
    
    def test_custom_timestamp(self):
        """Custom timestamp."""
        ts = 1234567890.123456
        line = build_json_line(
            message="test",
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1,),
            timestamp=ts,
        )
        parsed = json.loads(line)
        assert parsed["ts"] == pytest.approx(ts, abs=0.000001)
    
    def test_multi_level(self):
        """Multi-level task hierarchy."""
        line = build_json_line(
            message="test",
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1, 2, 3),
        )
        parsed = json.loads(line)
        assert parsed["lvl"] == [1, 2, 3]
    
    def test_complex_fields(self):
        """Complex nested field structures."""
        line = build_json_line(
            message="Data",
            message_type="debug",
            task_uuid="Xa.1",
            task_level=(1,),
            fields={
                "user": {"id": 1, "name": "Alice"},
                "tags": ["admin", "active"],
                "count": 42,
                "score": 95.5,
                "active": True,
                "meta": None,  # Should be skipped
            },
        )
        parsed = json.loads(line)
        assert parsed["user"]["id"] == 1
        assert parsed["tags"] == ["admin", "active"]
        assert parsed["count"] == 42
        assert parsed["score"] == 95.5
        assert parsed["active"] is True
        assert "meta" not in parsed


class TestJsonLineEdgeCases:
    """Edge cases and error conditions."""
    
    def test_special_characters_in_fields(self):
        """Special characters in field values."""
        line = build_json_line(
            message="test",
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1,),
            fields={
                "path": "/tmp/file.txt",
                "regex": ".*\\d+",
                "quote": 'He said "hi"',
            },
        )
        # Should not raise
        parsed = json.loads(line)
        assert parsed["path"] == "/tmp/file.txt"
    
    def test_numeric_string(self):
        """String that looks like a number."""
        line = build_json_line(
            message="test",
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1,),
            fields={"code": "12345"},  # String, not int
        )
        parsed = json.loads(line)
        assert parsed["code"] == "12345"
        assert isinstance(parsed["code"], str)
    
    def test_zero_and_negative(self):
        """Zero and negative numbers."""
        line = build_json_line(
            message="test",
            message_type="info",
            task_uuid="Xa.1",
            task_level=(1,),
            fields={
                "zero": 0,
                "negative": -42,
                "neg_float": -3.14,
            },
        )
        parsed = json.loads(line)
        assert parsed["zero"] == 0
        assert parsed["negative"] == -42
        assert parsed["neg_float"] == -3.14


class TestJsonLinePerformance:
    """Performance characteristics (not strict benchmarks)."""
    
    def test_simple_message_performance(self):
        """Simple messages should be fast."""
        import time
        
        N = 10000
        start = time.perf_counter()
        
        for i in range(N):
            build_json_line(
                message="test",
                message_type="info",
                task_uuid="Xa.1",
                task_level=(1,),
                fields={"i": i},
            )
        
        elapsed = time.perf_counter() - start
        throughput = N / elapsed
        
        # Should handle at least 200K L/s
        assert throughput > 200000, f"Throughput {throughput} below 200K L/s"
    
    def test_complex_message_performance(self):
        """Complex messages with nested fields."""
        import time
        
        N = 10000
        fields = {
            "user": {"id": 1, "name": "Alice", "tags": ["admin"]},
            "data": {"nested": {"deep": "value"}},
            "items": [1, 2, 3, 4, 5],
        }
        
        start = time.perf_counter()
        
        for i in range(N):
            build_json_line(
                message="Complex data",
                message_type="debug",
                task_uuid="Xa.1",
                task_level=(1,),
                fields=fields,
            )
        
        elapsed = time.perf_counter() - start
        throughput = N / elapsed
        
        # Complex messages should still be reasonably fast (>80K L/s on CI)
        assert throughput > 80000, f"Throughput {throughput} below 80K L/s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
