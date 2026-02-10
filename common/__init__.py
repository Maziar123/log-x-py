"""Common utilities for the LogXPy ecosystem.

This package provides shared types, constants, and utilities across:
- logxpy (logging library)
- logxpy-cli-view (tree viewer)
- logxy-log-parser (log parser)

Modules:
- types: Type aliases, field name constants, enums
- sqid: Sqid generation and parsing
- fields: Field normalization and extraction utilities
- predicates: Common filter predicates
- base: Base utilities (truncate, string, time functions)
- cache: Caching decorators and utilities
- fmt: Data type formatters
- iterutils: Iteration utilities (more-itertools wrappers)
- dictutils: Dict utilities (boltons wrappers)
"""

from __future__ import annotations

# Import base utilities first (they may be needed by other modules)
from . import base
from . import cache
from . import dictutils
from . import fmt
from . import iterutils

# Import specific items from base module
from .base import (
    cachedproperty,
    clean_text,
    escape_html_text,
    get_first,
    get_module,
    is_non_string_iterable,
    monotonic,
    now,
    pluralize,
    strip_ansi_codes,
    truncate,
    uuid as uuid_func,
)

# Import specific items from cache module
from .cache import (
    CacheStats,
    cache_until_invalidation,
    memoize,
    memoize_method,
    throttle,
)

# Import specific items from fmt module
from .fmt import format_value

# Import specific items from dictutils module (boltons wrappers)
from .dictutils import (
    FrozenDict,
    ManyToMany,
    OneToOne,
    OrderedMultiDict,
    get_nested,
    set_nested,
)

# Import specific items from iterutils module (more-itertools wrappers)
from .iterutils import (
    batched,
    bucket,
    chunked,
    consume,
    filter_except,
    first,
    flatten,
    grouper,
    ichunked,
    last,
    map_except,
    nth,
    one,
    pairwise,
    partition,
    peekable,
    seekable,
    sliding_window,
    split_at,
    unique_everseen,
    windowed,
)

# Import specific items from fields module
from .fields import (
    extract_duration,
    extract_task_uuids,
    format_timestamp as format_timestamp_field,
    get_action_status,
    get_action_type,
    get_field_value,
    get_message,
    get_message_type,
    get_task_level,
    get_task_uuid,
    get_timestamp,
    normalize_entry,
    parse_duration,
    parse_timestamp,
)

# Import specific items from predicates module
from .predicates import (
    after,
    by_action_type,
    by_action_type_pattern,
    by_field,
    by_field_contains,
    by_field_exists,
    by_keyword,
    by_level,
    by_message,
    by_nesting_level,
    by_status,
    by_task_uuid,
    by_time_range,
    before,
    combine_and,
    combine_not,
    combine_or,
    has_traceback,
    is_critical,
    is_debug,
    is_error,
    is_failed,
    is_fast,
    is_info,
    is_succeeded,
    is_started,
    is_warning,
    is_slow,
)

# Import specific items from sqid module
from .sqid import (
    SqidGenerator,
    SqidInfo,
    SqidParser,
    child_sqid,
    generate_task_id,
    parse_sqid,
    sqid,
    sqid_depth,
    sqid_parent,
    sqid_root,
)

# Import specific items from types module
from .types import (
    ACTION_STATUS,
    ACTION_STATUS_ALIAS,
    ACTION_TYPE,
    ACTION_TYPE_ALIAS,
    AT,
    ActionStatus,
    ActionStatusStr,
    COMPACT_TO_LEGACY,
    DUR,
    DURATION_NS,
    DURATION_NS_ALIAS,
    ALL_KNOWN_FIELDS,
    LEGACY_TO_COMPACT,
    LVL,
    Level,
    LevelName,
    LevelStr,
    LevelValue,
    LogDict,
    LogEntry,
    LogFormat,
    MESSAGE,
    MESSAGE_TYPE,
    MESSAGE_TYPE_ALIAS,
    MESSAGE_TYPE_PREFIX,
    MSG,
    MT,
    ST,
    TS,
    TID,
    TASK_LEVEL,
    TASK_LEVEL_ALIAS,
    TASK_UUID,
    TASK_UUID_ALIAS,
    TaskLevelTuple,
    TIMESTAMP,
    TIMESTAMP_ALIAS,
    detect_format,
    get_field,
    get_level_name,
    get_level_value,
    is_compact_field,
    is_legacy_field,
    legacy_field_name,
    LEVEL_VALUES,
    normalize_field_name,
)

__all__ = [
    # types module
    "LogEntry", "LogDict", "TaskLevelTuple",
    "TS", "TID", "LVL", "MT", "AT", "ST", "DUR", "MSG",
    "TIMESTAMP", "TASK_UUID", "TASK_LEVEL", "MESSAGE_TYPE",
    "ACTION_TYPE", "ACTION_STATUS", "DURATION_NS", "MESSAGE",
    "LEGACY_TO_COMPACT", "COMPACT_TO_LEGACY", "ALL_KNOWN_FIELDS",
    "Level", "LevelName", "LevelStr", "LevelValue", "LEVEL_VALUES",
    "ActionStatusStr", "ActionStatus",
    "LogFormat", "MESSAGE_TYPE_PREFIX",
    "detect_format", "get_field", "get_level_name", "get_level_value",
    "normalize_field_name", "legacy_field_name",
    "is_compact_field", "is_legacy_field",
    # sqid module
    "SqidGenerator", "SqidParser", "SqidInfo",
    "sqid", "child_sqid", "generate_task_id",
    "parse_sqid", "sqid_parent", "sqid_depth", "sqid_root",
    # fields module
    "get_field_value", "get_timestamp", "get_task_uuid", "get_task_level",
    "get_action_type", "get_action_status", "get_message", "get_message_type",
    "extract_duration", "parse_duration",
    "parse_timestamp", "format_timestamp_field",
    "normalize_entry", "extract_task_uuids",
    # predicates module
    "by_level", "is_debug", "is_info", "is_warning", "is_error", "is_critical",
    "by_action_type", "by_action_type_pattern",
    "by_status", "is_started", "is_succeeded", "is_failed", "has_traceback",
    "by_time_range", "after", "before",
    "by_task_uuid", "by_nesting_level",
    "by_message", "by_keyword", "by_field_exists", "by_field", "by_field_contains",
    "combine_and", "combine_or", "combine_not",
    # base module (re-export commonly used)
    "now", "monotonic", "uuid_func", "truncate", "strip_ansi_codes",
    "escape_html_text", "pluralize", "clean_text", "get_first",
    "is_non_string_iterable", "get_module", "cachedproperty",
    # cache module (re-export commonly used)
    "memoize", "memoize_method", "cache_until_invalidation", "throttle", "CacheStats",
    # fmt module (re-export commonly used)
    "format_value",
    # iterutils module (more-itertools wrappers)
    "chunked", "batched", "ichunked", "bucket", "grouper",
    "filter_except", "map_except", "partition", "split_at",
    "consume", "first", "last", "nth", "one",
    "peekable", "seekable",
    "windowed", "sliding_window",
    "flatten", "pairwise", "unique_everseen",
    # dictutils module (boltons wrappers)
    "OrderedMultiDict", "OneToOne", "ManyToMany", "FrozenDict",
    "get_nested", "set_nested",
]

__version__ = "0.2.0"
