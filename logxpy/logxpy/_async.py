"""Async action and scope - integrates with logxpy's context system."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar, Token
from typing import Any

# Use shared context var for action tracking
from ._action import _ACTION_CONTEXT, current_action
from ._base import now, uuid
from ._types import Level, Record

# Additional scope context (LoggerX feature - logxpy doesn't have this)
_SCOPE: ContextVar[dict[str, Any]] = ContextVar("loggerx_scope", default={})


def current_scope() -> dict[str, Any]:
    return _SCOPE.get()


def _get_parent_info() -> tuple[str, tuple[int, ...]]:
    """Get task_uuid and next level from current action."""
    parent = current_action()
    if parent:
        # Action has task_uuid property and _task_level (TaskLevel object)
        task_uuid = parent.task_uuid
        # Get current level and create child level
        if hasattr(parent, "_task_level"):
            level = tuple(parent._task_level.as_list()) + (1,)
        else:
            level = (1,)
        return task_uuid, level
    return uuid(), (1,)


# === AsyncAction (works alongside Action for async contexts) ===
class AsyncAction:
    """Async-native action that integrates with logxpy's context system."""

    __slots__ = (
        "_child_count",
        "_start",
        "_token",
        "action_type",
        "fields",
        "level",
        "task_level",
        "task_uuid",
    )

    def __init__(
        self,
        action_type: str,
        task_uuid: str,
        task_level: tuple[int, ...],
        level: Level = Level.INFO,
        **fields: Any,
    ):
        self.task_uuid = task_uuid
        self.task_level = task_level
        self.action_type = action_type
        self.fields = fields
        self.level = level
        self._start = now()
        self._token: Token[Any] | None = None
        self._child_count = 0

    def child_level(self) -> tuple[int, ...]:
        self._child_count += 1
        return (*self.task_level, self._child_count)

    def _enter(self) -> AsyncAction:
        self._token = _ACTION_CONTEXT.set(self)
        _emit(self._start_record())
        return self

    def _exit(self, exc: BaseException | None) -> None:
        if self._token:
            _ACTION_CONTEXT.reset(self._token)
        _emit(self._end_record(exc))

    def _start_record(self) -> Record:
        return Record(
            timestamp=self._start,
            level=self.level,
            message="",
            fields=self.fields,
            context=current_scope(),
            task_uuid=self.task_uuid,
            task_level=self.task_level,
            action_type=self.action_type,
            action_status="started",
        )

    def _end_record(self, exc: BaseException | None) -> Record:
        status = "failed" if exc else "succeeded"
        fields = {**self.fields, "logxpy:duration": round(now() - self._start, 6)}
        if exc:
            fields["exception"] = f"{type(exc).__module__}.{type(exc).__name__}"
            fields["reason"] = str(exc)
        return Record(
            timestamp=now(),
            level=self.level,
            message="",
            fields=fields,
            context=current_scope(),
            task_uuid=self.task_uuid,
            task_level=(*self.task_level, self._child_count + 1),
            action_type=self.action_type,
            action_status=status,
        )

    # Dual context manager support (sync + async)
    def __enter__(self) -> AsyncAction:
        return self._enter()

    def __exit__(self, *exc) -> None:
        self._exit(exc[1])

    async def __aenter__(self) -> AsyncAction:
        return self._enter()

    async def __aexit__(self, *exc) -> None:
        self._exit(exc[1])


@contextmanager
def action(action_type: str, level: str | Level = Level.INFO, **fields: Any) -> Iterator[AsyncAction]:
    """Create action context (sync) - compatible with logxpy's nesting."""
    if isinstance(level, str):
        level = Level[level.upper()]
    task_uuid, t_level = _get_parent_info()
    act = AsyncAction(action_type, task_uuid, t_level, level=level, **fields)
    with act:
        yield act


@asynccontextmanager
async def aaction(action_type: str, level: str | Level = Level.INFO, **fields: Any) -> AsyncIterator[AsyncAction]:
    """Create action context (async)."""
    if isinstance(level, str):
        level = Level[level.upper()]
    task_uuid, t_level = _get_parent_info()
    act = AsyncAction(action_type, task_uuid, t_level, level=level, **fields)
    async with act:
        yield act


# === Scope (LoggerX feature) ===
@contextmanager
def scope(**ctx: Any) -> Iterator[dict[str, Any]]:
    """Create nested scope context for field inheritance."""
    current = _SCOPE.get()
    merged = {**current, **ctx}
    token = _SCOPE.set(merged)
    try:
        yield merged
    finally:
        _SCOPE.reset(token)


# === Emit (connects to destination system) ===
_emit_handlers: list[Callable[[Record], None]] = []


def _emit(record: Record) -> None:
    """Emit to destinations + any registered handlers."""
    from ._output import Logger
    from .loggerx import get_global_masker

    data = record.to_dict()

    # Apply masking if configured
    masker = get_global_masker()
    if masker:
        data = masker.mask(data)

    Logger._destinations.send(data)  # Uses internal destination system
    for fn in _emit_handlers:
        fn(record)


def register_emitter(fn: Callable[[Record], None]) -> None:
    _emit_handlers.append(fn)
