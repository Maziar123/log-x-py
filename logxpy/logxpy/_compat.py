"""Eliot backward compatibility - re-export ALL logxpy APIs with deprecation notices."""

from warnings import warn

from ._action import (
    log_call as _log_call,
)
from ._action import (
    log_message as _log_message,
)
from ._action import (
    start_action,
    startTask,
)

# === Re-export ALL logxpy public APIs (from eliot/__init__.py __all__) ===
from ._output import (
    Logger,
)
from ._traceback import write_traceback, writeFailure

# === Backward compat aliases (same as eliot/__init__.py) ===
startAction = start_action
start_task = startTask
write_failure = writeFailure
writeTraceback = write_traceback
add_destinations = Logger._destinations.add
remove_destination = Logger._destinations.remove
add_global_fields = Logger._destinations.addGlobalFields


# Deprecated
def add_destination(dest):
    warn("Use add_destinations()", DeprecationWarning, stacklevel=2)
    Logger._destinations.add(dest)


addDestination = add_destination
removeDestination = remove_destination
addGlobalFields = add_global_fields


def use_asyncio_context():
    warn("No longer needed as of Eliot 1.8.0", DeprecationWarning, stacklevel=2)


# === New LoggerX API ===


# === Deprecation wrappers for common patterns ===
def _deprecated(old: str, new: str):
    def wrapper(fn):
        def inner(*a, **kw):
            warn(f"{old} is deprecated, use {new}", DeprecationWarning, stacklevel=2)
            return fn(*a, **kw)

        return inner

    return wrapper


# Wrap log_call to suggest @log.logged
@_deprecated("log_call", "@log.logged")
def log_call(*a, **kw):
    return _log_call(*a, **kw)


# Wrap log_message to suggest log.info()
@_deprecated("log_message", "log.info()")
def log_message(*a, **kw):
    return _log_message(*a, **kw)
