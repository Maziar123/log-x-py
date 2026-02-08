"""
Type definitions for logxy-log-parser.

This module contains all type aliases and enums used throughout the library.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

# Core type aliases
type LogDict = dict[str, Any]
type TaskLevel = tuple[int, ...]


class Level(StrEnum):
    """Log level enum matching LogXPy."""

    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    NOTE = "note"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ActionStatus(StrEnum):
    """Action status enum."""

    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


# Message type patterns
MESSAGE_TYPE_PREFIX = "loggerx:"
