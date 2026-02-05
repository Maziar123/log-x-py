"""Deprecated tree module for eliot-tree.

This module is deprecated. Use eliottree.tasks_from_iterable instead.
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any, ClassVar

from logxpy_cli_view._compat import deprecated


def task_name(task: dict[str, Any] | None) -> str | None:
    """
    Compute the task name for an Eliot task.

    Args:
        task: Eliot task dictionary

    Returns:
        Task name or None if name cannot be determined

    Raises:
        ValueError: If task is None
    """
    if task is None:
        raise ValueError("Cannot compute task name", task)

    level = ",".join(map(str, task["task_level"]))
    message_type = task.get("message_type")

    if message_type is not None:
        status = ""
    else:
        message_type = task.get("action_type")
        if message_type is None:
            return None
        status = "/" + task["action_status"]

    return f"{message_type}@{level}{status}"


@dataclass(slots=True)
class _TaskNode:
    """
    A node representing an Eliot task and its child tasks.
    """

    task: dict[str, Any]
    name: str | None = None
    _children: dict[int, _TaskNode] = field(default_factory=dict, repr=False)
    success: bool | None = field(default=None, init=False)

    _DEFAULT_TASK_NAME: ClassVar[str] = "<UNNAMED TASK>"

    def __post_init__(self) -> None:
        if self.task is None:
            raise ValueError("Missing logxpy task")
        if self.name is None:
            self.name = task_name(self.task) or self._DEFAULT_TASK_NAME

    def __repr__(self) -> str:
        """Human-readable representation of the node."""
        return (
            f"<{type(self).__name__} {self.task['task_uuid']!r} "
            f"{self.name!r} children={len(self._children)}>"
        )

    @property
    def task_uuid(self) -> str:
        """Get task UUID."""
        return self.task["task_uuid"]

    @property
    def is_root(self) -> bool:
        """Check if this is a root node (task_level == [1])."""
        return self.task.get("task_level") == [1]

    @property
    def child_count(self) -> int:
        """Get number of children."""
        return len(self._children)

    @property
    def children(self) -> list[_TaskNode]:
        """Get sorted list of child nodes."""
        return sorted(self._children.values(), key=lambda n: n.task["task_level"])

    def copy(self) -> _TaskNode:
        """Make a shallow copy of this node."""
        return _TaskNode(self.task, self.name)

    def add_child(self, node: _TaskNode) -> None:
        """
        Add a child node.

        Args:
            node: Child node to add to the tree
        """
        def _add_child(parent: _TaskNode, levels: list[int]) -> None:
            levels = list(levels)
            level = levels.pop(0)
            children = parent._children
            if level in children:
                _add_child(children[level], levels)
            else:
                children[level] = node
                action_status = node.task.get("action_status")
                if action_status == "succeeded":
                    node.success = parent.success = True
                elif action_status == "failed":
                    node.success = parent.success = False

        _add_child(self, node.task["task_level"])


def missing_start_task(task_missing_parent: dict[str, Any]) -> dict[str, Any]:
    """
    Create a fake start task for an existing task that happens to be missing one.

    Args:
        task_missing_parent: Task missing its parent

    Returns:
        Synthetic start task
    """
    return {
        "action_type": "<missing start task>",
        "action_status": "started",
        "timestamp": task_missing_parent["timestamp"],
        "task_uuid": task_missing_parent["task_uuid"],
        "task_level": [1],
    }


class TaskMergeError(RuntimeError):
    """An exception occurred while trying to merge a task into the tree."""

    def __init__(self, task: dict[str, Any], exc_info: Any):
        self.task = task
        self.exc_info = exc_info
        super().__init__()


@deprecated("Tree is deprecated, use eliottree.tasks_from_iterable instead")
class Tree:
    """
    Eliot task tree.

    Deprecated: Use eliottree.tasks_from_iterable instead.
    """

    def __init__(self):
        self._nodes: dict[str, _TaskNode] = {}

    def nodes(self, uuids: set[str] | None = None) -> list[tuple[str, _TaskNode]]:
        """
        All top-level nodes in the tree.

        Args:
            uuids: Set of task UUIDs to include, or None for no filtering

        Returns:
            List of (uuid, node) tuples sorted by timestamp
        """
        if uuids is not None:
            nodes = ((k, self._nodes[k]) for k in uuids)
        else:
            nodes = self._nodes.items()
        return sorted(nodes, key=lambda x: x[1].task["timestamp"])

    def merge_tasks(
        self,
        tasks: Iterable[dict[str, Any]],
        filter_funcs: Iterable[Callable[[dict[str, Any]], bool]] | None = None,
    ) -> set[str] | None:
        """
        Merge tasks into the tree.

        Args:
            tasks: Iterable of task dicts
            filter_funcs: Iterable of predicate functions

        Returns:
            Set of task UUIDs that match all filters, or None
        """
        tasktree = self._nodes
        filter_funcs = list(filter_funcs) if filter_funcs else []
        matches = {i: set() for i, _ in enumerate(filter_funcs)}

        def _merge_one(
            task: dict[str, Any], create_missing_tasks: bool
        ) -> dict[str, Any] | None:
            key = task["task_uuid"]
            node = tasktree.get(key)
            if node is None:
                if task["task_level"] != [1]:
                    if create_missing_tasks:
                        n = tasktree[key] = _TaskNode(task=missing_start_task(task))
                        n.add_child(_TaskNode(task))
                    else:
                        return task
                else:
                    node = tasktree[key] = _TaskNode(task=task)
            else:
                node.add_child(_TaskNode(task))
            for i, fn in enumerate(filter_funcs):
                if fn(task):
                    matches[i].add(key)
            return None

        def _merge(
            tasks: Iterable[dict[str, Any]], create_missing_tasks: bool = False
        ) -> list[dict[str, Any]]:
            pending = []
            for task in tasks:
                try:
                    result = _merge_one(task, create_missing_tasks)
                    if result is not None:
                        pending.append(result)
                except Exception:
                    raise TaskMergeError(task, sys.exc_info())
            return pending

        pending = _merge(tasks)
        if pending:
            pending = _merge(pending, True)
            if pending:
                raise RuntimeError("Some tasks have no start parent", pending)

        if not matches:
            return None
        return set.intersection(*matches.values())


__all__ = ["TaskMergeError", "Tree", "_TaskNode", "missing_start_task", "task_name"]
