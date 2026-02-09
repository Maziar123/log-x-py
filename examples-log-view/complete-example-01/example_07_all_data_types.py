#!/usr/bin/env python3
"""
Example 07: All Data Types & Objects Demo
==========================================
Comprehensive test showing how different data types are displayed in the tree viewer.
Tests primitives, collections, nested structures, and edge cases.
"""

import sys
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from uuid import UUID

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "logxpy"))

try:
    from logxpy import Message, start_action, to_file
except ImportError:
    from eliot import Message, start_action, to_file

# Setup logging (delete old log first)
log_file = Path(__file__).parent / "example_07_all_data_types.log"
if log_file.exists():
    log_file.unlink()
with open(log_file, "w", encoding="utf-8") as f:
    to_file(f)


def log_primitives():
    """Log all primitive data types."""
    with start_action(action_type="primitives:demo"):
        Message.log(
            message_type="primitives:types",
            # Numbers
            integer=42,
            negative_int=-123,
            zero=0,
            large_int=1_000_000_000,
            float_num=3.14159,
            negative_float=-2.5,
            scientific=1.23e-10,
            infinity=float("inf"),
            # Boolean
            bool_true=True,
            bool_false=False,
            # String
            string="Hello World",
            empty_string="",
            unicode_str="Hello 世界 🌍",
            multiline="Line 1\nLine 2\nLine 3",
            # None
            null_value=None,
        )


def log_collections():
    """Log various collection types."""
    with start_action(action_type="collections:demo"):
        Message.log(
            message_type="collections:list",
            empty_list=[],
            numbers_list=[1, 2, 3, 4, 5],
            mixed_list=[1, "two", 3.0, True, None],
            nested_list=[[1, 2], [3, 4], [5, 6]],
            deep_nested=[[[1, 2], [3]], [[4, [5, 6]]]],
        )

        Message.log(
            message_type="collections:dict",
            empty_dict={},
            simple_dict={"name": "Alice", "age": 30, "active": True},
            nested_dict={
                "user": {
                    "id": 123,
                    "profile": {
                        "name": "Bob",
                        "email": "bob@example.com",
                        "settings": {
                            "theme": "dark",
                            "notifications": True,
                        },
                    },
                },
            },
            mixed_keys={
                "string_key": "value1",
                "number_key": 42,
                "bool_key": True,
            },
        )

        Message.log(
            message_type="collections:tuple",
            empty_tuple=(),
            simple_tuple=(1, 2, 3),
            nested_tuple=((1, 2), (3, 4)),
            mixed_tuple=(1, "two", 3.0, True, None),
        )

        Message.log(
            message_type="collections:set",
            number_set={1, 2, 3, 4, 5},
            string_set={"apple", "banana", "cherry"},
        )


def log_complex_structures():
    """Log complex nested structures."""
    with start_action(action_type="complex:structures"):
        # API response-like structure
        Message.log(
            message_type="complex:api_response",
            data={
                "status": "success",
                "code": 200,
                "timestamp": "2026-02-05T14:30:00Z",
                "data": {
                    "users": [
                        {
                            "id": 1,
                            "name": "Alice",
                            "email": "alice@example.com",
                            "roles": ["admin", "user"],
                            "metadata": {
                                "last_login": "2026-02-05T10:00:00Z",
                                "login_count": 42,
                            },
                        },
                        {
                            "id": 2,
                            "name": "Bob",
                            "email": "bob@example.com",
                            "roles": ["user"],
                            "metadata": {
                                "last_login": "2026-02-04T15:30:00Z",
                                "login_count": 15,
                            },
                        },
                    ],
                    "pagination": {
                        "page": 1,
                        "per_page": 10,
                        "total": 2,
                        "total_pages": 1,
                    },
                },
                "meta": {
                    "request_id": "req-123-456",
                    "duration_ms": 45,
                },
            },
        )

        # Configuration-like structure
        Message.log(
            message_type="complex:config",
            config={
                "app": {
                    "name": "MyApp",
                    "version": "2.5.0",
                    "environment": "production",
                },
                "database": {
                    "host": "db.example.com",
                    "port": 5432,
                    "name": "myapp_db",
                    "pool": {
                        "min_size": 5,
                        "max_size": 20,
                        "timeout": 30,
                    },
                },
                "cache": {
                    "type": "redis",
                    "host": "cache.example.com",
                    "port": 6379,
                    "ttl": 3600,
                },
                "features": {
                    "authentication": True,
                    "analytics": True,
                    "beta_features": False,
                },
            },
        )


def log_special_values():
    """Log special and edge case values."""
    with start_action(action_type="special:values"):
        Message.log(
            message_type="special:strings",
            # Special characters
            special_chars="!@#$%^&*()_+-=[]{}|;':\",./<>?",
            path_unix="/usr/local/bin/python",
            path_windows="C:\\Users\\Alice\\Documents\\file.txt",
            url="https://example.com/path?key=value&foo=bar",
            email="user@example.com",
            # Escape sequences
            tab_separated="col1\tcol2\tcol3",
            escaped_quotes='He said "Hello" to me',
            single_quotes="It's a beautiful day",
            # Very long string
            long_string="A" * 200,
            # SQL-like
            sql_query="SELECT * FROM users WHERE id = 123 AND status = 'active'",
            # JSON-like string
            json_str='{"key": "value", "number": 42, "bool": true}',
        )

        Message.log(
            message_type="special:numbers",
            # Edge cases
            very_large=9_999_999_999_999_999,
            very_small=-9_999_999_999_999_999,
            tiny_float=0.000000001,
            precise_float=1.23456789012345,
            # Special floats
            negative_inf=float("-inf"),
            nan=float("nan"),
        )

        Message.log(
            message_type="special:empty_values",
            empty_string="",
            empty_list=[],
            empty_dict={},
            empty_tuple=(),
            none_value=None,
            zero=0,
            false_bool=False,
        )


def log_python_objects():
    """Log Python-specific object types."""
    with start_action(action_type="python:objects"):
        Message.log(
            message_type="python:datetime",
            # Note: These will be serialized to strings/numbers
            datetime_str=str(datetime.now()),
            date_str=str(date.today()),
            time_str=str(time(14, 30, 45)),
            timestamp=datetime.now().timestamp(),
        )

        Message.log(
            message_type="python:types",
            path_str=str(Path("/home/user/file.txt")),
            uuid_str=str(UUID("12345678-1234-5678-1234-567812345678")),
            decimal_str=str(Decimal("123.456")),
            bytes_str="binary data here",
        )


def log_error_scenarios():
    """Log error and exception scenarios."""
    with start_action(action_type="errors:demo"):
        Message.log(
            message_type="errors:validation",
            error_type="ValidationError",
            error_message="Invalid email format",
            field="email",
            provided_value="not-an-email",
            expected_format="user@example.com",
            error_code="VAL_001",
        )

        Message.log(
            message_type="errors:database",
            error_type="DatabaseError",
            error_message="Connection timeout",
            host="db.example.com",
            port=5432,
            timeout_seconds=30,
            retry_count=3,
            stacktrace=[
                "File: database.py, Line: 45",
                "File: connection.py, Line: 123",
                "File: pool.py, Line: 67",
            ],
        )


def log_performance_metrics():
    """Log performance and metrics data."""
    with start_action(action_type="performance:metrics"):
        Message.log(
            message_type="performance:timing",
            operation="api_request",
            duration_ms=145.67,
            cpu_time_ms=98.23,
            memory_mb=256.5,
            db_queries=3,
            cache_hits=15,
            cache_misses=2,
        )

        Message.log(
            message_type="performance:stats",
            requests_per_second=1250.5,
            avg_response_time_ms=45.3,
            p50_ms=42.1,
            p95_ms=89.6,
            p99_ms=145.8,
            error_rate_percent=0.05,
            success_rate_percent=99.95,
        )


def log_nested_actions():
    """Log deeply nested actions to test tree visualization."""
    with start_action(action_type="nested:level1", layer=1):
        Message.log(message_type="nested:data", level=1, data={"key": "value1"})

        with start_action(action_type="nested:level2", layer=2):
            Message.log(message_type="nested:data", level=2, data={"key": "value2"})

            with start_action(action_type="nested:level3", layer=3):
                Message.log(message_type="nested:data", level=3, data={"key": "value3"})

                with start_action(action_type="nested:level4", layer=4):
                    Message.log(
                        message_type="nested:deep_data",
                        level=4,
                        complex_data={
                            "arrays": [[1, 2], [3, 4]],
                            "objects": {"nested": {"deep": {"value": 42}}},
                            "mixed": [{"id": 1}, {"id": 2}, {"id": 3}],
                        },
                    )


def main():
    """Run all data type demonstrations."""
    print("=" * 70)
    print("Running Example 07: All Data Types & Objects Demo")
    print("=" * 70)
    print()

    print("📊 Logging primitives...")
    log_primitives()

    print("📦 Logging collections...")
    log_collections()

    print("🔗 Logging complex structures...")
    log_complex_structures()

    print("⚠️  Logging special values...")
    log_special_values()

    print("🐍 Logging Python objects...")
    log_python_objects()

    print("❌ Logging error scenarios...")
    log_error_scenarios()

    print("⚡ Logging performance metrics...")
    log_performance_metrics()

    print("🌲 Logging nested actions...")
    log_nested_actions()

    print()
    print("=" * 70)
    print(f"✅ Complete! Log created: {log_file}")
    print("=" * 70)
    print()
    print("View the log:")
    print(f"  python view_tree.py {log_file.name}")
    print(f"  python view_tree.py {log_file.name} --ascii")
    print(f"  python view_tree.py {log_file.name} --depth-limit 3")
    print()
    print("Log Statistics:")
    with open(log_file, encoding="utf-8") as log_f:
        entry_count = sum(1 for line in log_f if line.strip())
    print(f"  Total entries: {entry_count}")
    print(f"  File size: {log_file.stat().st_size} bytes")
    print()


if __name__ == "__main__":
    main()
