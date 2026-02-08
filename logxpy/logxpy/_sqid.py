"""Hierarchical Sqid generation for logging.

Ultra-short task IDs: PID_PREFIX.COUNTER[.CHILD...]
Example: "Xa.b" (4 chars) vs UUID4 (36 chars)
"""

from __future__ import annotations

import os
from itertools import count
from threading import Lock

_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_BASE = len(_ALPHABET)


def _encode(n: int) -> str:
    """Encode int to base62."""
    if n == 0:
        return _ALPHABET[0]
    r = []
    while n:
        r.append(_ALPHABET[n % _BASE])
        n //= _BASE
    return "".join(reversed(r))


class SqidGenerator:
    """Thread-safe hierarchical Sqid generator."""

    def __init__(self, prefix_len: int = 2):
        self._prefix = _encode(os.getpid())[-prefix_len:].rjust(prefix_len, "0")
        self._counter = count(1)
        self._lock = Lock()

    def generate(self) -> str:
        with self._lock:
            return f"{self._prefix}.{_encode(next(self._counter))}"

    def child(self, parent: str, index: int) -> str:
        return f"{parent}.{_encode(index)}"


# Global instance
_gen: SqidGenerator | None = None


def _get_gen() -> SqidGenerator:
    global _gen
    if _gen is None:
        _gen = SqidGenerator()
    return _gen


def sqid() -> str:
    """Generate new Sqid."""
    return _get_gen().generate()


def child_sqid(parent: str, index: int) -> str:
    """Generate child Sqid."""
    return _get_gen().child(parent, index)


def generate_task_id(use_sqid: bool = True) -> str:
    """Generate task ID (Sqid or UUID4)."""
    if use_sqid:
        return sqid()
    from uuid import uuid4

    return str(uuid4())


__all__ = ["SqidGenerator", "sqid", "child_sqid", "generate_task_id", "_encode"]
