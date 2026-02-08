"""Tests for tree functionality."""

from __future__ import annotations

import pytest

from logxy_log_parser import LogParser, TaskTree
from logxy_log_parser.types import ActionStatus


class TestTaskTree:
    """Tests for TaskTree class."""

    def test_from_entries(self, complex_log_path: str) -> None:
        """Test building tree from entries."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        task_uuid = logs[0].task_uuid
        tree = TaskTree.from_entries(logs, task_uuid)

        assert tree is not None
        assert tree.root.task_uuid == task_uuid

    def test_from_entries_invalid_uuid(self, sample_log_path: str) -> None:
        """Test building tree with invalid UUID raises error."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        with pytest.raises(ValueError):
            TaskTree.from_entries(logs, "invalid-uuid")

    def test_root_property(self, complex_log_path: str) -> None:
        """Test getting root node."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        task_uuid = logs[0].task_uuid
        tree = TaskTree.from_entries(logs, task_uuid)

        root = tree.root
        assert root is not None
        assert root.task_uuid == task_uuid

    def test_find_node(self, complex_log_path: str) -> None:
        """Test finding a node by task level."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        task_uuid = logs[0].task_uuid
        tree = TaskTree.from_entries(logs, task_uuid)

        # The root node should exist - check it directly
        root = tree.root
        assert root is not None
        assert root.task_uuid == task_uuid

        # find_node searches by node's task_level, which is the entry's task_level
        # For root action, this is the first action's entry task_level
        first_action = next(e for e in logs if e.is_action)
        found = tree.find_node(first_action.task_level)
        assert found is not None

    def test_deepest_nesting(self, complex_log_path: str) -> None:
        """Test getting deepest nesting level."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        task_uuid = logs[0].task_uuid
        tree = TaskTree.from_entries(logs, task_uuid)

        deepest = tree.deepest_nesting()
        assert deepest >= 0

    def test_visualize_ascii(self, complex_log_path: str) -> None:
        """Test ASCII visualization."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        task_uuid = logs[0].task_uuid
        tree = TaskTree.from_entries(logs, task_uuid)

        viz = tree.visualize("ascii")

        assert isinstance(viz, str)
        assert len(viz) > 0

    def test_visualize_text(self, complex_log_path: str) -> None:
        """Test text visualization."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        task_uuid = logs[0].task_uuid
        tree = TaskTree.from_entries(logs, task_uuid)

        viz = tree.visualize("text")

        assert isinstance(viz, str)
        assert len(viz) > 0

    def test_get_stats(self, complex_log_path: str) -> None:
        """Test getting tree statistics."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        task_uuid = logs[0].task_uuid
        tree = TaskTree.from_entries(logs, task_uuid)

        stats = tree.get_stats()

        assert "total_nodes" in stats
        assert "max_depth" in stats
        assert "total_duration" in stats
        assert stats["total_nodes"] > 0

    def test_to_dict(self, complex_log_path: str) -> None:
        """Test converting tree to dictionary."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        task_uuid = logs[0].task_uuid
        tree = TaskTree.from_entries(logs, task_uuid)

        data = tree.to_dict()

        assert isinstance(data, dict)
        assert "task_uuid" in data
        assert "children" in data


class TestTaskNode:
    """Tests for TaskNode class."""

    def test_depth_property(self, complex_log_path: str) -> None:
        """Test node depth property."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        task_uuid = logs[0].task_uuid
        tree = TaskTree.from_entries(logs, task_uuid)

        root = tree.root
        assert root.depth == len(root.task_level)

    def test_is_complete_property(self, complex_log_path: str) -> None:
        """Test is_complete property."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        task_uuid = logs[0].task_uuid
        tree = TaskTree.from_entries(logs, task_uuid)

        # Find a completed node
        for node in [tree.root]:
            if node.end_time:
                assert node.is_complete is True

    def test_total_duration_property(self, complex_log_path: str) -> None:
        """Test total_duration property."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        task_uuid = logs[0].task_uuid
        tree = TaskTree.from_entries(logs, task_uuid)

        duration = tree.root.total_duration
        assert duration >= 0

    def test_find_child(self, complex_log_path: str) -> None:
        """Test finding child node."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        task_uuid = logs[0].task_uuid
        tree = TaskTree.from_entries(logs, task_uuid)

        if tree.root.children:
            first_child = tree.root.children[0]
            found = tree.root.find_child(first_child.task_level)
            assert found is not None

    def test_add_child(self) -> None:
        """Test adding child node."""
        from logxy_log_parser.tree import TaskNode

        parent = TaskNode(
            task_uuid="test",
            task_level=(),
            action_type="parent",
            status=ActionStatus.STARTED,
            start_time=0.0,
            end_time=None,
            duration=None,
        )

        child = TaskNode(
            task_uuid="test",
            task_level=(1,),
            action_type="child",
            status=ActionStatus.STARTED,
            start_time=0.0,
            end_time=None,
            duration=None,
        )

        parent.add_child(child)

        assert len(parent.children) == 1
        assert parent.children[0] is child

    def test_add_message(self) -> None:
        """Test adding message to node."""
        from logxy_log_parser.tree import TaskNode
        from logxy_log_parser import LogEntry

        node = TaskNode(
            task_uuid="test",
            task_level=(),
            action_type="action",
            status=ActionStatus.STARTED,
            start_time=0.0,
            end_time=None,
            duration=None,
        )

        entry = LogEntry(
            timestamp=1.0,
            task_uuid="test",
            task_level=(),
            message_type="loggerx:info",
            message="Test message",
            action_type=None,
            action_status=None,
            duration=None,
            fields={},
        )

        node.add_message(entry)

        assert len(node.messages) == 1
        assert node.messages[0] is entry

    def test_to_dict(self) -> None:
        """Test converting node to dictionary."""
        from logxy_log_parser.tree import TaskNode

        node = TaskNode(
            task_uuid="test",
            task_level=(),
            action_type="action",
            status=ActionStatus.STARTED,
            start_time=0.0,
            end_time=None,
            duration=None,
        )

        data = node.to_dict()

        assert data["task_uuid"] == "test"
        assert "children" in data
        assert "messages" in data
