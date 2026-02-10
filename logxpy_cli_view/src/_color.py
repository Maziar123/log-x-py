"""Color utilities for eliot-tree."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import colored as _colored_module


def _get_color_code(color_name: str | None, is_background: bool = False) -> str:
    """Get ANSI color code from name."""
    if not color_name:
        return ""
    
    color_name = color_name.lower()
    
    # Map color names to colored module attributes
    if is_background:
        color_map = {
            "red": _colored_module.Back.RED,
            "green": _colored_module.Back.GREEN,
            "blue": _colored_module.Back.BLUE,
            "yellow": _colored_module.Back.YELLOW,
            "magenta": _colored_module.Back.MAGENTA,
            "cyan": _colored_module.Back.CYAN,
            "white": _colored_module.Back.WHITE,
            "black": _colored_module.Back.BLACK,
            "light_gray": _colored_module.Back.LIGHT_GRAY,
            "dark_gray": _colored_module.Back.DARK_GRAY,
            "light_red": _colored_module.Back.LIGHT_RED,
            "light_green": _colored_module.Back.LIGHT_GREEN,
            "light_blue": _colored_module.Back.LIGHT_BLUE,
            "light_yellow": _colored_module.Back.LIGHT_YELLOW,
            "light_magenta": _colored_module.Back.LIGHT_MAGENTA,
            "light_cyan": _colored_module.Back.LIGHT_CYAN,
        }
    else:
        color_map = {
            "red": _colored_module.Fore.RED,
            "green": _colored_module.Fore.GREEN,
            "blue": _colored_module.Fore.BLUE,
            "yellow": _colored_module.Fore.YELLOW,
            "magenta": _colored_module.Fore.MAGENTA,
            "cyan": _colored_module.Fore.CYAN,
            "white": _colored_module.Fore.WHITE,
            "black": _colored_module.Fore.BLACK,
            "light_gray": _colored_module.Fore.LIGHT_GRAY,
            "dark_gray": _colored_module.Fore.DARK_GRAY,
            "light_red": _colored_module.Fore.LIGHT_RED,
            "light_green": _colored_module.Fore.LIGHT_GREEN,
            "light_blue": _colored_module.Fore.LIGHT_BLUE,
            "light_yellow": _colored_module.Fore.LIGHT_YELLOW,
            "light_magenta": _colored_module.Fore.LIGHT_MAGENTA,
            "light_cyan": _colored_module.Fore.LIGHT_CYAN,
        }
    
    return color_map.get(color_name, "")


def _get_style_code(style_name: str) -> str:
    """Get ANSI style code from name."""
    style_map = {
        "bold": _colored_module.Style.BOLD,
        "dim": _colored_module.Style.DIM,
        "underline": _colored_module.Style.UNDERLINE,
        "blink": _colored_module.Style.BLINK,
        "reverse": _colored_module.Style.REVERSE,
        "hidden": _colored_module.Style.HIDDEN,
    }
    return style_map.get(style_name.lower(), "")


def color_factory(
    colored_func: Callable[..., str] | None = None,
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
            
            # Build formatting string by combining codes
            formatting = ""
            if foreground:
                formatting += _get_color_code(foreground, is_background=False)
            if background:
                formatting += _get_color_code(background, is_background=True)
            if attrs:
                for attr in attrs:
                    formatting += _get_style_code(attr)
            
            if not formatting:
                return text
            
            return _colored_module.stylize(text, formatting)
        
        return colorize
    
    return factory


def colored(text: str, *args: Any, **kwargs: Any) -> str:
    """Wrapper around colored.stylize."""
    return _colored_module.stylize(text, *args, **kwargs)


def no_color(text: str, *args: Any, **kwargs: Any) -> str:
    """No-op color function."""
    return text


__all__ = ["color_factory", "colored", "no_color"]
