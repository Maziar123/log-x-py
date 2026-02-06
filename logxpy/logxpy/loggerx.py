"""Main Logger facade - LoggerX API.

LoggerX provides a modern, fluent API for structured logging.
Part of the logxpy library - a fork of Eliot.
"""

from __future__ import annotations

import traceback
from contextlib import contextmanager
from typing import Any

from . import decorators
from ._action import current_action
from ._async import _emit, current_scope, scope
from ._base import now, uuid
from ._fmt import format_value
from ._output import to_file
from ._types import Level, Record


class Logger:
    """LoggerX-compatible logger with fluent API."""

    __slots__ = ("_context", "_level", "_masker", "_name")

    def __init__(self, name: str = "root", context: dict[str, Any] | None = None):
        self._level = Level.DEBUG
        self._name = name
        self._context = context or {}
        self._masker = None

    # === Level Methods (fluent - return self) ===
    def debug(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.DEBUG, msg, **f)

    def info(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.INFO, msg, **f)

    def success(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.SUCCESS, msg, **f)

    def note(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.NOTE, msg, **f)

    def warning(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.WARNING, msg, **f)

    def error(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.ERROR, msg, **f)

    def critical(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.CRITICAL, msg, **f)

    def checkpoint(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.INFO, f"📍 {msg}", **f)

    def exception(self, msg: str, **f: Any) -> Logger:
        f["logxpy:traceback"] = traceback.format_exc()
        return self._log(Level.ERROR, msg, **f)

    def __call__(self, msg: str, **f: Any) -> Logger:
        """Shortcut: log("msg") == log.info("msg")"""
        return self.info(msg, **f)

    # === Universal Send ===
    def send(self, msg: str, data: Any, **f: Any) -> Logger:
        return self._log(Level.INFO, msg, data=format_value(data), **f)

    # === Type Methods ===
    def df(self, data: Any, title: str | None = None, **opts: Any) -> Logger:
        return self.send(title or "DataFrame", data, **opts)

    def tensor(self, data: Any, title: str | None = None) -> Logger:
        return self.send(title or "Tensor", data)

    def json(self, data: dict, title: str | None = None) -> Logger:
        import json as _json

        return self._log(Level.INFO, title or "JSON", content=_json.dumps(data, indent=2, default=str)[:5000])

    def img(self, data: Any, title: str | None = None, **opts: Any) -> Logger:
        return self.send(title or "Image", data, **opts)

    def plot(self, fig: Any, title: str | None = None) -> Logger:
        return self.send(title or "Plot", fig)  # Basic support via repr/str for now

    def tree(self, data: Any, title: str | None = None) -> Logger:
        return self.send(title or "Tree", data)  # Basic support

    def table(self, data: list[dict], title: str | None = None) -> Logger:
        return self.send(title or "Table", data)  # Basic support

    # === Context (LoggerX features) ===
    def scope(self, **ctx: Any):
        """Create nested scope: `with log.scope(user_id=123):`"""
        return scope(**ctx)

    def ctx(self, **ctx: Any) -> Logger:
        """Fluent interface to add context to a new logger instance."""
        new_ctx = self._context.copy()
        new_ctx.update(ctx)
        child = Logger(self._name, new_ctx)
        child._level = self._level
        return child

    def new(self, name: str | None = None) -> Logger:
        """Create child logger with name."""
        new_name = f"{self._name}.{name}" if name else self._name
        child = Logger(new_name, self._context.copy())
        child._level = self._level
        return child

    @contextmanager
    def span(self, name: str, **attributes: Any):
        """OpenTelemetry span context manager."""
        try:
            from opentelemetry import trace as otel

            tracer = otel.get_tracer(__name__)
            with tracer.start_as_current_span(name, attributes=attributes) as span:
                yield span
        except ImportError:

            class MockSpan:
                def set_attribute(self, k, v):
                    pass

                def add_event(self, n, a=None):
                    pass

                def __enter__(self):
                    return self

                def __exit__(self, *a):
                    pass

            yield MockSpan()

    # === Decorators (exposed as methods) ===
    logged = staticmethod(decorators.logged)
    timed = staticmethod(decorators.timed)
    retry = staticmethod(decorators.retry)
    generator = staticmethod(decorators.generator)
    aiterator = staticmethod(decorators.aiterator)
    trace = staticmethod(decorators.trace)

    # === Config ===
    def configure(
        self,
        level: str = "DEBUG",
        destinations: list[str] | None = None,
        format: str = "rich",
        context: dict[str, Any] | None = None,
        mask_fields: list[str] | None = None,
        **_: Any,
    ) -> Logger:
        self._level = Level[level.upper()]

        if context:
            self._context.update(context)

        if mask_fields:
            from ._mask import Masker

            self._masker = Masker(mask_fields, [])
            set_global_masker(self._masker)

        if destinations:
            # Clear existing destinations if possible, or we just add new ones?
            # Simple implementation: Add what's requested.
            for dest in destinations:
                if dest == "console":
                    # Console destination setup
                    if format == "rich":

                    if format == "rich":
                        # We can't easily plug async destination into sync logxpy pipeline yet
                        # For now, we assume standard logxpy setup + our extensions.
                        pass

                elif dest.startswith("file://"):
                    path = dest.replace("file://", "")
                    to_file(open(path, "a"))

                elif dest.startswith("otel"):
                    # Setup OTel
                    pass

        return self

    # === Internal ===
    def _log(self, level: Level, msg: str, **fields: Any) -> Logger:
        if level.value < self._level.value:
            return self
        act = current_action()
        task_uuid, task_level = _get_task_info(act)

        # Merge context: global scope + logger instance context
        ctx = current_scope()
        if self._context:
            ctx = {**ctx, **self._context}

        record = Record(
            timestamp=now(),
            level=level,
            message=msg,
            message_type=f"loggerx:{level.name.lower()}",
            fields=fields,
            context=ctx,
            task_uuid=task_uuid,
            task_level=task_level,
        )
        _emit(record)  # Goes to destinations + any registered handlers
        return self


def _get_task_info(act) -> tuple[str, tuple[int, ...]]:
    """Extract task info from Action or AsyncAction."""
    if act is None:
        return uuid(), (1,)
    task_uuid = act.task_uuid
    # Action uses _task_level (TaskLevel), AsyncAction uses task_level (tuple)
    if hasattr(act, "task_level"):  # AsyncAction
        return task_uuid, act.task_level
    if hasattr(act, "_task_level"):  # Action
        return task_uuid, tuple(act._task_level.as_list())
    return task_uuid, (1,)


# === Global masker ===
_global_masker = None


def set_global_masker(masker):
    global _global_masker
    _global_masker = masker


def get_global_masker():
    return _global_masker


# === Global instance ===
log = Logger()
