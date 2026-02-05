"""Color utilities for eliot-tree."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import colored


def color_factory(
    colored_func: Callable[..., str],
) -> Callable[..., Callable[[str], str]]:
    """Create a color factory function."""
    def factory(
        foreground: str | None = None,
        background: str | None = None,
        attrs: list[str] | None = None,
    ) -> Callable[[str], str]:
        def colorize(text: str) -> str:
            if foreground is None and background is None and not attrs:
                return text
            return colored_func(
                text,
                color=foreground,
                bg=background,
                attrs=attrs or [],
            )
        return colorize
    return factory


def colored(text: str, *args: Any, **kwargs: Any) -> str:
    """Wrapper around colored.stylize."""
    return colored.stylize(text, *args, **kwargs)


def no_color(text: str, *args: Any, **kwargs: Any) -> str:
    """No-op color function."""
    return text


__all__ = ["color_factory", "colored", "no_color"]
