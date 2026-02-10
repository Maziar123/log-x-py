"""
Task Tracing Examples for logxy-log-parser.

This script demonstrates task tree capabilities:
1. Build task trees from log entries
2. Visualize task hierarchy
3. Get execution paths
4. Get all paths through the tree
5. Find specific nodes in the tree
6. Get tree statistics
"""

from logxy_log_parser import LogParser, LogFilter, TaskTree


def example_build_task_tree():
    """Build a task tree from log entries."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("=== Build Task Tree ===")

    # Get unique task UUIDs
    from logxy_log_parser.utils import extract_task_uuid
    task_uuids = extract_task_uuid(logs)

    print(f"Found {len(task_uuids)} unique tasks")

    # Build tree for first task
    first_uuid = list(task_uuids)[0]
    tree = TaskTree.from_entries(logs, first_uuid)

    print(f"\nTree for task {first_uuid[:8]}...")
    print(f"Root action: {tree.root.action_type}")


def example_visualize_ascii():
    """Visualize task tree in ASCII format."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("\n=== ASCII Visualization ===")

    from logxy_log_parser.utils import extract_task_uuid
    task_uuids = extract_task_uuid(logs)

    first_uuid = list(task_uuids)[0]
    tree = TaskTree.from_entries(logs, first_uuid)

    ascii_tree = tree.visualize(viz_format="ascii")
    print(ascii_tree)


def example_visualize_text():
    """Visualize task tree in text format."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("\n=== Text Visualization ===")

    from logxy_log_parser.utils import extract_task_uuid
    task_uuids = extract_task_uuid(logs)

    first_uuid = list(task_uuids)[0]
    tree = TaskTree.from_entries(logs, first_uuid)

    text_tree = tree.visualize(viz_format="text")
    print(text_tree[:500] + "...")


def example_execution_path():
    """Get the execution path through the task tree."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("\n=== Execution Path ===")

    from logxy_log_parser.utils import extract_task_uuid
    task_uuids = extract_task_uuid(logs)

    first_uuid = list(task_uuids)[0]
    tree = TaskTree.from_entries(logs, first_uuid)

    path = tree.get_execution_path()
    print(f"Execution path ({len(path)} steps):")
    for i, action in enumerate(path, 1):
        print(f"  {i}. {action}")


def example_all_paths():
    """Get all execution paths through the task tree."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    print("\n=== All Execution Paths ===")

    from logxy_log_parser.utils import extract_task_uuid
    task_uuids = extract_task_uuid(logs)

    for task_uuid in task_uuids:
        tree = TaskTree.from_entries(logs, task_uuid)
        paths = tree.get_all_paths()

        print(f"\nTask {task_uuid[:8]}... ({len(paths)} path(s)):")
        for i, path in enumerate(paths, 1):
            print(f"  Path {i}: {' -> '.join(path)}")


def example_find_node():
    """Find a specific node in the task tree."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("\n=== Find Node ===")

    from logxy_log_parser.utils import extract_task_uuid
    task_uuids = extract_task_uuid(logs)

    first_uuid = list(task_uuids)[0]
    tree = TaskTree.from_entries(logs, first_uuid)

    # Find node at level /2/2
    node = tree.find_node((2, 2))
    if node:
        print("Found node at level /2/2:")
        print(f"  Action type: {node.action_type}")
        print(f"  Status: {node.status}")
        print(f"  Duration: {node.duration}s")
        print(f"  Children: {len(node.children)}")
        print(f"  Messages: {len(node.messages)}")


def example_tree_stats():
    """Get statistics about the task tree."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("\n=== Tree Statistics ===")

    from logxy_log_parser.utils import extract_task_uuid
    task_uuids = extract_task_uuid(logs)

    first_uuid = list(task_uuids)[0]
    tree = TaskTree.from_entries(logs, first_uuid)

    stats = tree.get_stats()
    print(f"Total nodes: {stats['total_nodes']}")
    print(f"Total messages: {stats['total_messages']}")
    print(f"Max depth: {stats['max_depth']}")
    print(f"Completed nodes: {stats['completed']}")
    print(f"Failed nodes: {stats['failed']}")
    print(f"Total duration: {stats['total_duration']:.3f}s")


def example_deepest_nesting():
    """Find the deepest nesting level in the task tree."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("\n=== Deepest Nesting ===")

    from logxy_log_parser.utils import extract_task_uuid
    task_uuids = extract_task_uuid(logs)

    first_uuid = list(task_uuids)[0]
    tree = TaskTree.from_entries(logs, first_uuid)

    depth = tree.deepest_nesting()
    print(f"Deepest nesting level: {depth}")


def example_to_dict():
    """Convert task tree to dictionary."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("\n=== Tree to Dictionary ===")

    from logxy_log_parser.utils import extract_task_uuid
    task_uuids = extract_task_uuid(logs)

    first_uuid = list(task_uuids)[0]
    tree = TaskTree.from_entries(logs, first_uuid)

    tree_dict = tree.to_dict()
    print(f"Tree dictionary keys: {list(tree_dict.keys())}")
    print(f"Root action: {tree_dict['action_type']}")


def example_node_properties():
    """Access node properties."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("\n=== Node Properties ===")

    from logxy_log_parser.utils import extract_task_uuid
    task_uuids = extract_task_uuid(logs)

    first_uuid = list(task_uuids)[0]
    tree = TaskTree.from_entries(logs, first_uuid)

    root = tree.root
    print("Root node properties:")
    print(f"  Task UUID: {root.task_uuid[:8]}...")
    print(f"  Task level: {root.task_level}")
    print(f"  Action type: {root.action_type}")
    print(f"  Status: {root.status}")
    print(f"  Start time: {root.start_time}")
    print(f"  End time: {root.end_time}")
    print(f"  Duration: {root.duration}s")
    print(f"  Depth: {root.depth}")
    print(f"  Is complete: {root.is_complete}")
    print(f"  Total duration: {root.total_duration}s")
    print(f"  Children: {len(root.children)}")
    print(f"  Messages: {len(root.messages)}")


def example_traverse_tree():
    """Traverse the task tree manually."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()

    print("\n=== Manual Tree Traversal ===")

    from logxy_log_parser.utils import extract_task_uuid
    task_uuids = extract_task_uuid(logs)

    first_uuid = list(task_uuids)[0]
    tree = TaskTree.from_entries(logs, first_uuid)

    def traverse(node, depth=0):
        """Recursively traverse tree."""
        indent = "  " * depth
        print(f"{indent}{node.action_type} ({node.status})")
        for child in node.children:
            traverse(child, depth + 1)

    traverse(tree.root)


def example_filter_by_task():
    """Filter logs by task UUID and build tree."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()

    print("\n=== Filter by Task and Build Tree ===")

    from logxy_log_parser.utils import extract_task_uuid
    task_uuids = extract_task_uuid(logs)

    print(f"Found {len(task_uuids)} tasks")

    for task_uuid in task_uuids:
        # Filter logs for this task
        task_logs = LogFilter(logs).by_task_uuid(task_uuid)

        # Build tree
        tree = TaskTree.from_entries(task_logs, task_uuid)

        print(f"\nTask {task_uuid[:8]}...:")
        print(f"  Entries: {len(task_logs)}")
        print(f"  Root action: {tree.root.action_type}")
        print(f"  Max depth: {tree.deepest_nesting()}")


def main():
    """Run all examples."""
    example_build_task_tree()
    example_visualize_ascii()
    example_visualize_text()
    example_execution_path()
    example_all_paths()
    example_find_node()
    example_tree_stats()
    example_deepest_nesting()
    example_to_dict()
    example_node_properties()
    example_traverse_tree()
    example_filter_by_task()


if __name__ == "__main__":
    main()
