"""Library for formatting trees."""

# Copyright (c) 2015 Jonathan M. Lange <jml@mumak.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import itertools
from collections.abc import Callable
from typing import Any

RIGHT_DOUBLE_ARROW = "\N{RIGHTWARDS DOUBLE ARROW}"
HOURGLASS = "\N{WHITE HOURGLASS}"


class Options:
    """Tree formatting options."""

    def __init__(
        self,
        FORK: str = "\u251c",
        LAST: str = "\u2514",
        VERTICAL: str = "\u2502",
        HORIZONTAL: str = "\u2500",
        NEWLINE: str = "\u23ce",
        ARROW: str = RIGHT_DOUBLE_ARROW,
        HOURGLASS: str = HOURGLASS,
    ):
        self.FORK = FORK
        self.LAST = LAST
        self.VERTICAL = VERTICAL
        self.HORIZONTAL = HORIZONTAL
        self.NEWLINE = NEWLINE
        self.ARROW = ARROW
        self.HOURGLASS = HOURGLASS

    def color(self, node: Any, depth: int) -> Callable[..., str]:
        """Return color function for node at depth."""
        return lambda text, *a, **kw: text

    def vertical(self) -> str:
        """Vertical connector string."""
        return "".join([self.VERTICAL, "   "])

    def fork(self) -> str:
        """Fork connector string."""
        return "".join([self.FORK, self.HORIZONTAL, self.HORIZONTAL, " "])

    def last(self) -> str:
        """Last child connector string."""
        return "".join([self.LAST, self.HORIZONTAL, self.HORIZONTAL, " "])


ASCII_OPTIONS = Options(
    FORK="|",
    LAST="+",
    VERTICAL="|",
    HORIZONTAL="-",
    NEWLINE="\n",
    ARROW="=>",
    HOURGLASS="|Y|",
)


def _format_newlines(prefix: str, formatted_node: str, options: Options) -> str:
    """
    Convert newlines into U+23EC characters, followed by an actual newline and
    then a tree prefix so as to position the remaining text under the previous
    line.
    """
    replacement = "".join([options.NEWLINE, "\n", prefix])
    return formatted_node.replace("\n", replacement)


def _format_tree(
    node: Any,
    format_node: Callable[[Any], str],
    get_children: Callable[[Any], list[Any]],
    options: Options,
    prefix: str = "",
    depth: int = 0,
) -> Iterator[str]:
    """Recursively format tree nodes."""
    children = list(get_children(node))
    color = options.color(node, depth)
    next_prefix = prefix + color(options.vertical())

    for child in children[:-1]:
        yield "".join(
            [
                prefix,
                color(options.fork()),
                _format_newlines(next_prefix, format_node(child), options),
            ]
        )
        yield from _format_tree(
            child, format_node, get_children, options, next_prefix, depth + 1
        )

    if children:
        last_prefix = "".join([prefix, "    "])
        yield "".join(
            [
                prefix,
                color(options.last()),
                _format_newlines(last_prefix, format_node(children[-1]), options),
            ]
        )
        yield from _format_tree(
            children[-1], format_node, get_children, options, last_prefix, depth + 1
        )


def format_tree(
    node: Any,
    format_node: Callable[[Any], str],
    get_children: Callable[[Any], list[Any]],
    options: Options | None = None,
) -> str:
    """
    Format a tree structure as a string.

    Args:
        node: Root node
        format_node: Function to format a node to string
        get_children: Function to get children of a node
        options: Formatting options

    Returns:
        Formatted tree string
    """
    lines = itertools.chain(
        [format_node(node)],
        _format_tree(node, format_node, get_children, options or Options()),
        [""],
    )
    return "\n".join(lines)


def format_ascii_tree(
    tree: Any,
    format_node: Callable[[Any], str],
    get_children: Callable[[Any], list[Any]],
) -> str:
    """Format the tree using only ASCII characters."""
    return format_tree(tree, format_node, get_children, ASCII_OPTIONS)


def print_tree(*args: Any, **kwargs: Any) -> None:
    """Print a formatted tree."""
    print(format_tree(*args, **kwargs))
