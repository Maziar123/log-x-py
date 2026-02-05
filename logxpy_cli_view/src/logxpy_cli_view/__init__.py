"""Eliot Tree - Render Eliot logs as an ASCII tree."""

from logxpy_cli_view._color import color_factory, colored, no_color
from logxpy_cli_view._compat import catch_errors, deprecated, dump_json_bytes
from logxpy_cli_view._errors import ConfigError, EliotParseError, JSONParseError
from logxpy_cli_view._export import (
    EXPORT_FORMATS,
    ExportOptions,
    export_csv,
    export_html,
    export_json,
    export_logfmt,
    export_tasks,
)
from logxpy_cli_view._parse import parser_context, tasks_from_iterable
from logxpy_cli_view._patterns import (
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
)
from logxpy_cli_view._render import (
    DEFAULT_IGNORED_KEYS,
    ColorizedOptions,
    NodeFormatter,
    format_node,
    get_children,
    message_fields,
    message_name,
    render_tasks,
    track_exceptions,
)
from logxpy_cli_view._stats import (
    TaskStatistics,
    TimeSeriesData,
    calculate_statistics,
    create_time_series,
    print_statistics,
)
from logxpy_cli_view._tail import (
    LiveDashboard,
    LogTailer,
    tail_logs,
    watch_and_aggregate,
)
from logxpy_cli_view._theme import (
    DarkBackgroundTheme,
    LightBackgroundTheme,
    Theme,
    ThemeMode,
    apply_theme_overrides,
    get_theme,
)
from logxpy_cli_view._util import (
    Writable,
    _Namespace,
    eliot_ns,
    format_namespace,
    is_namespace,
    namespaced,
)
from logxpy_cli_view.filter import (
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
)
from logxpy_cli_view.format import (
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
)

try:
    from eliottree2._version import __version__
except ImportError:
    __version__ = "unknown"

__all__ = [
    # Version
    "__version__",
    # Errors
    "ConfigError",
    "EliotParseError",
    "JSONParseError",
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
