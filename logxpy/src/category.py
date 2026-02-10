"""Category Management - CodeSite-compatible with color/icon support.

Categories in logxpy work through action_type prefixes which determine
icons in the tree viewer. This module provides category context management.
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Any

from .logx import log, Logger

# Thread-local storage for current category
_local = threading.local()


def get_current_category() -> str | None:
    """Get the current category from thread-local storage."""
    return getattr(_local, "category", None)


def set_category(category: str | None) -> str | None:
    """Set the current category for this thread.
    
    Args:
        category: Category name or None to clear
        
    Returns:
        Previous category value
    """
    old = get_current_category()
    _local.category = category
    return old


@contextmanager
def category_context(category: str):
    """Context manager for category scope.
    
    Args:
        category: Category to use within this context
        
    Example:
        with category_context("database"):
            log.info("Query executed")  # Action type will be "database:info"
            with start_action("query:select"):  # Will be "database:query:select"
                pass
    """
    old = set_category(category)
    try:
        yield category
    finally:
        set_category(old)


class CategorizedLogger:
    """Logger with category prefix support.
    
    Similar to CodeSite.Category - all messages get category prefix.
    """
    
    def __init__(self, category: str, parent: Logger | None = None):
        self.category = category
        self._parent = parent or log
        
        # Category color (maps to log levels in viewer)
        self._color = None
        self._back_color = None
        self._fore_color = None
        self._font_color = None
    
    def _prefix(self, action_type: str) -> str:
        """Add category prefix to action type."""
        if ":" in action_type:
            return f"{self.category}:{action_type}"
        return f"{self.category}:{action_type}"
    
    def _log_with_category(self, level_method: str, msg: str, **fields) -> "CategorizedLogger":
        """Internal: log with category in message_type."""
        # Get the method from parent logger
        method = getattr(self._parent, level_method)
        # Add category to fields
        fields["_category"] = self.category
        method(msg, **fields)
        return self
    
    # Level methods
    def debug(self, msg: str, **f) -> "CategorizedLogger":
        return self._log_with_category("debug", msg, **f)
    
    def info(self, msg: str, **f) -> "CategorizedLogger":
        return self._log_with_category("info", msg, **f)
    
    def success(self, msg: str, **f) -> "CategorizedLogger":
        return self._log_with_category("success", msg, **f)
    
    def note(self, msg: str, **f) -> "CategorizedLogger":
        return self._log_with_category("note", msg, **f)
    
    def warning(self, msg: str, **f) -> "CategorizedLogger":
        return self._log_with_category("warning", msg, **f)
    
    def error(self, msg: str, **f) -> "CategorizedLogger":
        return self._log_with_category("error", msg, **f)
    
    def critical(self, msg: str, **f) -> "CategorizedLogger":
        return self._log_with_category("critical", msg, **f)
    
    def send(self, msg: str, data: Any = None, **f) -> "CategorizedLogger":
        f["_category"] = self.category
        self._parent.send(msg, data, **f)
        return self
    
    # Category color methods (CodeSite compatibility)
    def set_color(self, color: str) -> "CategorizedLogger":
        """Set category color hint (stored, viewer may use)."""
        self._color = color
        return self
    
    def set_back_color(self, color: str) -> "CategorizedLogger":
        """Set background color hint."""
        self._back_color = color
        return self
    
    def set_fore_color(self, color: str) -> "CategorizedLogger":
        """Set foreground color hint."""
        self._fore_color = color
        return self
    
    def set_font_color(self, color: str) -> "CategorizedLogger":
        """Set font color hint."""
        self._font_color = color
        return self
    
    # Context manager for actions
    def action(self, action_type: str, **fields):
        """Create action with category prefix."""
        from ._action import start_action
        prefixed = self._prefix(action_type)
        return start_action(action_type=prefixed, _category=self.category, **fields)
    
    # Child logger
    def child(self, subcategory: str) -> "CategorizedLogger":
        """Create child logger with subcategory."""
        return CategorizedLogger(f"{self.category}:{subcategory}", self._parent)
    
    def __call__(self, msg: str, **f) -> "CategorizedLogger":
        return self.info(msg, **f)


# Convenience factory
def get_categorized_logger(category: str) -> CategorizedLogger:
    """Get or create a categorized logger.
    
    Args:
        category: Category name
        
    Returns:
        CategorizedLogger instance
    """
    return CategorizedLogger(category)


# CodeSite-style aliases
class CategoryManager:
    """CodeSite.Category compatibility class."""
    
    def __init__(self):
        self._logger: CategorizedLogger | None = None
        self._name: str | None = None
    
    def __call__(self, name: str | None = None) -> CategorizedLogger:
        """Set or get category.
        
        Args:
            name: Category name to set, or None to get current
            
        Returns:
            CategorizedLogger instance
        """
        if name is not None:
            self._name = name
            self._logger = CategorizedLogger(name)
        return self._logger or CategorizedLogger("default")
    
    @property
    def current(self) -> str | None:
        """Get current category name."""
        return self._name
    
    # Color properties (CodeSite compatibility)
    @property
    def color(self) -> str | None:
        return self._logger._color if self._logger else None
    
    @color.setter
    def color(self, value: str):
        if self._logger:
            self._logger.set_color(value)
    
    @property
    def back_color(self) -> str | None:
        return self._logger._back_color if self._logger else None
    
    @back_color.setter
    def back_color(self, value: str):
        if self._logger:
            self._logger.set_back_color(value)
    
    @property
    def fore_color(self) -> str | None:
        return self._logger._fore_color if self._logger else None
    
    @fore_color.setter
    def fore_color(self, value: str):
        if self._logger:
            self._logger.set_fore_color(value)
    
    @property
    def font_color(self) -> str | None:
        return self._logger._font_color if self._logger else None
    
    @font_color.setter
    def font_color(self, value: str):
        if self._logger:
            self._logger.set_font_color(value)


# Global category manager (like CodeSite global)
Category = CategoryManager()

# CodeSite-style aliases for module level
def set_category(name: str) -> CategorizedLogger:
    """Set global category (CodeSite.Category := name)."""
    return Category(name)


def get_category() -> str | None:
    """Get current category name."""
    return Category.current


# Monkey-patch Logger to add category methods
def with_category(self, category: str) -> CategorizedLogger:
    """Create categorized logger from this logger.
    
    Args:
        category: Category name
        
    Returns:
        CategorizedLogger
    """
    return CategorizedLogger(category, self)


Logger.with_category = with_category
Logger.category = lambda self, name: self.with_category(name)

__all__ = [
    "CategorizedLogger",
    "CategoryManager",
    "Category",
    "category_context",
    "get_current_category",
    "set_category",
    "get_categorized_logger",
    "set_category",
    "get_category",
]
