"""
LogXPy CLI View: Render structured logs as an ASCII tree.

Forked from eliottree (https://github.com/jonathanj/eliottree).
Modernized with enhanced features and renamed to logxpy-cli-view.

Source code lives in logxpy_cli_view/src/. This __init__.py re-exports the public API.
"""

from __future__ import annotations

# Re-export the entire public API from src subpackage
from .src import (
    # Version
    __version__,
    # Errors
    ConfigError,
    EliotParseError,
    JSONParseError,
    LogXPyParseError,
    # Theme
    Theme,
    ThemeMode,
    DarkBackgroundTheme,
    LightBackgroundTheme,
    apply_theme_overrides,
    get_theme,
    # Color
    color_factory,
    colored,
    no_color,
    # Utilities
    Writable,
    _Namespace,
    eliot_ns,
    format_namespace,
    is_namespace,
    namespaced,
    # Filter
    combine_filters_and,
    combine_filters_not,
    combine_filters_or,
    filter_by_action_status,
    filter_by_action_type,
    filter_by_duration,
    filter_by_end_date,
    filter_by_field_exists,
    filter_by_jmespath,
    filter_by_keyword,
    filter_by_relative_time,
    filter_by_start_date,
    filter_by_task_level,
    filter_by_uuid,
    filter_sample,
    # Format
    anything,
    binary,
    duration,
    escape_control_characters,
    fields,
    format_any,
    some,
    text,
    timestamp,
    truncate_value,
    # Parsing
    parser_context,
    tasks_from_iterable,
    # Rendering
    DEFAULT_IGNORED_KEYS,
    ColorizedOptions,
    NodeFormatter,
    format_node,
    get_children,
    message_fields,
    message_name,
    render_oneline,
    render_tasks,
    track_exceptions,
    # Export
    ExportOptions,
    EXPORT_FORMATS,
    export_csv,
    export_html,
    export_json,
    export_logfmt,
    export_tasks,
    # Statistics
    TaskStatistics,
    TimeSeriesData,
    calculate_statistics,
    create_time_series,
    print_statistics,
    # Live Tail
    LiveDashboard,
    LogTailer,
    tail_logs,
    watch_and_aggregate,
    # Patterns
    COMMON_PATTERNS,
    LogClassifier,
    PatternExtractor,
    PatternMatch,
    compile_pattern,
    create_common_classifier,
    create_extraction_pipeline,
    extract_emails,
    extract_ips,
    extract_urls,
    extract_uuids,
    # Compatibility
    deprecated,
    catch_errors,
    dump_json_bytes,
)

__all__ = [
    # Version
    "__version__",
    # Errors
    "ConfigError",
    "EliotParseError",
    "JSONParseError",
    "LogXPyParseError",
    # Theme
    "Theme",
    "ThemeMode",
    "DarkBackgroundTheme",
    "LightBackgroundTheme",
    "apply_theme_overrides",
    "get_theme",
    # Color
    "color_factory",
    "colored",
    "no_color",
    # Utilities
    "Writable",
    "_Namespace",
    "eliot_ns",
    "format_namespace",
    "is_namespace",
    "namespaced",
    # Filter
    "combine_filters_and",
    "combine_filters_not",
    "combine_filters_or",
    "filter_by_action_status",
    "filter_by_action_type",
    "filter_by_duration",
    "filter_by_end_date",
    "filter_by_field_exists",
    "filter_by_jmespath",
    "filter_by_keyword",
    "filter_by_relative_time",
    "filter_by_start_date",
    "filter_by_task_level",
    "filter_by_uuid",
    "filter_sample",
    # Format
    "anything",
    "binary",
    "duration",
    "escape_control_characters",
    "fields",
    "format_any",
    "some",
    "text",
    "timestamp",
    "truncate_value",
    # Parsing
    "parser_context",
    "tasks_from_iterable",
    # Rendering
    "DEFAULT_IGNORED_KEYS",
    "ColorizedOptions",
    "NodeFormatter",
    "format_node",
    "get_children",
    "message_fields",
    "message_name",
    "render_tasks",
    "render_oneline",
    "track_exceptions",
    # Export
    "ExportOptions",
    "EXPORT_FORMATS",
    "export_csv",
    "export_html",
    "export_json",
    "export_logfmt",
    "export_tasks",
    # Statistics
    "TaskStatistics",
    "TimeSeriesData",
    "calculate_statistics",
    "create_time_series",
    "print_statistics",
    # Live Tail
    "LiveDashboard",
    "LogTailer",
    "tail_logs",
    "watch_and_aggregate",
    # Patterns
    "COMMON_PATTERNS",
    "LogClassifier",
    "PatternExtractor",
    "PatternMatch",
    "compile_pattern",
    "create_common_classifier",
    "create_extraction_pipeline",
    "extract_emails",
    "extract_ips",
    "extract_urls",
    "extract_uuids",
    # Compatibility
    "deprecated",
    "catch_errors",
    "dump_json_bytes",
]


def __getattr__(name: str):
    """Delegate submodule access to src/ subpackage.

    Allows ``from logxpy_cli_view._cli import main`` to resolve to
    ``logxpy_cli_view.src._cli.main``.
    """
    import importlib  # noqa: C0415

    try:
        return importlib.import_module(f".src.{name}", __name__)
    except ModuleNotFoundError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
