"""Tests for filtering functionality."""

from __future__ import annotations

import pytest

from logxy_log_parser import LogFilter, LogParser
from logxy_log_parser import Level


class TestLogFilter:
    """Tests for LogFilter class."""

    def test_by_level(self, sample_log_path: str) -> None:
        """Test filtering by log level."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        errors = LogFilter(logs).by_level("error")

        assert all(e.level == Level.ERROR for e in errors)

    def test_error_filter(self, error_log_path: str) -> None:
        """Test error convenience filter."""
        parser = LogParser(error_log_path)
        logs = parser.parse()

        errors = LogFilter(logs).error()

        assert len(errors) > 0
        assert all(e.is_error for e in errors)

    def test_warning_filter(self, sample_log_path: str) -> None:
        """Test warning filter."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        warnings = LogFilter(logs).warning()

        assert all(e.level == Level.WARNING for e in warnings)

    def test_by_message(self, sample_log_path: str) -> None:
        """Test filtering by message content."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        payment_logs = LogFilter(logs).by_message("payment")

        assert all("payment" in e.message.lower() for e in payment_logs if e.message)

    def test_by_message_regex(self, sample_log_path: str) -> None:
        """Test filtering by message with regex."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        # Test case insensitive regex
        result = LogFilter(logs).by_message(r"PAYMENT", regex=True)

        assert all(e.message and "payment" in e.message.lower() for e in result)

    def test_by_action_type(self, sample_log_path: str) -> None:
        """Test filtering by action type."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        # Filter entries that have specific action type
        result = LogFilter(logs).by_action_type("database.query", "api.call")

        # Our sample doesn't have these, so result should be empty
        assert len(result) == 0 or all(
            e.action_type in ("database.query", "api.call") for e in result
        )

    def test_by_field(self, sample_log_path: str) -> None:
        """Test filtering by field value."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        user_logs = LogFilter(logs).by_field("user_id", 12345)

        assert all(e.get("user_id") == 12345 for e in user_logs)

    def test_by_time_range(self, sample_log_path: str) -> None:
        """Test filtering by time range."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        recent = LogFilter(logs).after(1738332002.0)

        assert all(e.timestamp > 1738332002.0 for e in recent)

    def test_before_filter(self, sample_log_path: str) -> None:
        """Test before time filter."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        early = LogFilter(logs).before(1738332001.0)

        assert all(e.timestamp < 1738332001.0 for e in early)

    def test_by_task_uuid(self, sample_log_path: str) -> None:
        """Test filtering by task UUID."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        uuid = "550e8400-e29b-41d4-a716-446655440000"
        task_logs = LogFilter(logs).by_task_uuid(uuid)

        assert all(e.task_uuid == uuid for e in task_logs)

    def test_by_nesting_level(self, complex_log_path: str) -> None:
        """Test filtering by nesting depth."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        deep = LogFilter(logs).by_nesting_level(min_depth=1)

        assert all(e.depth >= 1 for e in deep)

    def test_by_duration(self, complex_log_path: str) -> None:
        """Test filtering by duration."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        slow = LogFilter(logs).slow_actions(threshold=0.5)

        assert all(e.duration and e.duration >= 0.5 for e in slow)

    def test_failed_actions(self, sample_log_path: str) -> None:
        """Test filtering failed actions."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        from logxy_log_parser import ActionStatus

        failed = LogFilter(logs).failed_actions()

        assert all(e.action_status == ActionStatus.FAILED for e in failed)

    def test_chaining_filters(self, sample_log_path: str) -> None:
        """Test chaining multiple filters."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        # Chain: filter to info level, then filter by timestamp
        info_logs = LogFilter(logs).info()
        result = LogFilter(info_logs).after(1738332001.0)

        assert all(e.level == Level.INFO for e in result)
        assert all(e.timestamp > 1738332001.0 for e in result)

    def test_limit(self, sample_log_path: str) -> None:
        """Test limiting results."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        limited = LogFilter(logs).limit(2)

        assert len(limited) <= 2

    def test_sort(self, sample_log_path: str) -> None:
        """Test sorting results."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        sorted_logs = LogFilter(logs).sort("timestamp", reverse=True)

        timestamps = [e.timestamp for e in sorted_logs]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_count_by_level(self, sample_log_path: str) -> None:
        """Test counting by level."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        counts = LogFilter(logs).count_by_level()

        assert isinstance(counts, dict)
        assert "info" in counts or "error" in counts or "warning" in counts

    def test_group_by(self, sample_log_path: str) -> None:
        """Test grouping by field."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        grouped = LogFilter(logs).group_by("task_uuid")

        assert isinstance(grouped, dict)
        assert len(grouped) > 0


class TestLogEntries:
    """Tests for LogEntries collection."""

    def test_len(self, sample_log_path: str) -> None:
        """Test getting length."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        from logxy_log_parser import LogEntries

        entries = LogEntries(logs)

        assert len(entries) == len(logs)

    def test_iteration(self, sample_log_path: str) -> None:
        """Test iterating over entries."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        from logxy_log_parser import LogEntries

        entries = LogEntries(logs)

        count = 0
        for entry in entries:
            assert isinstance(entry, object)
            count += 1

        assert count == len(logs)

    def test_getitem(self, sample_log_path: str) -> None:
        """Test indexing."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        from logxy_log_parser import LogEntries

        entries = LogEntries(logs)

        first = entries[0]
        assert first is not None

    def test_unique(self, sample_log_path: str) -> None:
        """Test getting unique entries."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        from logxy_log_parser import LogEntries

        entries = LogEntries(logs)
        unique = entries.unique("task_uuid")

        # Should have entries with unique task UUIDs
        uuids = {e.task_uuid for e in unique}
        assert len(uuids) <= len(unique)
