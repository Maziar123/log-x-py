"""Tests for tree module."""

from __future__ import annotations

import pytest

from logxpy_cli_view.src.tree import Tree, _TaskNode, missing_start_task, task_name


class TestTaskName:
    """Tests for task_name function."""

    def test_none_raises(self):
        """Raises ValueError for None task."""
        with pytest.raises(ValueError):
            task_name(None)

    def test_message_type(self):
        """Extracts name from message_type."""
        task = {
            "message_type": "log",
            "task_level": [1, 2],
        }
        result = task_name(task)
        assert result == "log@1,2"

    def test_action_type(self):
        """Extracts name from action_type."""
        task = {
            "action_type": "app:action",
            "action_status": "started",
            "task_level": [1],
        }
        result = task_name(task)
        assert result == "app:action@1/started"

    def test_no_type_returns_none(self):
        """Returns None if no type found."""
        task = {"task_level": [1]}
        result = task_name(task)
        assert result is None


class TestTaskNode:
    """Tests for _TaskNode class."""

    def test_init_requires_task(self):
        """Raises ValueError for None task."""
        with pytest.raises(ValueError):
            _TaskNode(None)

    def test_repr(self, sample_task):
        """Has readable repr."""
        node = _TaskNode(sample_task)
        assert "_TaskNode" in repr(node)
        assert "cdeb220d" in repr(node)

    def test_copy(self, sample_task):
        """Copy creates independent node."""
        node = _TaskNode(sample_task)
        copied = node.copy()
        assert copied.task == node.task
        assert copied.name == node.name


class TestMissingStartTask:
    """Tests for missing_start_task function."""

    def test_creates_synthetic_task(self, sample_task):
        """Creates synthetic start task."""
        result = missing_start_task(sample_task)
        assert result["action_type"] == "<missing start task>"
        assert result["action_status"] == "started"
        assert result["task_level"] == [1]


class TestTree:
    """Tests for Tree class."""

    def test_deprecated(self):
        """Tree is deprecated."""
        with pytest.warns(DeprecationWarning):
            Tree()

    def test_empty_nodes(self):
        """Empty tree has no nodes."""
        with pytest.warns(DeprecationWarning):
            tree = Tree()
        assert tree.nodes() == []
