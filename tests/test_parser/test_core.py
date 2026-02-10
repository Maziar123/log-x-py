"""Tests for core parsing functionality."""

from __future__ import annotations

import json

import pytest

from logxy_log_parser import LogEntry, LogParser
from logxy_log_parser import ActionStatus, Level


class TestLogEntry:
    """Tests for LogEntry dataclass."""

    def test_from_dict_basic(self) -> None:
        """Test creating LogEntry from basic dictionary."""
        data = {
            "task_uuid": "test-uuid",
            "timestamp": 1738332000.0,
            "level": "/",
            "message_type": "loggerx:info",
            "message": "Test message",
        }

        entry = LogEntry.from_dict(data)

        assert entry.task_uuid == "test-uuid"
        assert entry.timestamp == 1738332000.0
        assert entry.message == "Test message"
        assert entry.task_level == ()

    def test_from_dict_with_task_level(self) -> None:
        """Test creating LogEntry with task level."""
        data = {
            "task_uuid": "test-uuid",
            "timestamp": 1738332000.0,
            "level": "/1/2",
            "message_type": "loggerx:info",
            "message": "Test message",
        }

        entry = LogEntry.from_dict(data)

        assert entry.task_level == (1, 2)
        assert entry.depth == 2

    def test_from_dict_with_action_status(self) -> None:
        """Test creating LogEntry with action status."""
        data = {
            "task_uuid": "test-uuid",
            "timestamp": 1738332000.0,
            "level": "/",
            "message_type": "loggerx:info",
            "status": "started",
        }

        entry = LogEntry.from_dict(data)

        assert entry.action_status == ActionStatus.STARTED

    def test_from_dict_with_duration(self) -> None:
        """Test creating LogEntry with duration."""
        data = {
            "task_uuid": "test-uuid",
            "timestamp": 1738332000.0,
            "level": "/",
            "message_type": "loggerx:info",
            "duration_ns": 1500000000,
        }

        entry = LogEntry.from_dict(data)

        assert entry.duration == 1.5

    def test_from_dict_with_custom_fields(self) -> None:
        """Test creating LogEntry with custom fields."""
        data = {
            "task_uuid": "test-uuid",
            "timestamp": 1738332000.0,
            "level": "/",
            "message_type": "loggerx:info",
            "user_id": 12345,
            "request_id": "req-001",
        }

        entry = LogEntry.from_dict(data)

        assert entry.get("user_id") == 12345
        assert entry.get("request_id") == "req-001"
        assert entry.fields["user_id"] == 12345

    def test_level_property(self) -> None:
        """Test level property from message type."""
        data = {
            "task_uuid": "test-uuid",
            "timestamp": 1738332000.0,
            "level": "/",
            "message_type": "loggerx:info",
        }

        entry = LogEntry.from_dict(data)
        assert entry.level == Level.INFO

    def test_is_error_property(self) -> None:
        """Test is_error property."""
        error_data = {
            "task_uuid": "test-uuid",
            "timestamp": 1738332000.0,
            "level": "/",
            "message_type": "loggerx:error",
        }
        error_entry = LogEntry.from_dict(error_data)

        info_data = {
            "task_uuid": "test-uuid",
            "timestamp": 1738332000.0,
            "level": "/",
            "message_type": "loggerx:info",
        }
        info_entry = LogEntry.from_dict(info_data)

        assert error_entry.is_error is True
        assert info_entry.is_error is False

    def test_to_dict(self) -> None:
        """Test converting LogEntry back to dictionary."""
        data = {
            "task_uuid": "test-uuid",
            "timestamp": 1738332000.0,
            "level": "/",
            "message_type": "loggerx:info",
            "message": "Test message",
            "user_id": 12345,
        }

        entry = LogEntry.from_dict(data)
        result = entry.to_dict()

        assert result["task_uuid"] == "test-uuid"
        assert result["message"] == "Test message"
        assert result["user_id"] == 12345

    def test_string_representation(self) -> None:
        """Test string representation of LogEntry."""
        data = {
            "task_uuid": "test-uuid",
            "timestamp": 1738332000.0,
            "level": "/",
            "message_type": "loggerx:error",
            "message": "Error occurred",
        }

        entry = LogEntry.from_dict(data)
        str_repr = str(entry)

        assert "ERROR" in str_repr
        assert "Error occurred" in str_repr

    def test_immutability(self) -> None:
        """Test that LogEntry is immutable."""
        from dataclasses import FrozenInstanceError

        data = {
            "task_uuid": "test-uuid",
            "timestamp": 1738332000.0,
            "level": "/",
            "message_type": "loggerx:info",
        }

        entry = LogEntry.from_dict(data)

        with pytest.raises(FrozenInstanceError):
            entry.message = "New message"  # type: ignore[misc]


class TestLogParser:
    """Tests for LogParser class."""

    def test_parse_from_file(self, sample_log_path: str) -> None:
        """Test parsing from file path."""
        parser = LogParser(sample_log_path)
        entries = parser.parse()

        assert len(entries) > 0
        assert isinstance(entries[0], LogEntry)
        assert entries[0].task_uuid == "550e8400-e29b-41d4-a716-446655440000"

    def test_parse_from_list(self) -> None:
        """Test parsing from list of dicts."""
        data = [
            {
                "task_uuid": "test-uuid",
                "timestamp": 1738332000.0,
                "level": "/",
                "message_type": "loggerx:info",
                "message": "Test 1",
            },
            {
                "task_uuid": "test-uuid",
                "timestamp": 1738332001.0,
                "level": "/",
                "message_type": "loggerx:info",
                "message": "Test 2",
            },
        ]

        parser = LogParser(data)
        entries = parser.parse()

        assert len(entries) == 2
        assert entries[0].message == "Test 1"
        assert entries[1].message == "Test 2"

    def test_parse_from_file_object(self, sample_log_path: str) -> None:
        """Test parsing from file object."""
        with open(sample_log_path) as f:
            parser = LogParser(f)
            entries = parser.parse()

        assert len(entries) > 0

    def test_parse_stream(self, sample_log_path: str) -> None:
        """Test streaming parse."""
        parser = LogParser(sample_log_path)
        entries = list(parser.parse_stream())

        assert len(entries) > 0

    def test_parse_skip_malformed_lines(self, tmp_path: str) -> None:
        """Test that malformed lines are skipped."""
        import os

        log_file = os.path.join(tmp_path, "malformed.log")

        with open(log_file, "w") as f:
            f.write('{"valid": true}\n')
            f.write("invalid line\n")
            f.write('{"also": "valid"}\n')
            f.write("another invalid\n")

        parser = LogParser(log_file)
        entries = parser.parse()

        assert len(entries) == 2

    def test_parser_caching(self, sample_log_path: str) -> None:
        """Test that parse results are cached."""
        parser = LogParser(sample_log_path)

        entries1 = parser.parse()
        entries2 = parser.parse()

        # Same object returned
        assert entries1 is entries2

    def test_parser_len(self, sample_log_path: str) -> None:
        """Test getting parser length."""
        parser = LogParser(sample_log_path)

        count = len(parser)
        entries = parser.parse()

        assert count == len(entries)
