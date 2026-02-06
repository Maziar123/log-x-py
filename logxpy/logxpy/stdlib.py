"""Integration with the standard library ``logging`` package."""

from logging import Handler

from ._action import log_message
from ._traceback import write_traceback


class LogXPyHandler(Handler):
    """A C{logging.Handler} that routes log messages to LogXPy."""

    def emit(self, record):
        log_message(
            message_type="eliot:stdlib",
            log_level=record.levelname,
            logger=record.name,
            message=record.getMessage(),
        )
        if record.exc_info:
            write_traceback(exc_info=record.exc_info)


__all__ = ["LogXPyHandler", "EliotHandler"]  # EliotHandler kept for compatibility
