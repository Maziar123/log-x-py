"""
Tree functionality for logxy-log-parser.

Contains TaskNode and TaskTree for hierarchical task representation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .core import LogEntry
from .types import ActionStatus


@dataclass
class TaskNode:
    """Node in task tree."""

    task_uuid: str
    task_level: tuple[int, ...]
    action_type: str | None
    status: ActionStatus | None
    start_time: float | None
    end_time: float | None
    duration: float | None
    children: list[TaskNode] = field(default_factory=list)
    messages: list[LogEntry] = field(default_factory=list)

    @property
    def depth(self) -> int:
        """Get the depth of this node in the tree."""
        return len(self.task_level)

    @property
    def is_complete(self) -> bool:
        """Check if this node has completed (has end time)."""
        return self.end_time is not None

    @property
    def total_duration(self) -> float:
        """Get total duration including all children."""
        if self.duration is not None:
            return self.duration

        if self.children:
            child_durations = [c.total_duration for c in self.children if c.total_duration]
            if child_durations:
                return max(child_durations)

        return 0.0

    def find_child(self, task_level: tuple[int, ...]) -> TaskNode | None:
        """Find a child node by task level.

        Args:
            task_level: Task level to find.

        Returns:
            TaskNode | None: Child node or None.
        """
        for child in self.children:
            if child.task_level == task_level:
                return child
        return None

    def add_child(self, node: TaskNode) -> None:
        """Add a child node.

        Args:
            node: Child node to add.
        """
        self.children.append(node)

    def add_message(self, message: LogEntry) -> None:
        """Add a message to this node.

        Args:
            message: LogEntry message to add.
        """
        self.messages.append(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary.

        Returns:
            dict[str, Any]: Dictionary representation.
        """
        return {
            "task_uuid": self.task_uuid,
            "task_level": self.task_level,
            "action_type": self.action_type,
            "status": self.status.value if self.status else None,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "children": [c.to_dict() for c in self.children],
            "messages": [m.to_dict() for m in self.messages],
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"TaskNode(level={self.task_level}, action={self.action_type}, status={self.status})"


class TaskTree:
    """Hierarchical tree of actions for a task_uuid."""

    def __init__(self, root: TaskNode):
        """Initialize with root node.

        Args:
            root: Root node of the tree.
        """
        self._root = root

    @classmethod
    def from_entries(cls, entries: list[LogEntry], task_uuid: str) -> TaskTree:
        """Build tree from log entries.

        Args:
            entries: List of log entries.
            task_uuid: Task UUID to build tree for.

        Returns:
            TaskTree: Built task tree.
        """
        # Filter entries for this task
        task_entries = [e for e in entries if e.task_uuid == task_uuid]

        if not task_entries:
            raise ValueError(f"No entries found for task_uuid: {task_uuid}")

        # Sort by timestamp
        task_entries.sort(key=lambda e: e.timestamp)

        # Create root node (first action)
        first_entry = task_entries[0]
        root = TaskNode(
            task_uuid=task_uuid,
            task_level=first_entry.task_level,
            action_type=first_entry.action_type,
            status=first_entry.action_status,
            start_time=first_entry.timestamp,
            end_time=first_entry.timestamp if first_entry.duration else None,
            duration=first_entry.duration,
        )

        # Track nodes by task level
        nodes: dict[tuple[int, ...], TaskNode] = {first_entry.task_level: root}

        # Process remaining entries
        for entry in task_entries[1:]:
            if entry.is_action:
                # Create or update action node
                node = nodes.get(entry.task_level)

                if node is None:
                    # Create new node
                    node = TaskNode(
                        task_uuid=task_uuid,
                        task_level=entry.task_level,
                        action_type=entry.action_type,
                        status=entry.action_status,
                        start_time=entry.timestamp,
                        end_time=entry.timestamp if entry.duration else None,
                        duration=entry.duration,
                    )

                    # Find parent and add child
                    parent_level = entry.task_level[:-1]
                    parent = nodes.get(parent_level, root)
                    parent.add_child(node)

                    nodes[entry.task_level] = node
                else:
                    # Update existing node
                    if entry.action_status == ActionStatus.STARTED:
                        node.start_time = entry.timestamp
                    elif entry.action_status in (ActionStatus.SUCCEEDED, ActionStatus.FAILED):
                        node.end_time = entry.timestamp
                        node.status = entry.action_status
                        if entry.duration:
                            node.duration = entry.duration
            else:
                # Add message to appropriate node
                # Find the deepest node that was active at this time
                target_level = entry.task_level
                while target_level not in nodes and len(target_level) > 1:
                    target_level = target_level[:-1]

                if target_level in nodes:
                    nodes[target_level].add_message(entry)

        return cls(root)

    @property
    def root(self) -> TaskNode:
        """Get the root node."""
        return self._root

    def find_node(self, task_level: tuple[int, ...]) -> TaskNode | None:
        """Find a node by task level.

        Args:
            task_level: Task level to find.

        Returns:
            TaskNode | None: Node or None.
        """
        # BFS search
        queue = [self._root]

        while queue:
            node = queue.pop(0)

            if node.task_level == task_level:
                return node

            queue.extend(node.children)

        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert tree to dictionary.

        Returns:
            dict[str, Any]: Dictionary representation.
        """
        return self._root.to_dict()

    def visualize(self, viz_format: str = "ascii") -> str:
        """Visualize the tree.

        Args:
            format: Visualization format ("ascii", "text").

        Returns:
            str: Visualized tree.
        """
        if viz_format == "ascii":
            return self._visualize_ascii()
        else:
            return self._visualize_text()

    def _visualize_ascii(self) -> str:
        """Create ASCII tree visualization.

        Returns:
            str: ASCII tree.
        """
        lines: list[str] = []
        self._visualize_node(self._root, lines, "", True)

        return "\n".join(lines)

    def _visualize_node(
        self, node: TaskNode, lines: list[str], prefix: str, is_last: bool
    ) -> None:
        """Visualize a node recursively.

        Args:
            node: Node to visualize.
            lines: List to append lines to.
            prefix: Prefix for indentation.
            is_last: Whether this is the last child.
        """
        # Build node label
        action = node.action_type or "root"
        status = f" [{node.status.value}]" if node.status else ""
        duration = f" ({node.duration:.3f}s)" if node.duration else ""

        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{action}{status}{duration}")

        # Build prefix for children
        child_prefix = prefix + ("    " if is_last else "│   ")

        # Visualize children
        for i, child in enumerate(node.children):
            self._visualize_node(child, lines, child_prefix, i == len(node.children) - 1)

        # Visualize messages
        if node.messages:
            msg_prefix = prefix + ("    " if is_last else "│   ")
            for msg in node.messages:
                msg_text = msg.message or ""
                lines.append(f"{msg_prefix}└── 💬 {msg_text[:50]}{'...' if len(msg_text) > 50 else ''}")

    def _visualize_text(self) -> str:
        """Create simple text tree visualization.

        Returns:
            str: Text tree.
        """
        lines: list[str] = []
        self._visualize_node_text(self._root, lines, 0)

        return "\n".join(lines)

    def _visualize_node_text(self, node: TaskNode, lines: list[str], depth: int) -> None:
        """Visualize a node recursively with indentation.

        Args:
            node: Node to visualize.
            lines: List to append lines to.
            depth: Current depth.
        """
        indent = "  " * depth
        action = node.action_type or "root"
        status = f" [{node.status.value}]" if node.status else ""
        duration = f" ({node.duration:.3f}s)" if node.duration else ""

        lines.append(f"{indent}{action}{status}{duration}")

        # Visualize children
        for child in node.children:
            self._visualize_node_text(child, lines, depth + 1)

        # Visualize messages
        for msg in node.messages:
            msg_text = msg.message or ""
            lines.append(f"{indent}  💬 {msg_text[:50]}{'...' if len(msg_text) > 50 else ''}")

    def get_execution_path(self) -> list[str]:
        """Get the execution path (action types from root to deepest leaf).

        Returns:
            list[str]: List of action types.
        """
        path: list[str] = []

        def traverse(node: TaskNode) -> None:
            if node.action_type:
                path.append(node.action_type)

            if node.children:
                # Go to the last child (deepest path)
                traverse(node.children[-1])

        traverse(self._root)
        return path

    def get_all_paths(self) -> list[list[str]]:
        """Get all execution paths through the tree.

        Returns:
            list[list[str]]: List of paths.
        """
        paths: list[list[str]] = []

        def traverse(node: TaskNode, current: list[str]) -> None:
            if node.action_type:
                current.append(node.action_type)

            if not node.children:
                paths.append(current.copy())
            else:
                for child in node.children:
                    traverse(child, current)
                    current.pop()

        traverse(self._root, [])
        return paths

    def deepest_nesting(self) -> int:
        """Get the maximum nesting depth in the tree.

        Returns:
            int: Maximum nesting depth.
        """
        max_depth = 0

        def traverse(node: TaskNode, depth: int) -> None:
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            for child in node.children:
                traverse(child, depth + 1)

        traverse(self._root, 0)
        return max_depth

    def get_stats(self) -> dict[str, Any]:
        """Get tree statistics.

        Returns:
            dict[str, Any]: Tree statistics.
        """
        total_nodes = 0
        total_messages = 0
        max_depth = 0
        completed = 0
        failed = 0

        def count(node: TaskNode, depth: int) -> None:
            nonlocal total_nodes, total_messages, max_depth, completed, failed

            total_nodes += 1
            total_messages += len(node.messages)
            max_depth = max(max_depth, depth)

            if node.status == ActionStatus.SUCCEEDED:
                completed += 1
            elif node.status == ActionStatus.FAILED:
                failed += 1

            for child in node.children:
                count(child, depth + 1)

        count(self._root, 0)

        return {
            "total_nodes": total_nodes,
            "total_messages": total_messages,
            "max_depth": max_depth,
            "completed": completed,
            "failed": failed,
            "total_duration": self._root.total_duration,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"TaskTree(uuid={self._root.task_uuid}, nodes={self.get_stats()['total_nodes']})"
