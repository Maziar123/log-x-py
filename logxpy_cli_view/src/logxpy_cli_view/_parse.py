"""Parsing functions for Eliot messages."""

from __future__ import annotations

import sys
from collections.abc import Generator, Iterable, Iterator
from contextlib import contextmanager
from typing import Any

from logxpy.parse import Parser

from logxpy_cli_view._errors import EliotParseError


def tasks_from_iterable(
    iterable: Iterable[dict[str, Any]],
) -> Iterator[Any]:
    """Parse an iterable of Eliot message dictionaries into tasks."""
    parser = Parser()
    for message_dict in iterable:
        try:
            completed, parser = parser.add(message_dict)
            for task in completed:
                yield task
        except Exception:
            raise EliotParseError(message_dict, sys.exc_info())
    for task in parser.incomplete_tasks():
        yield task


@contextmanager
def parser_context() -> Generator[Parser, None, None]:
    """Context manager for Eliot parser."""
    parser = Parser()
    try:
        yield parser
    finally:
        pass


__all__ = ["parser_context", "tasks_from_iterable"]
