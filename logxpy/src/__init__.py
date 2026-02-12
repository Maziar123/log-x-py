"""
LogXPy: Modern Structured Logging for Python 3.12+

Forked from Eliot (https://github.com/itamarst/eliot).
Modernized with Python 3.12+ features: type aliases, pattern matching,
dataclass slots, and StrEnum.

Enhanced with boltons library for efficient caching, dict operations,
iteration, and string processing.
"""

from __future__ import annotations

from typing import Any
from warnings import warn

# Expose the public API:
from ._message import Message
from ._action import (
    Action,
    current_action,
    preserve_context,
    start_action,
    startTask,
)
from ._compat import log_call, log_message
from ._async import aaction
from ._output import FileDestination, ILogger, Logger, MemoryLogger, init_file_destination, to_file
from ._traceback import write_traceback, writeFailure
from ._validation import ActionType, Field, MessageType, ValidationError, fields
from .logx import log

# System info module (lazy import support)
from .system_info import (
    send_system_info,
    send_memory_status,
    send_heap_status,
    send_memory_manager_status,
    send_memory_as_hex,
    send_stack_trace,
    send_exception_trace,
    send_window_handle,
    send_screenshot,
    send_parents,
    # CodeSite-style aliases
    SendSystemInfo,
    SendMemoryStatus,
    SendHeapStatus,
    SendMemoryManagerStatus,
    SendMemoryAsHex,
    SendStackTrace,
    SendWindowHandle,
    SendScreenshot,
    SendParents,
)

# File and Stream Operations (lazy import support)
from .file_stream import (
    send_file_as_hex,
    send_text_file,
    send_stream_as_hex,
    send_stream_as_text,
    send_bytes,
    send_file_info,
    # CodeSite-style aliases
    SendFileAsHex,
    SendTextFile,
    SendStreamAsHex,
    SendStreamAsText,
)

# Data Type Specific (lazy import support)
from .data_types import (
    send_color,
    send_currency,
    send_datetime,
    send_datetime_if,
    send_enum,
    send_set,
    send_pointer,
    send_variant,
    # Conditional & Formatted Sending
    send_if,
    send_assigned,
    send_fmt_msg,
    # CodeSite-style aliases
    SendColor,
    SendCurrency,
    SendDateTime,
    SendDateTimeIf,
    SendEnum,
    SendSet,
    SendPointer,
    SendVariant,
    SendIf,
    SendAssigned,
    SendFmtMsg,
)

# Category Management
from .category import (
    CategorizedLogger,
    CategoryManager,
    Category,
    category_context,
    get_current_category,
    set_category,
    get_categorized_logger,
    get_category,
)

# Python 3.12+ & Boltons-Enhanced Utilities
# Import these after module initialization to avoid circular import issues
# They are exposed via __getattr__ below
from ._types import (
    Level,
    LevelName,
    ActionStatusStr,
    Record,
    # Compact field names (recommended)
    TS, TID, LVL, MT, AT, ST, DUR, MSG,
    # Legacy aliases (backwards compatible)
    TASK_UUID,
    TASK_LEVEL,
    TIMESTAMP,
    MESSAGE_TYPE,
    ACTION_TYPE,
    ACTION_STATUS,
    DURATION_NS,
    get_level_name,
    get_level_value,
    # Also export TaskLevel from _types (moved to break circular import)
    TaskLevel,
)
# From _action: StrEnum and backward compat constants
from ._action import (
    ActionStatus,
    STARTED_STATUS,
    SUCCEEDED_STATUS,
    FAILED_STATUS,
    VALID_STATUSES,
)


# Backwards compatibility:
def add_destination(destination):
    warn(
        "add_destination is deprecated since 1.1.0. Use add_destinations instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    Logger._destinations.add(destination)


# Backwards compatibility:
def use_asyncio_context():
    warn(
        "This function is no longer needed.",
        DeprecationWarning,
        stacklevel=2,
    )


# Async logging support - using choose-L2 based writer
# Force refactor: clean design, no backward compatibility for internal APIs
from ._writer import (
    # Core classes
    Q, 
    Mode,
    WriterType,
    QueuePolicy,
    WriterMetrics,
    BaseFileWriterThread,
    # Writer implementations
    LineBufferedWriter,
    BlockBufferedWriter,
    MemoryMappedWriter,
    # Factory
    create_writer,
)

# Backward compatible aliases (clean API - no deprecation)
AsyncWriter = BaseFileWriterThread
AsyncMetrics = WriterMetrics

# Factory function alias
create_default_writer = create_writer

# Sqid support (ultra-short task IDs)
from ._sqid import (
    SqidGenerator,
    sqid,
    child_sqid,
    generate_task_id,
)

# Backwards compatibilty:
addDestination = add_destination
removeDestination = Logger._destinations.remove
addGlobalFields = Logger._destinations.addGlobalFields
writeTraceback = write_traceback
startAction = start_action

# PEP 8 variants:
start_task = startTask
write_failure = writeFailure
add_destinations = Logger._destinations.add
remove_destination = removeDestination
add_global_fields = addGlobalFields


# Backwards compatibility for tree viewers that rely on _parse:
def _parse_compat():
    # Force parse module to be imported in way that works with old Python:
    from .parse import Parser

    del Parser
    import sys

    # Map logxpy.parse for compatibility
    current_module = sys.modules.get("logxpy.parse")
    if current_module:
        sys.modules["logxpy._parse"] = current_module
        return current_module
    return None


_parse = _parse_compat()
del _parse_compat


__all__ = [
    # Core logging
    "Message",
    "writeTraceback",
    "writeFailure",
    "startAction",
    "startTask",
    "Action",
    "preserve_context",
    "Field",
    "fields",
    "MessageType",
    "ActionType",
    "ILogger",
    "Logger",
    "MemoryLogger",
    "addDestination",
    "removeDestination",
    "addGlobalFields",
    "FileDestination",
    "current_action",
    "use_asyncio_context",
    "ValidationError",
    # Async logging / Writer (choose-L2 based)
    "Q",
    "Mode",
    "WriterType",
    "QueuePolicy",
    "WriterMetrics",
    "BaseFileWriterThread",
    "LineBufferedWriter",
    "BlockBufferedWriter",
    "MemoryMappedWriter",
    "create_writer",
    "create_default_writer",
    # Backward compatible aliases
    "AsyncWriter",
    "AsyncMetrics",
    # PEP 8 variants:
    "write_traceback",
    "write_failure",
    "start_action",
    "start_task",
    "add_destination",
    "add_destinations",
    "remove_destination",
    "add_global_fields",
    "to_file",
    "log_call",
    "log_message",
    "__version__",
    "log",
    "aaction",
    # System info (CodeSite-compatible)
    "send_system_info",
    "send_memory_status",
    "send_heap_status",
    "send_memory_manager_status",
    "send_memory_as_hex",
    "send_stack_trace",
    "send_exception_trace",
    "send_window_handle",
    "send_screenshot",
    "send_parents",
    # CodeSite-style aliases
    "SendSystemInfo",
    "SendMemoryStatus",
    "SendHeapStatus",
    "SendMemoryManagerStatus",
    "SendMemoryAsHex",
    "SendStackTrace",
    "SendWindowHandle",
    "SendScreenshot",
    "SendParents",
    # File and Stream (CodeSite-compatible)
    "send_file_as_hex",
    "send_text_file",
    "send_stream_as_hex",
    "send_stream_as_text",
    "send_bytes",
    "send_file_info",
    # CodeSite-style aliases
    "SendFileAsHex",
    "SendTextFile",
    "SendStreamAsHex",
    "SendStreamAsText",
    # Data Types (CodeSite-compatible)
    "send_color",
    "send_currency",
    "send_datetime",
    "send_datetime_if",
    "send_enum",
    "send_set",
    "send_pointer",
    "send_variant",
    # Conditional & Formatted Sending
    "send_if",
    "send_assigned",
    "send_fmt_msg",
    # CodeSite-style aliases
    "SendColor",
    "SendCurrency",
    "SendDateTime",
    "SendDateTimeIf",
    "SendEnum",
    "SendSet",
    "SendPointer",
    "SendVariant",
    "SendIf",
    "SendAssigned",
    "SendFmtMsg",
    # Category Management
    "CategorizedLogger",
    "CategoryManager",
    "Category",
    "category_context",
    "get_current_category",
    "set_category",
    "get_categorized_logger",
    "get_category",
    # Python 3.12+ & Boltons-Enhanced Utilities
    "Level",
    "LevelName",
    "ActionStatusStr",
    "Record",
    # Compact field names
    "TS", "TID", "LVL", "MT", "AT", "ST", "DUR", "MSG",
    # Legacy aliases
    "TASK_UUID",
    "TASK_LEVEL",
    "TIMESTAMP",
    "MESSAGE_TYPE",
    "ACTION_TYPE",
    "ACTION_STATUS",
    "DURATION_NS",
    "get_level_name",
    "get_level_value",
    "ActionStatus",
    "TaskLevel",
    "STARTED_STATUS",
    "SUCCEEDED_STATUS",
    "FAILED_STATUS",
    "VALID_STATUSES",
    # Tree viewer compatibility:
    "_parse",
    # Boltons-enhanced utilities (lazy loaded via __getattr__)
    "truncate",  # noqa: E0603
    "strip_ansi_codes",  # noqa: E0603
    "escape_html_text",  # noqa: E0603
    "pluralize",  # noqa: E0603
    "clean_text",  # noqa: E0603
    "get_first",  # noqa: E0603
    "is_non_string_iterable",  # noqa: E0603
    "memoize",  # noqa: E0603
    "memoize_method",  # noqa: E0603
    "throttle",  # noqa: E0603
    "CacheStats",  # noqa: E0603
    # Sqid support (ultra-short task IDs)
    "SqidGenerator",
    "sqid",
    "child_sqid",
    "generate_task_id",
]


from . import _version

__version__ = _version.get_versions()["version"]


# ============================================================================
# Python 3.12+ & Boltons-Enhanced Utilities (Lazy Export)
# ============================================================================
# These are exported via __getattr__ to avoid circular import issues

_BOLTONS_UTILITY_MODULES = {
    # From _base module
    'truncate': '_base',
    'strip_ansi_codes': '_base',
    'escape_html_text': '_base',
    'pluralize': '_base',
    'clean_text': '_base',
    'get_first': '_base',
    'is_non_string_iterable': '_base',
    # From _cache module
    'memoize': '_cache',
    'memoize_method': '_cache',
    'throttle': '_cache',
    'CacheStats': '_cache',
}


def __getattr__(name: str) -> Any:
    """Lazy import for boltons utilities to avoid circular imports."""
    if name in _BOLTONS_UTILITY_MODULES:
        module_name = _BOLTONS_UTILITY_MODULES[name]
        if module_name == '_base':
            from . import _base
            return getattr(_base, name)
        from . import _cache
        return getattr(_cache, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
