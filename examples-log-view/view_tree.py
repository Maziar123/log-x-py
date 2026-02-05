#!/usr/bin/env python3
"""
Modern Tree Viewer for Eliot Logs using Python 3.12+ features.

Features:
- 🎨 Beautiful color-coded output with rich ANSI support
- 😊 Emoji support for quick visual scanning
- 📊 Clean, minimal, professional design
- 🌲 Enhanced deep nesting visualization
- ⚡ Fast rendering, zero external dependencies
- 🚀 Python 3.12+ features for optimal performance
"""

import json
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

type LogEntry = dict[str, Any]
type TaskUUID = str
type TreeNode = dict[str, Any]


class Color(StrEnum):
    """ANSI color codes using modern StrEnum."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    # Standard colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


@dataclass(slots=True, frozen=True)
class Colors:
    """Color scheme manager with zero overhead."""

    enabled: bool = True

    def get(self, color: Color) -> str:
        """Get color code if enabled."""
        return color.value if self.enabled else ""

    def __getitem__(self, color: Color) -> str:
        """Allow dict-style access."""
        return self.get(color)


class EmojiIcon(StrEnum):
    """Emoji indicators using modern StrEnum."""

    # Status
    SUCCEEDED = "✔️"
    FAILED = "✖️"
    STARTED = "▶️"
    # Types
    ACTION = "⚡"
    MESSAGE = "💬"
    ERROR = "🔥"
    DATABASE = "💾"
    NETWORK = "🌐"
    AUTH = "🔐"
    PAYMENT = "💳"
    SERVER = "🖥️"
    API = "🔌"
    PIPELINE = "🔄"
    # Misc
    DURATION = "⏱️"
    TREE = "🌲"


@dataclass(slots=True, frozen=True)
class Emoji:
    """Emoji manager with smart icon detection."""

    enabled: bool = True

    def get(self, icon: EmojiIcon) -> str:
        """Get emoji if enabled."""
        return icon.value if self.enabled else ""

    def get_icon(self, action_type: str) -> str:
        """Get emoji icon based on action type using pattern matching."""
        if not self.enabled:
            return ""

        lower = action_type.lower()
        match lower:
            case s if "database" in s or "db:" in s or "query" in s:
                return EmojiIcon.DATABASE
            case s if "http" in s or "request" in s or "api" in s:
                return EmojiIcon.API
            case s if "auth" in s or "login" in s:
                return EmojiIcon.AUTH
            case s if "payment" in s or "charge" in s:
                return EmojiIcon.PAYMENT
            case s if "server" in s:
                return EmojiIcon.SERVER
            case s if "pipeline" in s or "etl" in s:
                return EmojiIcon.PIPELINE
            case s if "error" in s or "fail" in s:
                return EmojiIcon.ERROR
            case s if "network" in s or "connect" in s:
                return EmojiIcon.NETWORK
            case _:
                return EmojiIcon.ACTION


@dataclass(slots=True)
class TreeChars:
    """Tree drawing characters."""

    fork: str = "├── "
    last: str = "└── "
    vertical: str = "│   "
    space: str = "    "
    thin_vertical: str = "┆   "
    arrow: str = "⇒ "
    separator: str = "─" * 70

    @classmethod
    def ascii(cls) -> "TreeChars":
        """Create ASCII-only character set."""
        return cls(
            fork="|-- ",
            last="+-- ",
            vertical="|   ",
            space="    ",
            thin_vertical="|   ",
            arrow="=> ",
            separator="-" * 70,
        )


@dataclass(slots=True)
class SimpleTreeRenderer:
    """Modern tree renderer with Python 3.12+ optimizations."""

    ascii_mode: bool = False
    use_colors: bool = True
    use_emojis: bool = True
    depth_limit: int | None = None

    # Auto-initialized fields
    colors: Colors = field(init=False)
    emoji: Emoji = field(init=False)
    chars: TreeChars = field(init=False)
    depth_colors: tuple[Color, ...] = field(init=False)

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        self.colors = Colors(enabled=self.use_colors and not self.ascii_mode)
        self.emoji = Emoji(enabled=self.use_emojis and not self.ascii_mode)
        self.chars = TreeChars.ascii() if self.ascii_mode else TreeChars()
        self.depth_colors = (
            Color.CYAN,
            Color.BLUE,
            Color.MAGENTA,
            Color.GREEN,
            Color.YELLOW,
        )

    def format_timestamp(self, ts: float) -> str:
        """Format timestamp in compact format."""
        return datetime.fromtimestamp(ts).strftime("%H:%M:%S")

    def format_duration(self, seconds: float) -> str:
        """Format duration with smart color coding."""
        c = self.colors
        match seconds:
            case s if s < 0.001:
                return f"{c[Color.DIM]}< 1ms{c[Color.RESET]}"
            case s if s < 1:
                return f"{c[Color.BRIGHT_CYAN]}{s * 1000:.0f}ms{c[Color.RESET]}"
            case s if s < 60:
                return f"{c[Color.CYAN]}{s:.2f}s{c[Color.RESET]}"
            case s:
                mins, secs = divmod(s, 60)
                return f"{c[Color.CYAN]}{int(mins)}m {secs:.1f}s{c[Color.RESET]}"

    def format_status(self, status: str) -> str:
        """Format action status with pattern matching."""
        c, e = self.colors, self.emoji
        match status:
            case "started":
                icon = e.get(EmojiIcon.STARTED)
                return f"{c[Color.BRIGHT_BLUE]}{icon}{' ' if icon else ''}{status}{c[Color.RESET]}"
            case "succeeded":
                icon = e.get(EmojiIcon.SUCCEEDED)
                return f"{c[Color.BRIGHT_GREEN]}{icon}{' ' if icon else ''}{status}{c[Color.RESET]}"
            case "failed":
                icon = e.get(EmojiIcon.FAILED)
                return f"{c[Color.BRIGHT_RED]}{icon}{' ' if icon else ''}{status}{c[Color.RESET]}"
            case _:
                return f"{c[Color.WHITE]}{status}{c[Color.RESET]}"

    def get_depth_color(self, depth: int) -> str:
        """Get color for nesting depth."""
        return self.colors[self.depth_colors[depth % len(self.depth_colors)]]

    def get_connector(self, depth: int) -> str:
        """Get connector style based on depth."""
        return self.chars.thin_vertical if depth > 4 else self.chars.vertical

    def group_by_task(self, log_entries: Iterable[LogEntry]) -> dict[TaskUUID, list[LogEntry]]:
        """Group log entries by task_uuid using modern dict comprehension."""
        tasks: dict[TaskUUID, list[LogEntry]] = {}
        for entry in log_entries:
            if task_uuid := entry.get("task_uuid"):  # Walrus operator
                tasks.setdefault(task_uuid, []).append(entry)
        return tasks

    def build_tree(self, entries: list[LogEntry]) -> list[TreeNode]:
        """Build tree structure with optimized algorithm."""
        # Sort by task_level efficiently
        sorted_entries = sorted(entries, key=lambda e: e.get("task_level", [1]))

        tree: list[TreeNode] = []
        stack: list[tuple[int, TreeNode]] = []  # Modern type hint

        for entry in sorted_entries:
            level = entry.get("task_level", [1])
            depth = len(level)

            node: TreeNode = {
                "entry": entry,
                "children": [],
                "depth": depth,
            }

            # Pop stack until finding parent level
            while stack and stack[-1][0] >= depth:
                stack.pop()

            # Add to parent or root
            (stack[-1][1]["children"] if stack else tree).append(node)
            stack.append((depth, node))

        return tree

    def render_node(self, node: TreeNode, prefix: str = "", is_last: bool = True, depth: int = 0) -> list[str]:
        """Render node with modern Python 3.12+ features."""
        entry = node["entry"]
        output: list[str] = []
        c = self.colors

        # Check depth limit
        if self.depth_limit and depth > self.depth_limit:
            connector = self.chars.last if is_last else self.chars.fork
            dc = self.get_depth_color(depth)
            output.append(f"{prefix}{dc}{connector}{c[Color.DIM]}... (depth limit){c[Color.RESET]}")
            return output

        # Extract fields with defaults
        action_type = entry.get("action_type") or entry.get("message_type") or "unknown"
        action_status = entry.get("action_status", "")
        timestamp = entry.get("timestamp")

        # Get emoji icon
        icon = self.emoji.get_icon(action_type)

        # Build node text
        task_level = entry.get("task_level", [])
        level_str = "/".join(map(str, task_level)) if task_level else "1"

        dc = self.get_depth_color(depth)
        action_colored = f"{dc}{c[Color.BOLD]}{action_type}{c[Color.RESET]}"
        level_colored = f"{c[Color.DIM]}/{level_str}{c[Color.RESET]}"

        node_text = f"{icon} {action_colored}{level_colored}" if icon else f"{action_colored}{level_colored}"

        # Add status, timestamp, duration
        if action_status:
            node_text += f" {self.chars.arrow}{self.format_status(action_status)}"
        if timestamp:
            node_text += f" {c[Color.BRIGHT_BLACK]}{self.format_timestamp(timestamp)}{c[Color.RESET]}"
        if duration := entry.get("duration"):  # Walrus operator
            dur_icon = self.emoji.get(EmojiIcon.DURATION) or "⧖"
            node_text += f" {dur_icon}{self.format_duration(duration)}"

        # Output node line
        connector = self.chars.last if is_last else self.chars.fork
        colored_connector = f"{dc}{connector}{c[Color.RESET]}" if self.colors.enabled else connector
        output.append(f"{prefix}{colored_connector}{node_text}")

        # Output fields (skip metadata keys)
        skip_keys = frozenset(
            {  # frozenset is faster for lookups
                "timestamp",
                "task_uuid",
                "task_level",
                "message_type",
                "action_type",
                "action_status",
                "duration",
            }
        )

        extension = self.chars.space if is_last else self.get_connector(depth)
        field_prefix = f"{prefix}{dc}{extension}{c[Color.RESET]}" if self.colors.enabled else f"{prefix}{extension}"

        fields = [(k, v) for k, v in entry.items() if k not in skip_keys]

        # Render fields with smart coloring
        for i, (key, value) in enumerate(fields):
            is_last_field = (i == len(fields) - 1) and not node.get("children")
            field_connector = self.chars.last if is_last_field else self.chars.fork

            # Color keys
            key_colored = f"{c[Color.BRIGHT_BLUE]}{key}{c[Color.RESET]}" if self.colors.enabled else key

            # Smart value coloring using pattern matching
            if self.colors.enabled:
                match value:
                    case int() | float():
                        value_colored = f"{c[Color.BRIGHT_CYAN]}{value}{c[Color.RESET]}"
                    case bool():
                        value_colored = f"{c[Color.BRIGHT_MAGENTA]}{value}{c[Color.RESET]}"
                    case str() if "error" in key.lower() or "fail" in key.lower():
                        value_colored = f"{c[Color.BRIGHT_RED]}{value}{c[Color.RESET]}"
                    case str() if "success" in key.lower() or "complete" in key.lower():
                        value_colored = f"{c[Color.BRIGHT_GREEN]}{value}{c[Color.RESET]}"
                    case _:
                        value_colored = f"{c[Color.WHITE]}{value}{c[Color.RESET]}"
            else:
                value_colored = str(value)

            field_line = (
                f"{field_prefix}{dc}{field_connector}{c[Color.RESET]}"
                if self.colors.enabled
                else f"{field_prefix}{field_connector}"
            )
            output.append(f"{field_line}{key_colored}: {value_colored}")

        # Render children recursively
        for i, child in enumerate(node.get("children", [])):
            is_last_child = i == len(node["children"]) - 1
            child_extension = self.chars.space if is_last else self.get_connector(depth)
            child_prefix = (
                f"{prefix}{dc}{child_extension}{c[Color.RESET]}"
                if self.colors.enabled
                else f"{prefix}{child_extension}"
            )
            output.extend(self.render_node(child, child_prefix, is_last_child, depth + 1))

        return output

    def render_header(self, log_file_name: str, total_entries: int) -> str:
        """Render modern header with efficient string building."""
        c = self.colors
        tree_icon = self.emoji.get(EmojiIcon.TREE)
        icon_prefix = f"{tree_icon} " if tree_icon else ""

        if self.colors.enabled:
            return f"""
{c[Color.BRIGHT_CYAN]}{c[Color.BOLD]}{self.chars.separator}{c[Color.RESET]}
{c[Color.BRIGHT_WHITE]}{c[Color.BOLD]}{icon_prefix}Log Tree: {c[Color.BRIGHT_YELLOW]}{log_file_name}{c[Color.RESET]}
{c[Color.BRIGHT_CYAN]}{c[Color.BOLD]}{self.chars.separator}{c[Color.RESET]}

{c[Color.BRIGHT_BLACK]}Total entries: {c[Color.BRIGHT_WHITE]}{total_entries}{c[Color.RESET]}
"""
        return f"""
{self.chars.separator}
{icon_prefix}Log Tree: {log_file_name}
{self.chars.separator}

Total entries: {total_entries}
"""

    def render_footer(self) -> str:
        """Render clean footer."""
        c = self.colors
        sep = (
            f"{c[Color.BRIGHT_CYAN]}{c[Color.BOLD]}{self.chars.separator}{c[Color.RESET]}"
            if self.colors.enabled
            else self.chars.separator
        )
        return f"\n{sep}\n"

    def render(self, log_entries: Iterable[LogEntry]) -> str:
        """Render all log entries as modern tree."""
        tasks = self.group_by_task(log_entries)
        c = self.colors

        output: list[str] = []
        for task_uuid, entries in tasks.items():
            # Task UUID header
            uuid_colored = (
                f"{c[Color.BRIGHT_MAGENTA]}{c[Color.BOLD]}{task_uuid}{c[Color.RESET]}"
                if self.colors.enabled
                else task_uuid
            )
            output.append(uuid_colored)

            # Build and render tree
            tree = self.build_tree(entries)
            for i, node in enumerate(tree):
                output.extend(self.render_node(node, "", i == len(tree) - 1, 0))

            output.append("")  # Blank line between tasks

        return "\n".join(output)


def view_log_tree(
    log_file: str | Path,
    ascii_mode: bool = False,
    use_colors: bool = True,
    use_emojis: bool = True,
    depth_limit: int | None = None,
) -> None:
    """View log file with modern tree rendering using Python 3.12+ features."""
    log_path = Path(log_file)

    # Quick validation
    if not log_path.exists():
        c = Colors(enabled=use_colors)
        print(f"{c[Color.BRIGHT_RED]}Error: Log file not found: {log_file}{c[Color.RESET]}")
        return

    # Read and parse log entries with error handling
    try:
        log_entries = [json.loads(line) for line in log_path.read_text().splitlines() if line.strip()]
    except Exception as e:
        c = Colors(enabled=use_colors)
        print(f"{c[Color.BRIGHT_RED]}Error reading log file: {e}{c[Color.RESET]}")
        return

    # Render tree
    renderer = SimpleTreeRenderer(ascii_mode, use_colors, use_emojis, depth_limit)
    print(renderer.render_header(log_path.name, len(log_entries)))
    print(renderer.render(log_entries))
    print(renderer.render_footer())


def main() -> None:
    """Run tree viewer with modern argument parsing."""
    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        print("""Usage: python view_tree.py <log_file> [options]

Options:
  --ascii          Use plain ASCII characters
  --no-colors      Disable ANSI colors
  --no-emojis      Disable emoji indicators
  --depth-limit N  Limit tree depth to N levels
  --help, -h       Show this help message

Examples:
  python view_tree.py example_01_basic.log
  python view_tree.py example_02_actions.log --ascii
  python view_tree.py example_06_deep_nesting.log --depth-limit 5
""")
        sys.exit(0 if "--help" in sys.argv or "-h" in sys.argv else 1)

    # Parse arguments using modern Python features
    args = sys.argv[1:]
    log_file = args[0]

    options = {
        "ascii_mode": "--ascii" in args,
        "use_colors": "--no-colors" not in args and sys.stdout.isatty(),
        "use_emojis": "--no-emojis" not in args,
        "depth_limit": None,
    }

    # Parse depth limit with walrus operator
    if "--depth-limit" in args:
        idx = args.index("--depth-limit")
        if idx + 1 < len(args):
            try:
                options["depth_limit"] = int(args[idx + 1])
            except ValueError:
                print("Error: --depth-limit requires an integer")
                sys.exit(1)

    view_log_tree(log_file, **options)


if __name__ == "__main__":
    main()
