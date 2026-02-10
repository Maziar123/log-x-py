#!/usr/bin/env python3
"""Example 07: All Data Types - how different types are displayed in the tree viewer."""

from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from logxpy import log, start_action


def log_primitives():
    with start_action(action_type="primitives:demo"):
        log.info("Primitive types",
                 integer=42, negative_int=-123, zero=0, large_int=1_000_000_000,
                 float_num=3.14159, negative_float=-2.5, scientific=1.23e-10,
                 bool_true=True, bool_false=False,
                 string="Hello World", empty_string="",
                 unicode_str="Hello 世界", null_value=None)


def log_collections():
    with start_action(action_type="collections:demo"):
        log.info("Lists",
                 empty_list=[], numbers=[1, 2, 3, 4, 5],
                 mixed=[1, "two", 3.0, True, None],
                 nested=[[1, 2], [3, 4], [5, 6]])

        log.info("Dicts",
                 empty_dict={},
                 simple={"name": "Alice", "age": 30, "active": True},
                 nested={"user": {"id": 123, "profile": {"name": "Bob",
                         "settings": {"theme": "dark", "notifications": True}}}})

        log.info("Tuples & Sets",
                 tuple_val=(1, 2, 3),
                 set_val={1, 2, 3, 4, 5},
                 string_set={"apple", "banana", "cherry"})


def log_complex_structures():
    with start_action(action_type="complex:structures"):
        log.info("API Response", data={
            "status": "success", "code": 200,
            "data": {
                "users": [
                    {"id": 1, "name": "Alice", "roles": ["admin", "user"],
                     "metadata": {"last_login": "2026-02-05T10:00:00Z", "login_count": 42}},
                    {"id": 2, "name": "Bob", "roles": ["user"],
                     "metadata": {"last_login": "2026-02-04T15:30:00Z", "login_count": 15}},
                ],
                "pagination": {"page": 1, "per_page": 10, "total": 2},
            },
            "meta": {"request_id": "req-123-456", "duration_ms": 45},
        })

        log.info("Config", config={
            "app": {"name": "MyApp", "version": "2.5.0", "environment": "production"},
            "database": {"host": "db.example.com", "port": 5432,
                         "pool": {"min_size": 5, "max_size": 20, "timeout": 30}},
            "cache": {"type": "redis", "host": "cache.example.com", "ttl": 3600},
            "features": {"authentication": True, "analytics": True, "beta": False},
        })


def log_special_values():
    with start_action(action_type="special:values"):
        log.info("Special strings",
                 special_chars="!@#$%^&*()_+-=[]{}|;':<>?",
                 path_unix="/usr/local/bin/python",
                 url="https://example.com/path?key=value&foo=bar",
                 email="user@example.com",
                 long_string="A" * 200,
                 sql="SELECT * FROM users WHERE id = 123 AND status = 'active'")

        log.info("Special numbers",
                 very_large=9_999_999_999_999_999,
                 tiny_float=0.000000001,
                 negative_inf=float("-inf"))

        log.info("Empty values",
                 empty_string="", empty_list=[], empty_dict={},
                 none_value=None, zero=0, false_bool=False)


def log_python_objects():
    with start_action(action_type="python:objects"):
        log.info("Datetime types",
                 datetime_str=str(datetime.now()),
                 date_str=str(date.today()),
                 time_str=str(time(14, 30, 45)),
                 timestamp=datetime.now().timestamp())

        log.info("Other types",
                 path=str(Path("/home/user/file.txt")),
                 uuid=str(UUID("12345678-1234-5678-1234-567812345678")),
                 decimal=str(Decimal("123.456")))


def log_error_scenarios():
    with start_action(action_type="errors:demo"):
        log.error("Validation error",
                  error_type="ValidationError", error_message="Invalid email format",
                  field="email", provided_value="not-an-email", error_code="VAL_001")

        log.error("Database error",
                  error_type="DatabaseError", error_message="Connection timeout",
                  host="db.example.com", port=5432, retry_count=3,
                  stacktrace=["database.py:45", "connection.py:123", "pool.py:67"])


def log_performance_metrics():
    with start_action(action_type="performance:metrics"):
        log.info("Timing",
                 operation="api_request", duration_ms=145.67, cpu_time_ms=98.23,
                 memory_mb=256.5, db_queries=3, cache_hits=15, cache_misses=2)

        log.info("Stats",
                 rps=1250.5, avg_ms=45.3, p50_ms=42.1, p95_ms=89.6,
                 p99_ms=145.8, error_rate=0.05, success_rate=99.95)


def log_nested_actions():
    with start_action(action_type="nested:level1", layer=1):
        log.info("Level 1", data={"key": "value1"})
        with start_action(action_type="nested:level2", layer=2):
            log.info("Level 2", data={"key": "value2"})
            with start_action(action_type="nested:level3", layer=3):
                log.info("Level 3", data={"key": "value3"})
                with start_action(action_type="nested:level4", layer=4):
                    log.info("Level 4", complex_data={
                        "arrays": [[1, 2], [3, 4]],
                        "objects": {"nested": {"deep": {"value": 42}}},
                        "mixed": [{"id": 1}, {"id": 2}, {"id": 3}],
                    })


log_primitives()
log_collections()
log_complex_structures()
log_special_values()
log_python_objects()
log_error_scenarios()
log_performance_metrics()
log_nested_actions()

print("✓ Log created: example_07_all_data_types.log")
