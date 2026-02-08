"""Rendering functions for logxpy task trees."""

from __future__ import annotations

import sys
import traceback
import warnings
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import partial
from typing import Any, Protocol, TypeVar, runtime_checkable

from logxpy.parse import Task, WrittenAction, WrittenMessage
from toolz import compose, excepts, identity

from logxpy_cli_view import format
from logxpy_cli_view._color import colored
from logxpy_cli_view._theme import Theme, get_theme
from logxpy_cli_view._util import Writable, logxpy_ns, eliot_ns, format_namespace, is_namespace
from logxpy_cli_view.tree_format import ASCII_OPTIONS, Options, format_tree

T = TypeVar("T")

DEFAULT_IGNORED_KEYS: set[str] = {
    "action_status",
    "action_type",
    "task_level",
    "task_uuid",
    "message_type",
}


@runtime_checkable
class NodeFormatter(Protocol):
    """Protocol for node formatting functions."""

    def __call__(
        self,
        format_value: Callable[[Any, str | None], str],
        theme: Theme,
        options: Options,
        node: Task | WrittenAction | WrittenMessage | tuple[str, Any],
    ) -> str:
        ...


def _default_value_formatter(
    human_readable: bool,
    field_limit: int,
    utc_timestamps: bool = True,
    encoding: str = "utf-8",
) -> Callable[[Any, str | None], str]:
    """
    Create a value formatter based on several user-specified options.

    Args:
        human_readable: Whether to format values as human-readable
        field_limit: Length at which to truncate, 0 means no truncation
        utc_timestamps: Whether to format timestamps as UTC
        encoding: Encoding for bytes values

    Returns:
        Composed formatter function
    """
    fields: dict[str, Callable[..., Any]] = {}
    if human_readable:
        fields = {
            eliot_ns("timestamp"): format.timestamp(
                include_microsecond=False, utc_timestamps=utc_timestamps
            ),
            eliot_ns("duration"): format.duration(),
        }
    return compose(
        partial(format.escape_control_characters, overrides={0x0A: "\n"}),
        partial(format.truncate_value, field_limit) if field_limit else identity,
        format.some(
            format.fields(fields),
            format.text(),
            format.binary(encoding),
            format.anything(encoding),
        ),
    )


def message_name(
    theme: Theme,
    format_value: Callable[[Any, str | None], str],
    message: WrittenMessage | None,
    end_message: WrittenMessage | None = None,
    options: Options | None = None,
) -> str:
    """
    Derive the name for a message.

    If the message is an action type then the action_type field is used in
    conjunction with task_level and action_status. If the message is a
    message type then the message_type and task_level fields are used,
    otherwise no name will be derived.

    Args:
        theme: Color theme
        format_value: Value formatter function
        message: The message to name
        end_message: Optional end message for actions
        options: Tree formatting options

    Returns:
        Formatted message name
    """
    if message is None:
        return "<unnamed>"

    timestamp = theme.timestamp(
        format_value(message.timestamp, field_name=eliot_ns("timestamp"))
    )

    if "action_type" in message.contents:
        action_type = format.escape_control_characters(message.contents.action_type)
        duration = ""
        if end_message:
            duration_seconds = end_message.timestamp - message.timestamp
            duration = " {} {}".format(
                options.HOURGLASS if options else "",
                theme.duration(
                    format_value(
                        duration_seconds, field_name=eliot_ns("duration")
                    )
                ),
            )
            action_status = end_message.contents.action_status
        else:
            action_status = message.contents.action_status

        status_color = identity
        if action_status == "succeeded":
            status_color = theme.status_success
        elif action_status == "failed":
            status_color = theme.status_failure

        return "{}{} {} {} {}{}".format(
            theme.parent(action_type),
            theme.task_level(message.task_level.to_string()),
            options.ARROW if options else "=>",
            status_color(message.contents.action_status),
            timestamp,
            duration,
        )
    elif "message_type" in message.contents:
        message_type = format.escape_control_characters(message.contents.message_type)
        
        # Check for custom foreground/background colors from logxpy
        fg = message.contents.get("logxpy:foreground")
        bg = message.contents.get("logxpy:background")
        
        if fg or bg:
            # Apply custom colors using theme's color function
            from logxpy_cli_view._color import _get_color_code, _get_style_code
            import colored as _colored_module
            
            # Build formatting string
            formatting = ""
            if fg:
                formatting += _get_color_code(fg, is_background=False)
            if bg:
                formatting += _get_color_code(bg, is_background=True)
            
            if formatting:
                formatted = _colored_module.stylize(
                    f"{message_type} {message.task_level.to_string()} {timestamp}",
                    formatting
                )
                return formatted
        
        return f"{theme.parent(message_type)} {theme.task_level(message.task_level.to_string())} {timestamp}"

    return "<unnamed>"


def format_node(
    format_value: Callable[[Any, str | None], str],
    theme: Theme,
    options: Options,
    node: Task | WrittenAction | WrittenMessage | tuple[str, Any],
) -> str:
    """
    Format a node for display purposes.

    Different representations exist for the various types of node:
        - eliot.parse.Task: A task UUID
        - eliot.parse.WrittenAction: An action's type, level and status
        - eliot.parse.WrittenMessage: A message's type and level
        - tuple: A field name and value

    Args:
        format_value: Value formatter function
        theme: Color theme
        options: Tree formatting options
        node: Node to format

    Returns:
        Formatted node string
    """
    if isinstance(node, Task):
        return f"{theme.root(format.escape_control_characters(node.root().task_uuid))}"
    elif isinstance(node, WrittenAction):
        return message_name(
            theme, format_value, node.start_message, node.end_message, options
        )
    elif isinstance(node, WrittenMessage):
        return message_name(theme, format_value, node, options=options)
    elif isinstance(node, tuple):
        key, value = node
        if isinstance(value, (dict, list)):
            value_str = ""
        else:
            value_str = format_value(value, key)
        if is_namespace(key):
            key = format_namespace(key)
        return f"{theme.prop_key(format.escape_control_characters(key))}: {theme.prop_value(str(value_str))}"
    raise NotImplementedError(f"Unknown node type: {type(node)}")


def message_fields(
    message: WrittenMessage | None,
    ignored_fields: set[str],
) -> list[tuple[str, Any]]:
    """
    Sorted fields for a WrittenMessage.

    Args:
        message: Message to extract fields from
        ignored_fields: Set of field names to ignore

    Returns:
        List of (key, value) tuples sorted by key
    """
    if message is None:
        return []

    def _items() -> Iterable[tuple[str, Any]]:
        for key, value in message.contents.items():
            if key not in ignored_fields:
                yield key, value

    def _sortkey(x: tuple[str, Any]) -> str:
        k = x[0]
        return format_namespace(k) if is_namespace(k) else k

    return sorted(_items(), key=_sortkey)


def get_children(
    ignored_fields: set[str],
    node: Task | WrittenAction | WrittenMessage | tuple[str, Any],
) -> list[Any]:
    """
    Retrieve the child nodes for a node.

    The various types of node have different concepts of children:
        - eliot.parse.Task: The root WrittenAction
        - eliot.parse.WrittenAction: The start message fields, child
          WrittenAction or WrittenMessages, and end WrittenMessage
        - eliot.parse.WrittenMessage: Message fields
        - tuple: Contained values for dict and list types

    Args:
        ignored_fields: Set of field names to ignore
        node: Node to get children for

    Returns:
        List of child nodes
    """
    if isinstance(node, Task):
        return [node.root()]
    elif isinstance(node, WrittenAction):
        children = message_fields(node.start_message, ignored_fields)
        children.extend(node.children)
        if node.end_message:
            children.append(node.end_message)
        return [c for c in children if c is not None]
    elif isinstance(node, WrittenMessage):
        return message_fields(node, ignored_fields)
    elif isinstance(node, tuple):
        value = node[1]
        if isinstance(value, dict):
            return sorted(value.items())
        elif isinstance(value, list):
            return list(enumerate(value))
    return []


def track_exceptions(
    f: Callable[..., T],
    caught: list[Any],
    default: T | None = None,
) -> Callable[..., T | None]:
    """
    Decorate f with a function that traps exceptions and appends them to
    caught, returning default in their place.

    Args:
        f: Function to wrap
        caught: List to append exceptions to
        default: Default value to return on exception

    Returns:
        Wrapped function
    """
    def _catch(_: Any) -> T | None:
        caught.append(sys.exc_info())
        return default

    return excepts(Exception, f, _catch)


@dataclass(slots=True)
class ColorizedOptions:
    """
    Options for format_tree that colorizes sub-trees.
    """

    failed_color: Callable[[str], str]
    depth_colors: list[Callable[[str], str]]
    options: Options

    def __getattr__(self, name: str) -> Any:
        return getattr(self.options, name)

    def color(self, node: WrittenAction | Any, depth: int) -> Callable[[str], str]:
        if isinstance(node, WrittenAction):
            end_message = node.end_message
            if end_message and end_message.contents.action_status == "failed":
                return self.failed_color
        return self.depth_colors[depth % len(self.depth_colors)]


def render_tasks(
    write: Writable | Callable[[str], Any],
    tasks: Iterable[Any],
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
) -> None:
    """
    Render Eliot tasks as an ASCII tree.

    Args:
        write: Callable used to write the output (or Writable protocol)
        tasks: Iterable of parsed Eliot tasks
        field_limit: Length at which to begin truncating, 0 means no truncation
        ignored_fields: Set of field names to ignore
        human_readable: Render field values as human-readable
        colorize: Deprecated, use theme
        write_err: Callable used to write errors (or Writable protocol)
        format_node: Function to format nodes
        format_value: Callable to format a value
        utc_timestamps: Format timestamps as UTC
        colorize_tree: Colorize the tree output
        ascii: Render the tree as plain ASCII instead of Unicode
        theme: Theme to use for rendering
    """

    def make_options() -> Options | ColorizedOptions:
        if ascii:
            _options = ASCII_OPTIONS
        else:
            _options = Options()
        if colorize_tree:
            return ColorizedOptions(
                failed_color=theme.tree_failed if theme else identity,
                depth_colors=[
                    theme.tree_color0 if theme else identity,
                    theme.tree_color1 if theme else identity,
                    theme.tree_color2 if theme else identity,
                ],
                options=_options,
            )
        return _options

    options = make_options()

    if ignored_fields is None:
        ignored_fields = DEFAULT_IGNORED_KEYS

    if colorize is not None:
        warnings.warn(
            "Passing `colorize` is deprecated, use `theme` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        theme = get_theme(
            dark_background=True, colored=colored if colorize else None
        )

    if theme is None:
        theme = get_theme(dark_background=True)

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
        partial(format_node, _format_value, theme, options),
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
        for exc in caught_exceptions:
            for line in traceback.format_exception(*exc):
                if isinstance(line, bytes):
                    line = line.decode("utf-8")
                write_err(line)
            write_err("\n")


__all__ = [
    "DEFAULT_IGNORED_KEYS",
    "ColorizedOptions",
    "NodeFormatter",
    "format_node",
    "get_children",
    "message_fields",
    "message_name",
    "render_tasks",
    "track_exceptions",
]
