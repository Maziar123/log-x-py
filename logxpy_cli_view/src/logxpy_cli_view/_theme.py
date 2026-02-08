"""Theme support for eliot-tree."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, overload

from logxpy_cli_view._color import color_factory, no_color


class ThemeMode(Enum):
    """Available theme modes for terminal backgrounds."""
    AUTO = auto()
    DARK = auto()
    LIGHT = auto()


@dataclass(slots=True)
class Theme:
    """Theme class for terminal color styling.
    
    All color attributes are callable that take a string and return
    a styled string.
    """

    # Core color function
    color: Callable[..., Callable[[str], str]] = field(default=color_factory)

    # Task root color
    root: Callable[[str], str] = field(default=lambda x: x)
    # Action / message node color
    parent: Callable[[str], str] = field(default=lambda x: x)
    # Action / message task level color
    task_level: Callable[[str], str] = field(default=lambda x: x)
    # Action success status color
    status_success: Callable[[str], str] = field(default=lambda x: x)
    # Action failure status color
    status_failure: Callable[[str], str] = field(default=lambda x: x)
    # Task timestamp color
    timestamp: Callable[[str], str] = field(default=lambda x: x)
    # Action / message property key color
    prop_key: Callable[[str], str] = field(default=lambda x: x)
    # Action / message property value color
    prop_value: Callable[[str], str] = field(default=lambda x: x)
    # Task duration color
    duration: Callable[[str], str] = field(default=lambda x: x)
    # Tree color for failed tasks
    tree_failed: Callable[[str], str] = field(default=lambda x: x)
    # Cycled tree colors
    tree_color0: Callable[[str], str] = field(default=lambda x: x)
    tree_color1: Callable[[str], str] = field(default=lambda x: x)
    tree_color2: Callable[[str], str] = field(default=lambda x: x)
    # Processing error color
    error: Callable[[str], str] = field(default=lambda x: x)
    # Line number color
    line_number: Callable[[str], str] = field(default=lambda x: x)

    @classmethod
    def create(
        cls,
        colored: Callable[..., str],
        **theme: tuple[Any, ...],
    ) -> Theme:
        """
        Factory method to create a Theme with color validation.
        
        Args:
            colored: The colored function to use
            **theme: Theme color specifications as tuples
            
        Returns:
            Configured Theme instance
        """
        color_fn = color_factory(colored)

        # Validate and apply colors
        processed = {}
        for key, color_spec in theme.items():
            if not isinstance(color_spec, (tuple, list)):
                raise TypeError(
                    f"Theme color must be a tuple or list of values: {key}={color_spec}"
                )
            processed[key] = color_fn(*color_spec)

        return cls(color=color_fn, **processed)


class DarkBackgroundTheme(Theme):
    """Color theme for dark backgrounds."""

    def __init__(self, colored: Callable[..., str]):
        color_fn = color_factory(colored)
        super().__init__(
            color=color_fn,
            root=color_fn("white", attrs=["bold"]),
            parent=color_fn("magenta"),
            status_success=color_fn("green"),
            status_failure=color_fn("red"),
            prop_key=color_fn("blue"),
            error=color_fn("red", attrs=["bold"]),
            timestamp=color_fn("white", attrs=["dim"]),
            duration=color_fn("blue", attrs=["dim"]),
            tree_failed=color_fn("red"),
            tree_color0=color_fn("white", attrs=["dim"]),
            tree_color1=color_fn("blue", attrs=["dim"]),
            tree_color2=color_fn("magenta", attrs=["dim"]),
            line_number=color_fn("cyan", attrs=["dim"]),
        )


class LightBackgroundTheme(Theme):
    """Color theme for light backgrounds."""

    def __init__(self, colored: Callable[..., str]):
        color_fn = color_factory(colored)
        super().__init__(
            color=color_fn,
            root=color_fn("dark_gray", attrs=["bold"]),
            parent=color_fn("magenta"),
            status_success=color_fn("green"),
            status_failure=color_fn("red"),
            prop_key=color_fn("blue"),
            error=color_fn("red", attrs=["bold"]),
            timestamp=color_fn("dark_gray"),
            duration=color_fn("blue", attrs=["dim"]),
            tree_failed=color_fn("red"),
            tree_color0=color_fn("dark_gray", attrs=["dim"]),
            tree_color1=color_fn("blue", attrs=["dim"]),
            tree_color2=color_fn("magenta", attrs=["dim"]),
            line_number=color_fn("cyan", attrs=["dim"]),
        )


@overload
def get_theme(
    dark_background: True,
    colored: Callable[..., str] | None = None,
) -> DarkBackgroundTheme: ...


@overload
def get_theme(
    dark_background: False,
    colored: Callable[..., str] | None = None,
) -> LightBackgroundTheme: ...


@overload
def get_theme(
    mode: ThemeMode,
    colored: Callable[..., str] | None = None,
) -> Theme: ...


def get_theme(
    dark_background: bool | ThemeMode = True,
    colored: Callable[..., str] | None = None,
) -> Theme:
    """
    Create an appropriate theme.

    Args:
        dark_background: Whether to use dark background theme, or a ThemeMode enum
        colored: Color function to use, or None for no color

    Returns:
        Theme instance
    """
    if colored is None:
        colored = no_color

    # Handle ThemeMode enum
    if isinstance(dark_background, ThemeMode):
        if dark_background == ThemeMode.AUTO:
            # Default to dark for auto when we can't detect
            dark_background = True
        else:
            dark_background = dark_background == ThemeMode.DARK

    return DarkBackgroundTheme(colored) if dark_background else LightBackgroundTheme(colored)


def apply_theme_overrides(
    theme: Theme,
    overrides: dict[str, tuple[Any, ...]] | None,
) -> Theme:
    """
    Apply overrides to a theme.

    Args:
        theme: Theme to modify
        overrides: Dictionary of theme key to color arguments

    Returns:
        Modified theme (same instance, mutated)
    """
    if overrides is None:
        return theme

    for key, args in overrides.items():
        setattr(theme, key, theme.color(*args))
    return theme


__all__ = [
    "DarkBackgroundTheme",
    "LightBackgroundTheme",
    "Theme",
    "ThemeMode",
    "apply_theme_overrides",
    "get_theme",
]
