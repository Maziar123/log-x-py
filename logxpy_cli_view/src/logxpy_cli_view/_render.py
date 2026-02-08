"""Rendering functions for logxpy CLI view."""

from __future__ import annotations

import json
import warnings
from collections.abc import Callable, Iterable, Mapping, Set
from dataclasses import dataclass
from functools import partial
from typing import Any

from toolz import compose

from logxpy_cli_view import format
from logxpy_cli_view._color import color_factory, colored, _get_color_code


def _apply_fg_bg_colors(text: str, fg: str | None, bg: str | None) -> str:
    """Apply foreground and background colors to text if specified.
    
    Args:
        text: The text to color
        fg: Foreground color name (optional)
        bg: Background color name (optional)
    
    Returns:
        Colored text if colors specified, otherwise original text
    """
    if not fg and not bg:
        return text
    
    # Build ANSI codes
    codes = ""
    if fg:
        codes += _get_color_code(fg, is_background=False)
    if bg:
        codes += _get_color_code(bg, is_background=True)
    
    if codes:
        return colored(text, codes)
    return text
from logxpy_cli_view._compat import get, get_message_type
from logxpy_cli_view._theme import Theme, get_theme
from logxpy_cli_view._util import Writable, logxpy_ns, eliot_ns, format_namespace, is_namespace
from logxpy_cli_view.tree_format import ASCII_OPTIONS, Options, format_tree


class ColorizedOptions(Options):
    """Options with color support for tree rendering."""

    def __init__(
        self,
        failed_color: Callable[[str], str],
        depth_colors: list[Callable[[str], str]],
        options: Options | None = None,
    ):
        if options is None:
            super().__init__()
        else:
            super().__init__(
                FORK=options.FORK,
                LAST=options.LAST,
                VERTICAL=options.VERTICAL,
                HORIZONTAL=options.HORIZONTAL,
                NEWLINE=options.NEWLINE,
                ARROW=options.ARROW,
                HOURGLASS=options.HOURGLASS,
            )
        self._failed_color = failed_color
        self._depth_colors = depth_colors

    def color(self, node: Any, depth: int) -> Callable[..., str]:
        """Return color function for node at depth."""
        if hasattr(node, 'end_message') and node.end_message:
            # Check if action failed
            end_contents = node.end_message.contents if hasattr(node.end_message, 'contents') else {}
            status = end_contents.get('st') or end_contents.get('action_status', '')
            if status == 'failed':
                return self._failed_color
        # Use depth-based color
        if self._depth_colors:
            return self._depth_colors[depth % len(self._depth_colors)]
        return lambda text, *a, **kw: text

# ============================================================================
# Constants
# ============================================================================

# Ignored keys - includes both compact and legacy field names
DEFAULT_IGNORED_KEYS = frozenset(
    {
        # Compact format
        "ts",
        "tid",
        "lvl",
        "mt",
        "at",
        "st",
        "msg",
        "dur",
        "fg",
        "bg",
        # Legacy format
        "timestamp",
        "task_uuid",
        "task_level",
        "message_type",
        "action_type",
        "action_status",
        "message",
        "duration",
        "logxpy:duration",
        "logxpy:foreground",
        "logxpy:background",
        # Eliot compatibility
        "eliot:timestamp",
        "eliot:task_uuid",
        "eliot:task_level",
        "eliot:message_type",
        "eliot:action_type",
        "eliot:action_status",
    }
)


# ============================================================================
# Helper Functions
# ============================================================================

def identity(value: Any) -> Any:
    """Identity function - returns value unchanged."""
    return value


def _escape_control_chars(text: str) -> str:
    """Escape control characters in text for safe display."""
    result = []
    for char in text:
        if char == '\n':
            result.append('\\n')
        elif char == '\r':
            result.append('\\r')
        elif char == '\t':
            result.append('\\t')
        elif ord(char) < 32:
            result.append(f'\\x{ord(char):02x}')
        else:
            result.append(char)
    return ''.join(result)


# ============================================================================
# Value Formatting
# ============================================================================

def _format_value_human_readable(
    value: Any,
    field_name: str | None = None,
    field_limit: int = 0,
    utc_timestamps: bool = True,
) -> str:
    """Format a value as human-readable string."""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        escaped = _escape_control_chars(value)
        if field_limit and len(escaped) > field_limit:
            return escaped[:field_limit - 3] + "..."
        return escaped
    elif isinstance(value, (list, tuple)):
        return json.dumps(value, default=str)
    elif isinstance(value, dict):
        return json.dumps(value, default=str)
    else:
        return str(value)


def _default_value_formatter(
    human_readable: bool = False,
    field_limit: int = 0,
    utc_timestamps: bool = True,
) -> Callable[[Any, str | None], str]:
    """Create a default value formatter."""
    if human_readable:
        return partial(
            _format_value_human_readable,
            field_limit=field_limit,
            utc_timestamps=utc_timestamps,
        )
    else:
        def format_simple(value: Any, field_name: str | None = None) -> str:
            text = str(value)
            if field_limit and len(text) > field_limit:
                return text[:field_limit - 3] + "..."
            return text
        return format_simple


# ============================================================================
# Exception Tracking
# ============================================================================

def track_exceptions(
    func: Callable[..., T],
    exceptions: list[Any],
    error_message: str,
) -> Callable[..., T]:
    """Wrap a function to track exceptions."""
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            exceptions.append((e, error_message))
            return error_message
    return wrapper


# ============================================================================
# Node Formatting
# ============================================================================

def message_fields(
    message: Any,
    ignored_fields: set[str] | None = None,
) -> list[tuple[str, Any]]:
    """Get fields from a message, excluding ignored ones."""
    if ignored_fields is None:
        ignored_fields = DEFAULT_IGNORED_KEYS

    result = []
    
    # Handle Task object - get root node
    if hasattr(message, 'root'):
        message = message.root()
    
    # Handle WrittenAction - get fields from start_message
    if hasattr(message, 'start_message') and message.start_message:
        if hasattr(message.start_message, 'contents'):
            contents = message.start_message.contents
            if isinstance(contents, dict):
                for key, value in contents.items():
                    if key not in ignored_fields:
                        result.append((key, value))
        return result
    
    # Handle regular WrittenMessage
    if hasattr(message, 'contents'):
        contents = message.contents
        if isinstance(contents, dict):
            for key, value in contents.items():
                if key not in ignored_fields:
                    result.append((key, value))
    return result


def message_name(
    theme: Theme,
    format_value: Callable[[Any, str | None], str],
    message: Any | None,
    end_message: Any | None = None,
    options: Options | None = None,
    line_number: int | None = None,
) -> str:
    """Derive the name for a message."""
    if message is None:
        return "<unnamed>"

    line_prefix = ""
    if line_number is not None:
        line_prefix = f"{theme.line_number(f'[{line_number}]')} "

    # Handle Task object - get root node
    if hasattr(message, 'root'):
        message = message.root()

    # Handle WrittenAction - use start_message for naming
    if hasattr(message, 'start_message') and message.start_message:
        start_msg = message.start_message
        end_msg = message.end_message if hasattr(message, 'end_message') else None
        
        # Get timestamp from start message
        timestamp = theme.timestamp(
            format_value(start_msg.timestamp, field_name="timestamp")
        ) if hasattr(start_msg, 'timestamp') else ""
        
        # Support both compact (at) and legacy (action_type) field names
        action_type_val = None
        if hasattr(start_msg, 'contents'):
            action_type_val = start_msg.contents.get("at") or start_msg.contents.get("action_type")
        
        if action_type_val:
            action_type = format.escape_control_characters(action_type_val)
            duration = ""
            action_status = ""
            if end_msg and hasattr(end_msg, 'timestamp') and hasattr(start_msg, 'timestamp'):
                duration_seconds = end_msg.timestamp - start_msg.timestamp
                duration = f" ⧖ {duration_seconds:.3f}s"
                # Support both compact (st) and legacy (action_status) field names
                action_status = end_msg.contents.get("st") or end_msg.contents.get("action_status", "")
            else:
                # Fallback to start message status
                action_status = start_msg.contents.get("st") or start_msg.contents.get("action_status", "") if hasattr(start_msg, 'contents') else ""
            
            status_color = identity
            if action_status == "succeeded":
                status_color = theme.status_success
            elif action_status == "failed":
                status_color = theme.status_failure
            
            task_level_str = ""
            if hasattr(start_msg, 'task_level'):
                task_level_str = start_msg.task_level.to_string()
            
            return f"{line_prefix}{theme.parent(action_type)}/{task_level_str} ⇒ {status_color(action_status)} {timestamp}{duration}"
        
        # Check for message_type in start message
        msg_type_val = None
        if hasattr(start_msg, 'contents'):
            msg_type_val = start_msg.contents.get("mt") or start_msg.contents.get("message_type", "")
        
        if msg_type_val:
            message_type = format.escape_control_characters(msg_type_val)
            task_level_str = ""
            if hasattr(start_msg, 'task_level'):
                task_level_str = start_msg.task_level.to_string()
            return f"{line_prefix}{message_type} {task_level_str} {timestamp}"
    
    # Handle regular WrittenMessage
    timestamp = theme.timestamp(
        format_value(message.timestamp, field_name="timestamp")
    ) if hasattr(message, 'timestamp') else ""

    # Support both compact (at) and legacy (action_type) field names
    action_type_val = None
    if hasattr(message, 'contents'):
        action_type_val = message.contents.get("at") or message.contents.get("action_type")

    if action_type_val:
        action_type = format.escape_control_characters(action_type_val)
        duration = ""
        action_status = ""
        if end_message and hasattr(end_message, 'timestamp') and hasattr(message, 'timestamp'):
            duration_seconds = end_message.timestamp - message.timestamp
            duration = f" ⧖ {duration_seconds:.3f}s"
            # Support both compact (st) and legacy (action_status) field names
            action_status = end_message.contents.get("st") or end_message.contents.get("action_status", "")
        else:
            action_status = message.contents.get("st") or message.contents.get("action_status", "") if hasattr(message, 'contents') else ""

        status_color = identity
        if action_status == "succeeded":
            status_color = theme.status_success
        elif action_status == "failed":
            status_color = theme.status_failure

        task_level_str = ""
        if hasattr(message, 'task_level'):
            task_level_str = message.task_level.to_string()

        return f"{line_prefix}{theme.parent(action_type)}/{task_level_str} ⇒ {status_color(action_status)} {timestamp}{duration}"

    # Support both compact (mt) and legacy (message_type) field names
    msg_type_val = None
    if hasattr(message, 'contents'):
        msg_type_val = message.contents.get("mt") or message.contents.get("message_type", "")

    if msg_type_val:
        message_type = format.escape_control_characters(msg_type_val)
        task_level_str = ""
        if hasattr(message, 'task_level'):
            task_level_str = message.task_level.to_string()
        return f"{line_prefix}{message_type} {task_level_str} {timestamp}"

    return "<unnamed>"


# ============================================================================
# Tree Node Processing
# ============================================================================

def format_node(
    format_value: Callable[[Any, str | None], str],
    theme: Theme,
    options: Options,
    node: Any,
    depth: int = 0,
    is_last: bool = False,
    inventory: dict[str, int] | None = None,
    show_line_numbers: bool = True,
) -> str:
    """Format a single tree node.
    
    Note: The tree formatter handles the tree drawing prefixes (├──, └──, │).
    This function should only format the node content.
    """
    name = message_name(theme, format_value, node, options=options)
    fields = message_fields(node)

    result = f"{name}\n"
    for key, value in fields:
        formatted_value = format_value(value, field_name=key)
        # Use the tree format's vertical() method for indentation
        indent = options.vertical() if hasattr(options, 'vertical') else "│   "
        result += f"{indent}{theme.prop_key(key)}: {formatted_value}\n"

    return result


NodeFormatter = Callable[..., str]


# ============================================================================
# Children Processing
# ============================================================================

def get_children(
    ignored_fields: set[str] | None,
    node: Any,
) -> list[Any]:
    """Get children of a node."""
    # Handle Task object - get root node first
    if hasattr(node, 'root'):
        node = node.root()
    
    # Handle WrittenAction - get children from _children
    if hasattr(node, '_children'):
        return list(node._children.values())
    return []


# ============================================================================
# Task to Dict Conversion
# ============================================================================

def _task_to_dict(task: Any) -> dict[str, Any]:
    """Convert a Task object or dict to a dictionary."""
    if hasattr(task, "root"):
        root = task.root()
        if hasattr(root, "_logged_dict"):
            return dict(root._logged_dict)
        elif hasattr(root, "as_dict"):
            return dict(root.as_dict())
        else:
            return {}
    elif isinstance(task, dict):
        return task
    else:
        return {}


def _get_task_nodes_flat(task: Any) -> list[tuple[int, dict[str, Any], bool]]:
    """Flatten a Task object into list of (depth, node_dict, is_last) tuples.

    Actions are consolidated - each action shows as one line with final status.
    """
    result: list[tuple[int, dict[str, Any], bool]] = []

    def process_node(node: Any, depth: int = 0, is_last: bool = True) -> None:
        """Recursively process a node and its children."""
        if hasattr(node, '_logged_dict'):
            # It's a WrittenMessage (not an action)
            result.append((depth, dict(node._logged_dict), is_last))
        elif hasattr(node, 'start_message') and hasattr(node, 'end_message'):
            # It's a WrittenAction - consolidate start+end into one entry
            start_dict = dict(node.start_message._logged_dict) if node.start_message and hasattr(node.start_message, '_logged_dict') else {}
            end_dict = dict(node.end_message._logged_dict) if node.end_message and hasattr(node.end_message, '_logged_dict') else {}

            # Merge: use start fields + end status
            merged = dict(start_dict)
            if end_dict:
                # Override with end status
                if 'st' in end_dict:
                    merged['st'] = end_dict['st']
                if 'action_status' in end_dict:
                    merged['action_status'] = end_dict['action_status']
                # Calculate duration
                if hasattr(node.start_message, 'timestamp') and hasattr(node.end_message, 'timestamp'):
                    duration = node.end_message.timestamp - node.start_message.timestamp
                    merged['_duration'] = duration

            merged['_is_action'] = True
            result.append((depth, merged, is_last))

            # Process children if any
            if hasattr(node, '_children') and node._children:
                children = sorted(node._children.items(), key=lambda x: str(x[0]))
                for i, (child_level, child_node) in enumerate(children):
                    child_is_last = (i == len(children) - 1)
                    process_node(child_node, depth + 1, child_is_last)
        elif hasattr(node, '_children') and node._children:
            # Has children but not an action (like root Task)
            children = sorted(node._children.items(), key=lambda x: str(x[0]))
            for i, (child_level, child_node) in enumerate(children):
                child_is_last = (i == len(children) - 1)
                process_node(child_node, depth, child_is_last)

    if hasattr(task, 'root'):
        process_node(task.root())
    elif hasattr(task, '_nodes'):
        # Task object - process all nodes
        children = sorted(task._nodes.items(), key=lambda x: str(x[0]))
        for i, (level, node) in enumerate(children):
            is_last = (i == len(children) - 1)
            process_node(node, 0, is_last)

    return result


def _build_tree_prefix(depth: int, is_last: bool = False, parent_prefixes: list[bool] | None = None) -> str:
    """Build tree drawing prefix like '├── ' or '│   ├── '."""
    if depth == 0:
        return ""

    prefix = ""
    if parent_prefixes:
        for is_parent_last in parent_prefixes:
            if is_parent_last:
                prefix += "    "
            else:
                prefix += "│   "

    if is_last:
        prefix += "└── "
    else:
        prefix += "├── "

    return prefix


# ============================================================================
# Rendering Functions
# ============================================================================

def render_oneline(
    tasks: Iterable[Any],
    write: Writable | Callable[[str], Any],
    theme: Theme | None = None,
    max_msg_len: int = 80,
) -> None:
    """Render tasks in one-line tree format.

    Format: [tree_prefix] tid │ at/mt [lvl] ⇒ status │ msg │ field1=value1 ...

    Shows hierarchical tree structure - actions consolidated (start+end together).
    """
    if theme is None:
        theme = get_theme(dark_background=True)

    # Fields to exclude from "extra fields" display
    CORE_FIELDS = {"ts", "tid", "lvl", "mt", "at", "st", "msg", "fg", "bg",
                   "_is_action", "action_type", "action_status", "message_type"}

    for task in tasks:
        # Check if this is a complex Task with hierarchy
        if hasattr(task, 'root') or hasattr(task, '_nodes'):
            # Process as hierarchical task - actions are consolidated
            nodes = _get_task_nodes_flat(task)

            # Track parent prefixes for proper tree drawing
            parent_prefixes: list[bool] = []

            for depth, node_dict, is_last in nodes:
                # Build tree prefix based on depth
                tree_prefix = _build_tree_prefix(depth, is_last, parent_prefixes[:depth-1] if depth > 0 else [])

                # Update parent prefixes for next iteration
                while len(parent_prefixes) < depth:
                    parent_prefixes.append(False)
                if depth > 0:
                    parent_prefixes[depth - 1] = is_last

                # Get fields
                tid = get(node_dict, "tid", "?")
                at = get(node_dict, "at") or get(node_dict, "action_type", "")
                mt = get_message_type(node_dict) or ""
                lvl = get(node_dict, "lvl") or get(node_dict, "task_level", [])
                st = get(node_dict, "st") or get(node_dict, "action_status", "")
                msg = get(node_dict, "msg", "")
                duration = node_dict.get('_duration', 0)

                # Format level string
                lvl_str = "/".join(str(x) for x in lvl) if lvl else ""

                # Determine what to show as "type"
                msg_type = at if at else mt

                # Handle status coloring
                status_color = identity
                if st == "succeeded":
                    status_color = theme.status_success if hasattr(theme, 'status_success') else identity
                elif st == "failed":
                    status_color = theme.status_failure if hasattr(theme, 'status_failure') else identity

                # Build extra fields
                extra_fields = []
                for key, value in sorted(node_dict.items()):
                    if key not in CORE_FIELDS and not key.startswith('_'):
                        val_str = str(value)
                        if len(val_str) > 20:
                            val_str = val_str[:17] + "..."
                        extra_fields.append(f"{key}={val_str}")

                # Format line like tree view: type/lvl ⇒ status
                tid_fmt = theme.root(tid[:8]) if hasattr(theme, 'root') else tid[:8]
                type_fmt = theme.parent(msg_type) if hasattr(theme, 'parent') else msg_type
                status_fmt = status_color(st) if st else ""

                # Build the line
                line = f"{tree_prefix}{tid_fmt} │ {type_fmt}"

                if lvl_str:
                    line += f"/{lvl_str}"

                if status_fmt:
                    line += f" ⇒ {status_fmt}"

                # Add duration if available
                if duration and duration > 0:
                    line += f" ⧖ {duration:.3f}s"

                # Extract fg/bg colors from message
                fg = get(node_dict, "fg") or get(node_dict, "logxpy:foreground")
                bg = get(node_dict, "bg") or get(node_dict, "logxpy:background")

                if msg:
                    if len(msg) > max_msg_len:
                        msg = msg[:max_msg_len-3] + "..."
                    # Apply fg/bg colors to message
                    msg_colored = _apply_fg_bg_colors(msg, fg, bg)
                    line += f" │ {msg_colored}"

                if extra_fields:
                    extras = " ".join(extra_fields)
                    extras_colored = _apply_fg_bg_colors(
                        extras, 
                        fg if not msg else None,  # Only color extras if msg wasn't colored
                        bg if not msg else None
                    )
                    line += f" │ {theme.prop_key(extras_colored) if hasattr(theme, 'prop_key') else extras_colored}"

                write(line + "\n")
        else:
            # Simple dict - process as flat
            task_dict = _task_to_dict(task)

            tid = get(task_dict, "tid", "?")
            mt = get_message_type(task_dict) or "?"
            msg = get(task_dict, "msg", "")

            if not msg:
                msg = "<no message>"

            if len(msg) > max_msg_len:
                msg = msg[:max_msg_len-3] + "..."

            # Extract fg/bg colors
            fg = get(task_dict, "fg") or get(task_dict, "logxpy:foreground")
            bg = get(task_dict, "bg") or get(task_dict, "logxpy:background")

            # Build extra fields
            extra_fields = []
            for key, value in sorted(task_dict.items()):
                if key not in CORE_FIELDS:
                    val_str = str(value)
                    if len(val_str) > 30:
                        val_str = val_str[:27] + "..."
                    extra_fields.append(f"{key}={val_str}")

            tid_colored = theme.root(tid) if hasattr(theme, 'root') else tid
            mt_colored = theme.prop_key(mt) if hasattr(theme, 'prop_key') else mt
            msg_colored = _apply_fg_bg_colors(msg, fg, bg)

            if extra_fields:
                extras_str = " ".join(extra_fields)
                extras_colored = _apply_fg_bg_colors(
                    extras_str,
                    fg if not msg else None,
                    bg if not msg else None
                )
                line = f"│ {tid_colored:6} │ {mt_colored:8} │ {msg_colored} │ {theme.prop_key(extras_colored) if hasattr(theme, 'prop_key') else extras_colored}"
            else:
                line = f"│ {tid_colored:6} │ {mt_colored:8} │ {msg_colored}"

            write(line + "\n")


def render_tasks(
    write: Writable | Callable[[str], Any],
    tasks: Iterable[Any],
    inventory: dict[str, int] | None = None,
    field_limit: int = 0,
    ignored_fields: set[str] | None = None,
    human_readable: bool = False,
    colorize: bool | None = None,
    write_err: Writable | Callable[[str], Any] | None = None,
    format_node: NodeFormatter = format_node,
    format_value: Callable[[Any, str | None], str] | None = None,
    utc_timestamps: bool = True,
    colorize_tree: bool = False,
    ascii: bool = False,
    theme: Theme | None = None,
    show_line_numbers: bool = True,
) -> None:
    """Render tasks as a tree."""
    if theme is None:
        theme = get_theme(dark_background=True)

    if ascii:
        _options: Options = ASCII_OPTIONS
    else:
        _options = Options()

    if colorize_tree:
        options = ColorizedOptions(
            failed_color=theme.tree_failed if hasattr(theme, 'tree_failed') else identity,
            depth_colors=[
                theme.tree_color0 if hasattr(theme, 'tree_color0') else identity,
                theme.tree_color1 if hasattr(theme, 'tree_color1') else identity,
                theme.tree_color2 if hasattr(theme, 'tree_color2') else identity,
            ],
            options=_options,
        )
    else:
        options = _options

    if ignored_fields is None:
        ignored_fields = set(DEFAULT_IGNORED_KEYS)

    if inventory is None:
        inventory = {}

    caught_exceptions: list[Any] = []

    if format_value is None:
        format_value = _default_value_formatter(
            human_readable=human_readable,
            field_limit=field_limit,
            utc_timestamps=utc_timestamps,
        )

    _format_value = track_exceptions(
        format_value,
        caught_exceptions,
        "<value formatting exception>",
    )
    _format_node = track_exceptions(
        partial(format_node, _format_value, theme, options, inventory=inventory, show_line_numbers=show_line_numbers),
        caught_exceptions,
        "<node formatting exception>",
    )
    _get_children = partial(get_children, ignored_fields)

    for task in tasks:
        write(format_tree(task, _format_node, _get_children, options))
        write("\n")

    if write_err and caught_exceptions:
        write_err(
            theme.error(
                f"Exceptions ({len(caught_exceptions)}) occurred during processing:\n"
            )
        )
