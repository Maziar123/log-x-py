"""
LogXPy: Modern Structured Logging for Python 3.12+

Forked from Eliot (https://github.com/itamarst/eliot).
Modernized with Python 3.12+ features: type aliases, pattern matching,
dataclass slots, and StrEnum.
"""

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
from ._output import FileDestination, ILogger, Logger, MemoryLogger, to_file
from ._traceback import write_traceback, writeFailure
from ._validation import ActionType, Field, MessageType, ValidationError, fields
from .loggerx import log

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
    "register_exception_extractor",
    "current_action",
    "use_asyncio_context",
    "ValidationError",
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
    # Tree viewer compatibility:
    "_parse",
]


from . import _version

__version__ = _version.get_versions()["version"]
