"""Hierarchical Sqid generation for logging.

Ultra-short task IDs: PID_PREFIX.COUNTER[.CHILD...]
Example: "Xa.b" (4 chars) vs UUID4 (36 chars)

This module re-exports from common.sqid (the canonical implementation).
"""

from __future__ import annotations

from common.sqid import (
    SqidGenerator,
    _encode_base62 as _encode,
    child_sqid,
    generate_task_id,
    sqid,
)

__all__ = ["SqidGenerator", "sqid", "child_sqid", "generate_task_id", "_encode"]
