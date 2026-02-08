"""
LogXPy Log Parser & Analyzer

A Python library for parsing, analyzing, and querying LogXPy log files.

SIMPLE ONE-LINE API (recommended for logxpy logs):
    >>> from logxy_log_parser import parse_log, check_log, analyze_log
    >>> 
    >>> # One line to parse
    >>> entries = parse_log("app.log")
    >>> 
    >>> # One line to parse + validate  
    >>> result = check_log("app.log")
    >>> 
    >>> # One line to parse + validate + analyze
    >>> report = analyze_log("app.log")
    >>> report.print_summary()

FULL API:
    >>> from logxy_log_parser import LogParser, LogFilter
    >>> parser = LogParser("app.log")
    >>> logs = parser.parse()
    >>> errors = LogFilter(logs).by_level("error")
    >>> errors.to_html("errors.html")
"""

from __future__ import annotations

from typing import Any

__version__ = "0.1.0"

# SIMPLE ONE-LINE API (import these for easiest use)
from .simple import (
    # Core classes
    LogXPyEntry,
    ParseResult,
    CheckResult,
    LogStats,
    AnalysisReport,
    # One-line functions
    parse_log,
    parse_line,
    check_log,
    analyze_log,
)

# Core API
from .analyzer import (
    ActionStat,
    DurationStats,
    ErrorSummary,
    LogAnalyzer,
)
from .core import LogEntry, LogParser, ParseError
from .filter import LogEntries, LogFilter
from .monitor import LogFile, LogFileError
from .tree import TaskNode, TaskTree
from .types import ActionStatus, Level, TaskLevel
from .utils import (
    bucketize,
    chunked,
    extract_task_uuid,
    first,
    flatten,
    format_timestamp,
    is_iterable,
    level_from_message_type,
    merge_fields,
    pairwise,
    parse_duration,
    parse_timestamp,
    subdict,
    unique,
    windowed,
)

# Indexing
from .index import (
    IndexedLogParser,
    IndexStats,
    LogIndex,
    LogPosition,
)

# Aggregation
from .aggregation import (
    AggregatedStats,
    LogAggregator,
    MultiFileAnalyzer,
    TimeBucket,
    TimeSeriesAnalyzer,
)

# Configuration
from .config import (
    ConfigManager,
    ParserConfig,
    get_config,
)

# CLI (optional)
try:
    from .cli import main as _cli_main
    main = _cli_main
    _cli_available = True
except ImportError:
    _cli_available = False
    main = None  # type: ignore

__all__ = [
    # Version
    "__version__",
    # SIMPLE API (one-line parsing)
    "parse_log",
    "parse_line",
    "check_log",
    "analyze_log",
    "LogXPyEntry",
    "ParseResult",
    "CheckResult",
    "LogStats",
    "AnalysisReport",
    # Core
    "LogEntry",
    "LogParser",
    "ParseError",
    # Monitoring
    "LogFile",
    "LogFileError",
    # Filtering
    "LogEntries",
    "LogFilter",
    # Analysis
    "LogAnalyzer",
    "ActionStat",
    "DurationStats",
    "ErrorSummary",
    # Tree
    "TaskNode",
    "TaskTree",
    # Types
    "Level",
    "ActionStatus",
    "TaskLevel",
    # Utils
    "parse_timestamp",
    "format_timestamp",
    "parse_duration",
    "level_from_message_type",
    "extract_task_uuid",
    "merge_fields",
    "subdict",
    # boltons utilities (re-exported)
    "bucketize",
    "chunked",
    "first",
    "flatten",
    "is_iterable",
    "pairwise",
    "unique",
    "windowed",
    # Indexing
    "LogIndex",
    "IndexedLogParser",
    "IndexStats",
    "LogPosition",
    # Aggregation
    "AggregatedStats",
    "LogAggregator",
    "MultiFileAnalyzer",
    "TimeBucket",
    "TimeSeriesAnalyzer",
    # Configuration
    "ConfigManager",
    "ParserConfig",
    "get_config",
    # CLI
    "main",
]

# Optional pandas support
try:
    import pandas as _pd  # type: ignore  # noqa: F401

    _pandas_available = True
except ImportError:
    _pandas_available = False

# Optional rich support
try:
    import rich as _rich  # noqa: F401

    _rich_available = True
except ImportError:
    _rich_available = False


def __getattr__(name: str) -> Any:
    """Lazy import for optional dependencies."""
    if name == "to_dataframe" and not _pandas_available:
        raise ImportError(
            "pandas is required for DataFrame export. "
            "Install with: pip install logxy-log-parser[pandas]"
        )
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
