"""Pytest fixtures for logxy-log-parser tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_log_path(tmp_path: Path) -> Path:
    """Create a sample log file for testing.

    Args:
        tmp_path: Pytest temporary path fixture.

    Returns:
        Path: Path to the sample log file.
    """
    log_file = tmp_path / "sample.log"

    entries = [
        {
            "task_uuid": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": 1738332000.123,
            "message_type": "loggerx:info",
            "message": "Application started",
            "level": "info",
            "status": "started",
        },
        {
            "task_uuid": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": 1738332000.456,
            "message_type": "loggerx:debug",
            "message": "Loading configuration",
            "level": "debug",
            "status": "started",
        },
        {
            "task_uuid": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": 1738332000.789,
            "message_type": "loggerx:debug",
            "message": "Configuration loaded successfully",
            "level": "debug",
            "status": "succeeded",
            "duration_ns": 333000000,
        },
        {
            "task_uuid": "550e8400-e29b-41d4-a716-446655440001",
            "timestamp": 1738332002.000,
            "message_type": "loggerx:info",
            "message": "Processing user request",
            "level": "info",
            "status": "started",
            "user_id": 12345,
            "request_id": "req-001",
        },
        {
            "task_uuid": "550e8400-e29b-41d4-a716-446655440001",
            "timestamp": 1738332002.234,
            "message_type": "loggerx:warning",
            "message": "Cache miss for user data",
            "level": "warning",
            "user_id": 12345,
        },
        {
            "task_uuid": "550e8400-e29b-41d4-a716-446655440002",
            "timestamp": 1738332003.000,
            "message_type": "loggerx:success",
            "message": "Payment processed",
            "level": "success",
            "status": "succeeded",
            "payment_id": "pay-123",
            "amount": 99.99,
        },
        {
            "task_uuid": "550e8400-e29b-41d4-a716-446655440003",
            "timestamp": 1738332004.000,
            "message_type": "loggerx:error",
            "message": "Database connection failed",
            "level": "error",
            "status": "failed",
            "error_code": "DB_001",
        },
    ]

    with open(log_file, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    return log_file


@pytest.fixture
def error_log_path(tmp_path: Path) -> Path:
    """Create a log file with errors for testing.

    Args:
        tmp_path: Pytest temporary path fixture.

    Returns:
        Path: Path to the error log file.
    """
    log_file = tmp_path / "errors.log"

    entries = [
        {
            "task_uuid": "err-001",
            "timestamp": 1738332000.0,
            "message_type": "loggerx:error",
            "message": "Connection timeout",
            "level": "error",
            "status": "failed",
        },
        {
            "task_uuid": "err-001",
            "timestamp": 1738332001.0,
            "message_type": "loggerx:critical",
            "message": "System crash",
            "level": "critical",
            "status": "failed",
        },
        {
            "task_uuid": "err-002",
            "timestamp": 1738332002.0,
            "message_type": "loggerx:error",
            "message": "Connection timeout",
            "level": "error",
            "status": "failed",
        },
    ]

    with open(log_file, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    return log_file


@pytest.fixture
def complex_log_path(tmp_path: Path) -> Path:
    """Create a complex nested log file for testing.

    Args:
        tmp_path: Pytest temporary path fixture.

    Returns:
        Path: Path to the complex log file.
    """
    log_file = tmp_path / "complex.log"

    entries = [
        {
            "task_uuid": "complex-001",
            "timestamp": 1738332000.0,
            "level": "/",
            "message_type": "loggerx:info",
            "message": "Main task started",
            "status": "started",
        },
        {
            "task_uuid": "complex-001",
            "timestamp": 1738332001.0,
            "level": "/1",
            "message_type": "loggerx:info",
            "message": "Subtask 1 started",
            "action_type": "database.query",
            "status": "started",
        },
        {
            "task_uuid": "complex-001",
            "timestamp": 1738332002.0,
            "level": "/1",
            "message_type": "loggerx:success",
            "message": "Subtask 1 completed",
            "action_type": "database.query",
            "status": "succeeded",
            "duration_ns": 1000000000,
        },
        {
            "task_uuid": "complex-001",
            "timestamp": 1738332003.0,
            "level": "/2",
            "message_type": "loggerx:info",
            "message": "Subtask 2 started",
            "action_type": "api.call",
            "status": "started",
        },
        {
            "task_uuid": "complex-001",
            "timestamp": 1738332005.0,
            "level": "/2",
            "message_type": "loggerx:success",
            "message": "Subtask 2 completed",
            "action_type": "api.call",
            "status": "succeeded",
            "duration_ns": 2000000000,
        },
    ]

    with open(log_file, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    return log_file


@pytest.fixture
def sample_entries(sample_log_path: Path) -> list[dict]:
    """Get sample log entries as a list of dicts.

    Args:
        sample_log_path: Path to sample log file.

    Returns:
        list[dict]: List of log entry dictionaries.
    """
    from logxy_log_parser import LogParser

    parser = LogParser(sample_log_path)
    return [entry.to_dict() for entry in parser.parse()]
