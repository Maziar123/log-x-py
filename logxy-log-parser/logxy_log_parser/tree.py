"""
Tree functionality for logxy-log-parser.

Contains TaskNode and TaskTree for hierarchical task representation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .core import LogEntry
from .types import ActionStatus


def _get_action_level(task_level: tuple[int, ...]) -> tuple[int, ...]:
    """Get the action level from a task level.

    In logxpy, action messages have a task_level that is one level deeper
    than the action itself. For example:
    - Action at level [3] has messages at [3,1], [3,2], etc.
    - So [3,1].parent() = [3] (the action level)

    Args:
        task_level: The task level tuple.

    Returns:
        The parent level (action level).
    """
    return task_level[:-1] if len(task_level) > 1 else tuple()


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
        """Build tree from log entries using logxpy format.

        In logxpy, the task_level works as follows:
        - Single element [1], [2], [3] are sequential top-level entries
        - Multi-element [3,1], [3,2] are children of entry at action_level [3]
        - Action entries have action_type and action_status
        - Their child messages have task_level = [action_level, index]

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

        # Sort by timestamp (logxpy outputs in order, but sort to be safe)
        task_entries.sort(key=lambda e: e.timestamp)

        # Track actions by their level (action messages are at level N,
        # their children are at level [N, 1], [N, 2], etc.)
        # We use the message's task_level to find its parent action
        actions: dict[tuple[int, ...], TaskNode] = {}
        root: TaskNode | None = None

        # First pass: collect all action start/end events
        for entry in task_entries:
            if entry.is_action:
                action_level = _get_action_level(entry.task_level)

                if action_level not in actions:
                    # Create new action node
                    node = TaskNode(
                        task_uuid=task_uuid,
                        task_level=entry.task_level,
                        action_type=entry.action_type,
                        status=entry.action_status,
                        start_time=entry.timestamp,
                        end_time=entry.timestamp if entry.duration else None,
                        duration=entry.duration,
                    )
                    actions[action_level] = node

                    # Track root (empty tuple action_level means root)
                    if len(action_level) == 0:
                        root = node
                else:
                    # Update existing action
                    node = actions[action_level]
                    if entry.action_status == ActionStatus.STARTED:
                        if node.start_time is None:
                            node.start_time = entry.timestamp
                    elif entry.action_status in (ActionStatus.SUCCEEDED, ActionStatus.FAILED):
                        node.end_time = entry.timestamp
                        node.status = entry.action_status
                        if entry.duration is not None:
                            node.duration = entry.duration

        # If no actions found, create a synthetic root from the first message
        if root is None:
            if task_entries:
                first = task_entries[0]
                root = TaskNode(
                    task_uuid=task_uuid,
                    task_level=first.task_level,
                    action_type=first.action_type or "message",
                    status=first.action_status,
                    start_time=first.timestamp,
                    end_time=first.timestamp,
                    duration=first.duration,
                )
                # Add all messages as children of root
                for entry in task_entries:
                    root.add_message(entry)
            else:
                raise ValueError(f"No entries found for task_uuid: {task_uuid}")

        # Second pass: build parent-child relationships
        # A child action has action_level that is a suffix of a parent's children
        # E.g., if parent action has children at [3,1], [3,2]
        # then [3,1, 1] would be a child of action at [3,1]
        for action_level, node in sorted(actions.items(), key=lambda x: len(x[0])):
            if action_level == ():
                continue  # Skip root

            # Find parent: parent is the action whose children would have
            # task_levels starting with action_level
            # In logxpy, if this action is at level [3], its messages are [3,1], [3,2]
            # A nested action would have messages like [3,1, 1], so its action_level is [3,1]
            parent_level = action_level[:-1] if len(action_level) > 1 else ()

            if parent_level in actions:
                actions[parent_level].add_child(node)
            else:
                # If no parent found, attach to root
                root.add_child(node)

        # Third pass: assign messages to actions
        for entry in task_entries:
            if not entry.is_action:
                # Find parent action for this message
                # The message's task_level parent gives us the action level
                action_level = _get_action_level(entry.task_level)

                if action_level in actions:
                    actions[action_level].add_message(entry)
                elif root is not None:
                    # Attach to root if no specific action found
                    root.add_message(entry)

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
                # Use message_type if message is not available
                msg_text = msg.message or msg.message_type or ""
                if not msg_text and msg.fields:
                    # Show field names if no text
                    msg_text = f"fields: {', '.join(list(msg.fields.keys())[:3])}"
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
            # Use message_type if message is not available
            msg_text = msg.message or msg.message_type or ""
            if not msg_text and msg.fields:
                # Show field names if no text
                msg_text = f"fields: {', '.join(list(msg.fields.keys())[:3])}"
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
