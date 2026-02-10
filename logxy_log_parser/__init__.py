"""
LogXPy Log Parser & Analyzer

A Python library for parsing, analyzing, and querying LogXPy log files.

Source code lives in logxy_log_parser/src/. This __init__.py re-exports the public API.
"""

from __future__ import annotations

# Re-export the entire public API from src subpackage
from .src import *  # noqa: F401, F403
from .src import __all__, __version__  # noqa: F401


def __getattr__(name: str):
    """Delegate submodule access to src/ subpackage."""
    import importlib  # noqa: C0415

    try:
        return importlib.import_module(f".src.{name}", __name__)
    except ModuleNotFoundError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
