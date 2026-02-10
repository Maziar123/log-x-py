"""
LogXPy Log Parser & Analyzer

A Python library for parsing, analyzing, and querying LogXPy log files.

Supports both:
- New LogXPy compact format (ts, tid, lvl, mt, at, st, dur, msg)
- Legacy Eliot format (timestamp, task_uuid, task_level, etc.)

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

COMPATIBILITY:
    >>> # Works with both compact and legacy formats
    >>> from logxy_log_parser import TS, TID, MT, get_field
    >>> entry = {"ts": 1234567890.0, "tid": "Xa.1", "mt": "info", "msg": "Hello"}
    >>> timestamp = get_field(entry, TS)  # Works with both "ts" and "timestamp"
"""

from __future__ import annotations

from typing import Any

__version__ = "0.1.0"

# Import from common FIRST (first-party imports)
# Sqid task ID parsing
from common.sqid import (
    SqidInfo,
    SqidParser,
    parse_sqid,
    sqid_depth,
    sqid_parent,
    sqid_root,
)
from common.types import (
    ACTION_STATUS,
    ACTION_TYPE,
    AT,
    DUR,
    DURATION_NS,
    LVL,
    MESSAGE,
    MESSAGE_TYPE,
    MSG,
    MT,
    ST,
    TASK_LEVEL,
    TASK_UUID,
    TID,
    TIMESTAMP,
    TS,
    ActionStatus,
    Level,
    LevelValue,
    LogFormat,
    LogFormat as SqidLogFormat,  # Alias for clarity in parser context
    TaskLevelTuple as TaskLevel,  # Alias for backward compatibility
    detect_format,
    get_field,
    is_compact_field,
    is_legacy_field,
    legacy_field_name,
    normalize_field_name,
)

# SIMPLE ONE-LINE API (import these for easiest use)
# Aggregation
from .aggregation import (
    AggregatedStats,
    LogAggregator,
    MultiFileAnalyzer,
    TimeBucket,
    TimeSeriesAnalyzer,
)

# Core API
from .analyzer import (
    ActionStat,
    DurationStats,
    ErrorSummary,
    LogAnalyzer,
)

# Configuration
from .config import (
    ConfigManager,
    ParserConfig,
    get_config,
)
from .core import LogEntry, LogParser, ParseError
from .filter import LogEntries, LogFilter

# Indexing
from .index import (
    IndexedLogParser,
    IndexStats,
    LogIndex,
    LogPosition,
)
from .monitor import LogFile, LogFileError
from .simple import (
    AnalysisReport,
    CheckResult,
    LogStats,
    # One-line functions
    analyze_log,
    check_log,
    parse_line,
    parse_log,
    # Type & count helpers
    count_by,
    group_by,
    types,
)

from .tree import TaskNode, TaskTree
from .utils import (
    bucketize,
    chunked,
    extract_duration,
    extract_task_uuids,
    first,
    flatten,
    format_timestamp,
    get_field_value,
    get_task_level,
    get_task_uuid,
    get_timestamp,
    is_iterable,
    level_from_entry,
    level_from_message_type,
    merge_fields,
    normalize_entry,
    pairwise,
    parse_duration,
    parse_timestamp,
    subdict,
    unique,
    unique_everseen,
    windowed,
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
    "CheckResult",
    "LogStats",
    "AnalysisReport",
    # Type & count helpers
    "count_by",
    "group_by",
    "types",
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
    "LevelValue",
    "ActionStatus",
    "TaskLevel",
    "LogFormat",
    # Field name constants (compact)
    "TS",
    "TID",
    "LVL",
    "MT",
    "AT",
    "ST",
    "DUR",
    "MSG",
    # Field name constants (legacy)
    "TIMESTAMP",
    "TASK_UUID",
    "TASK_LEVEL",
    "MESSAGE_TYPE",
    "ACTION_TYPE",
    "ACTION_STATUS",
    "DURATION_NS",
    "MESSAGE",
    # Field utilities
    "detect_format",
    "get_field",
    "is_compact_field",
    "is_legacy_field",
    "legacy_field_name",
    "normalize_field_name",
    # Utils
    "parse_timestamp",
    "format_timestamp",
    "parse_duration",
    "extract_duration",
    "level_from_message_type",
    "level_from_entry",
    "extract_task_uuids",
    "merge_fields",
    "subdict",
    "normalize_entry",
    "get_field_value",
    "get_timestamp",
    "get_task_uuid",
    "get_task_level",
    # boltons utilities (re-exported)
    "bucketize",
    "chunked",
    "first",
    "flatten",
    "is_iterable",
    "pairwise",
    "unique",
    "unique_everseen",
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
    # Sqid task ID parsing
    "SqidParser",
    "SqidInfo",
    "parse_sqid",
    "sqid_depth",
    "sqid_parent",
    "sqid_root",
    "SqidLogFormat",
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
