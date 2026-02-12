"""
LogXPy: Modern Structured Logging for Python 3.12+

Forked from Eliot (https://github.com/itamarst/eliot).
Modernized with Python 3.12+ features: type aliases, pattern matching,
dataclass slots, and StrEnum.

Enhanced with boltons library for efficient caching, dict operations,
iteration, and string processing.

Source code lives in logxpy/src/. This __init__.py re-exports the public API.
"""

from __future__ import annotations

from typing import Any
from warnings import warn

# Expose the public API from src subpackage:
from .src._message import Message
from .src._action import (
    Action,
    current_action,
    preserve_context,
    start_action,
    startTask,
)
from .src._compat import log_call, log_message
from .src._async import aaction
from .src._output import FileDestination, ILogger, Logger, MemoryLogger, init_file_destination, to_file
from .src._traceback import write_traceback, writeFailure
from .src._validation import ActionType, Field, MessageType, ValidationError, fields
from .src.logx import log

# Writer classes (choose-L2 based)
from .src._writer import (
    Mode,
    WriterType,
    QueuePolicy,
    BaseFileWriterThread,
    LineBufferedWriter,
    BlockBufferedWriter,
    MemoryMappedWriter,
    create_writer,
    Q,
)

# System info module
from .src.system_info import (
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

# File and Stream Operations
from .src.file_stream import (
    send_file_as_hex,
    send_text_file,
    send_stream_as_hex,
    send_stream_as_text,
    send_bytes,
    send_file_info,
    SendFileAsHex,
    SendTextFile,
    SendStreamAsHex,
    SendStreamAsText,
)

# Data Type Specific
from .src.data_types import (
    send_color,
    send_currency,
    send_datetime,
    send_datetime_if,
    send_enum,
    send_set,
    send_pointer,
    send_variant,
    send_if,
    send_assigned,
    send_fmt_msg,
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
from .src.category import (
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
from .src._types import (
    Level,
    LevelName,
    ActionStatusStr,
    Record,
    TS, TID, LVL, MT, AT, ST, DUR, MSG,
    TASK_UUID,
    TASK_LEVEL,
    TIMESTAMP,
    MESSAGE_TYPE,
    ACTION_TYPE,
    ACTION_STATUS,
    DURATION_NS,
    get_level_name,
    get_level_value,
    TaskLevel,
)
from .src._action import (
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


def use_asyncio_context():
    warn(
        "This function is no longer needed.",
        DeprecationWarning,
        stacklevel=2,
    )


# Async logging support - using choose-L2 based writer
from .src._writer import (
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

# Backward compatible aliases
AsyncWriter = BaseFileWriterThread
AsyncMetrics = WriterMetrics
create_default_writer = create_writer

# Sqid support (ultra-short task IDs)
from .src._sqid import (
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
    from .src.parse import Parser
    del Parser
    import sys
    current_module = sys.modules.get("logxpy.src.parse")
    if current_module:
        sys.modules["logxpy.parse"] = current_module
        sys.modules["logxpy._parse"] = current_module
        return current_module
    return None


_parse = _parse_compat()
del _parse_compat


__all__ = [
    "Message",
    "writeTraceback", "writeFailure", "startAction", "startTask",
    "Action", "preserve_context",
    "Field", "fields", "MessageType", "ActionType",
    "ILogger", "Logger", "MemoryLogger",
    "addDestination", "removeDestination", "addGlobalFields",
    "FileDestination", "current_action",
    "use_asyncio_context", "ValidationError",
    "write_traceback", "write_failure",
    "start_action", "start_task",
    "add_destination", "add_destinations",
    "remove_destination", "add_global_fields",
    "to_file", "log_call", "log_message",
    "__version__", "log", "aaction",
    # System info
    "send_system_info", "send_memory_status", "send_heap_status",
    "send_memory_manager_status", "send_memory_as_hex",
    "send_stack_trace", "send_exception_trace",
    "send_window_handle", "send_screenshot", "send_parents",
    "SendSystemInfo", "SendMemoryStatus", "SendHeapStatus",
    "SendMemoryManagerStatus", "SendMemoryAsHex", "SendStackTrace",
    "SendWindowHandle", "SendScreenshot", "SendParents",
    # File and Stream
    "send_file_as_hex", "send_text_file",
    "send_stream_as_hex", "send_stream_as_text",
    "send_bytes", "send_file_info",
    "SendFileAsHex", "SendTextFile", "SendStreamAsHex", "SendStreamAsText",
    # Data Types
    "send_color", "send_currency", "send_datetime", "send_datetime_if",
    "send_enum", "send_set", "send_pointer", "send_variant",
    "send_if", "send_assigned", "send_fmt_msg",
    "SendColor", "SendCurrency", "SendDateTime", "SendDateTimeIf",
    "SendEnum", "SendSet", "SendPointer", "SendVariant",
    "SendIf", "SendAssigned", "SendFmtMsg",
    # Category Management
    "CategorizedLogger", "CategoryManager", "Category",
    "category_context", "get_current_category", "set_category",
    "get_categorized_logger", "get_category",
    # Types & Constants
    "Level", "LevelName", "ActionStatusStr", "Record",
    "TS", "TID", "LVL", "MT", "AT", "ST", "DUR", "MSG",
    "TASK_UUID", "TASK_LEVEL", "TIMESTAMP", "MESSAGE_TYPE",
    "ACTION_TYPE", "ACTION_STATUS", "DURATION_NS",
    "get_level_name", "get_level_value",
    "ActionStatus", "TaskLevel",
    "STARTED_STATUS", "SUCCEEDED_STATUS", "FAILED_STATUS", "VALID_STATUSES",
    "_parse",
    # Boltons utilities (lazy)
    "truncate", "strip_ansi_codes", "escape_html_text",
    "pluralize", "clean_text", "get_first", "is_non_string_iterable",
    "memoize", "memoize_method", "throttle", "CacheStats",
    # Async logging / Writer (choose-L2 based)
    "Q", "Mode", "WriterType", "QueuePolicy",
    "WriterMetrics", "BaseFileWriterThread",
    "LineBufferedWriter", "BlockBufferedWriter", "MemoryMappedWriter",
    "create_writer", "create_default_writer",
    # Backward compatible aliases (clean API)
    "AsyncWriter", "AsyncMetrics", "create_default_writer",
    # Sqid
    "SqidGenerator", "sqid", "child_sqid", "generate_task_id",
]


from .src import _version

__version__ = _version.get_versions()["version"]


# ============================================================================
# Python 3.12+ & Boltons-Enhanced Utilities (Lazy Export)
# ============================================================================
_BOLTONS_UTILITY_MODULES = {
    'truncate': '_base',
    'strip_ansi_codes': '_base',
    'escape_html_text': '_base',
    'pluralize': '_base',
    'clean_text': '_base',
    'get_first': '_base',
    'is_non_string_iterable': '_base',
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
            from .src import _base
            return getattr(_base, name)
        from .src import _cache
        return getattr(_cache, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
