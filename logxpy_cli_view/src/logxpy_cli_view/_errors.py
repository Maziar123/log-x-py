"""Exception classes for logxpy-cli-view."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class JSONParseError(Exception):
    """Exception raised when JSON parsing fails."""

    file_name: str
    line_number: int
    line: str
    exc_info: Any

    def __str__(self) -> str:
        return f"JSON parse error in {self.file_name} at line {self.line_number}"


@dataclass(slots=True)
class LogXPyParseError(Exception):
    """Exception raised when logxpy message parsing fails."""

    message_dict: dict[str, Any]
    exc_info: Any

    def __str__(self) -> str:
        return f"LogXPy message parse error: {self.message_dict}"


# Backwards compatibility alias
EliotParseError = LogXPyParseError


@dataclass(slots=True)
class ConfigError(Exception):
    """Exception raised when configuration is invalid."""

    message: str
    path: str | None = None

    def __str__(self) -> str:
        if self.path:
            return f"Config error in {self.path}: {self.message}"
        return f"Config error: {self.message}"


__all__ = ["ConfigError", "EliotParseError", "JSONParseError", "LogXPyParseError"]
