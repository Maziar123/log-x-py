"""
Support for actions and tasks.

Actions have a beginning and an eventual end, and can be nested. Tasks are
top-level actions.

Python 3.12+ features used:
- Type aliases (PEP 695): `type Name = ...`
- Pattern matching (PEP 634): Clean value routing
- Walrus operator (PEP 572): Assignment expressions
- StrEnum (PEP 663): Type-safe string enums

Boltons features used:
- boltons.funcutils: Enhanced function wrapping
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from contextlib import contextmanager
from contextvars import ContextVar
from enum import StrEnum
from functools import partial
from inspect import getcallargs
from typing import Any, TypeVar

T = TypeVar("T")
from uuid import uuid4

from boltons.funcutils import wraps
from pyrsistent import PClass, field, optional, pmap_field, pvector

from ._types import TaskLevel  # Import to avoid circular import
from ._message import (
    MESSAGE_TYPE_FIELD,
    TASK_LEVEL_FIELD,
    TASK_UUID_FIELD,
    TIMESTAMP_FIELD,
    EXCEPTION_FIELD,
    REASON_FIELD,
    WrittenMessage,
)
from ._util import safeunicode
from ._errors import _error_extraction


# ============================================================================
# Type Aliases (PEP 695 - Python 3.12+)
# ============================================================================

type ActionDict = dict[str, Any]
type TaskLevelList = list[int]


# ============================================================================
# Constants
# ============================================================================

ACTION_STATUS_FIELD = "st"  # was: action_status
ACTION_TYPE_FIELD = "at"  # was: action_type

_ACTION_CONTEXT: ContextVar[Action] = ContextVar("logxpy.action")
_TASK_ID_NOT_SUPPLIED: object = object()


# ============================================================================
# Action Status Enum (PEP 663 - StrEnum)
# ============================================================================

class ActionStatus(StrEnum):
    """Action status values as string enum (PEP 663)."""
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


# Backwards compatibility - keep the old constant names
STARTED_STATUS = "started"
SUCCEEDED_STATUS = "succeeded"
FAILED_STATUS = "failed"
VALID_STATUSES = (STARTED_STATUS, SUCCEEDED_STATUS, FAILED_STATUS)


# ============================================================================
# Action Class
# ============================================================================

class Action:
    """
    Part of a nested hierarchy of ongoing actions.

    An action has a start and an end; a message is logged for each.

    Actions should only be used from a single thread, by implication the
    thread where they were created.

    @ivar _identification: Fields identifying this action.
    @ivar _successFields: Fields to be included in successful finish message.
    @ivar _finished: True if the Action has finished, otherwise False.
    """

    __slots__ = (
        "_success_fields",
        "_logger",
        "_task_level",
        "_last_child",
        "_identification",
        "_serializers",
        "_finished",
        "_parent_token",
    )

    def __init__(
        self,
        logger: Any | None,
        task_uuid: str,
        task_level: TaskLevel,
        action_type: str,
        serializers: Any | None = None,
    ):
        """
        Initialize the Action and log the start message.

        You probably do not want to use this API directly: use start_action
        or start_task instead.

        @param logger: The ILogger to which to write messages.
        @param task_uuid: The uuid of the top-level task, e.g. "123525".
        @param task_level: The action's level in the task.
        @param action_type: The type of the action, e.g. "yourapp:subsystem:dosomething".
        @param serializers: Either an _ActionSerializers instance or None.
        """
        self._success_fields: dict[str, Any] = {}
        self._logger = _output._DEFAULT_LOGGER if logger is None else logger
        self._task_level = task_level
        self._last_child: TaskLevel | None = None
        self._identification = {
            TASK_UUID_FIELD: task_uuid,
            ACTION_TYPE_FIELD: action_type,
        }
        self._serializers = serializers
        self._finished = False
        self._parent_token: Any | None = None

    @property
    def task_uuid(self) -> str:
        """Return the current action's task UUID."""
        return self._identification[TASK_UUID_FIELD]

    def serialize_task_id(self) -> bytes:
        """
        Create a unique identifier for the current location within the task.

        The format is b"<task_uuid>@<task_level>".

        @return: bytes encoding the current location within the task.
        """
        return f"{self._identification[TASK_UUID_FIELD]}@{self._next_task_level().to_string()}".encode("ascii")

    @classmethod
    def continue_task(
        cls,
        logger: Any | None = None,
        task_id: Any = _TASK_ID_NOT_SUPPLIED,
        *,
        action_type: str = "logxpy:remote_task",
        _serializers: Any | None = None,
        **fields: Any,
    ) -> Action:
        """
        Start a new action which is part of a serialized task.

        @param logger: The ILogger to which to write messages, or None.
        @param task_id: A serialized task identifier from serialize_task_id.
        @param action_type: The type of this action.
        @param _serializers: Either an _ActionSerializers instance or None.
        @param fields: Additional fields to add to the start message.
        @return: The new Action instance.
        """
        # Use walrus operator for cleaner validation
        if task_id is _TASK_ID_NOT_SUPPLIED:
            raise RuntimeError("You must supply a task_id keyword argument.")

        # Use pattern matching for task_id conversion
        match task_id:
            case bytes():
                task_id_str = task_id.decode("ascii")
            case str():
                task_id_str = task_id
            case _:
                raise TypeError(f"task_id must be bytes or str, got {type(task_id)}")

        # Use walrus for clean parsing
        if "@" not in task_id_str:
            raise ValueError(f"Invalid task_id format: {task_id_str}")

        uuid, task_level = task_id_str.split("@")
        action = cls(logger, uuid, TaskLevel.from_string(task_level), action_type, _serializers)
        action._start(fields)
        return action

    # Backwards-compat variants:
    serializeTaskId = serialize_task_id
    continueTask = continue_task

    def _next_task_level(self) -> TaskLevel:
        """
        Return the next task_level for messages within this action.

        Called whenever a message is logged within the context of an action.

        @return: The message's task_level.
        """
        if self._last_child is None:
            self._last_child = self._task_level.child()
        else:
            self._last_child = self._last_child.next_sibling()
        return self._last_child

    def _start(self, fields: dict[str, Any]) -> None:
        """
        Log the start message.

        The action identification fields, and any additional given fields,
        will be logged.
        """
        fields[ACTION_STATUS_FIELD] = ActionStatus.STARTED
        fields[TIMESTAMP_FIELD] = time.time()
        fields.update(self._identification)
        fields[TASK_LEVEL_FIELD] = self._next_task_level().as_list()

        # Use pattern matching for serializer selection
        match self._serializers:
            case None:
                serializer = None
            case _:
                serializer = self._serializers.start

        self._logger.write(fields, serializer)

    def finish(self, exception: Exception | None = None) -> None:
        """
        Log the finish message.

        @param exception: None for success, or an Exception for failure.
        """
        if self._finished:
            return
        self._finished = True

        # Use pattern matching for cleaner exception handling
        match (exception, self._serializers):
            case (None, serializers):
                fields = self._success_fields
                fields[ACTION_STATUS_FIELD] = ActionStatus.SUCCEEDED
                serializer = None if serializers is None else serializers.success
            case (exc, serializers):
                fields = _error_extraction.get_fields_for_exception(self._logger, exc)
                fields[EXCEPTION_FIELD] = f"{exc.__class__.__module__}.{exc.__class__.__name__}"
                fields[REASON_FIELD] = safeunicode(exc)
                fields[ACTION_STATUS_FIELD] = ActionStatus.FAILED
                serializer = None if serializers is None else serializers.failure

        fields[TIMESTAMP_FIELD] = time.time()
        fields.update(self._identification)
        fields[TASK_LEVEL_FIELD] = self._next_task_level().as_list()
        self._logger.write(fields, serializer)

    def child(self, logger: Any, action_type: str, serializers: Any | None = None) -> Action:
        """
        Create a child Action.

        @param logger: The ILogger to which to write messages.
        @param action_type: The type of this action.
        @param serializers: Either an _ActionSerializers instance or None.
        """
        new_level = self._next_task_level()
        return self.__class__(
            logger,
            self._identification[TASK_UUID_FIELD],
            new_level,
            action_type,
            serializers,
        )

    def run(self, f: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Run the given function with this Action as its execution context.
        """
        parent = _ACTION_CONTEXT.set(self)
        try:
            return f(*args, **kwargs)
        finally:
            _ACTION_CONTEXT.reset(parent)

    def add_success_fields(self, **fields: Any) -> None:
        """
        Add fields to be included in the result message when the action
        finishes successfully.

        @param fields: Additional fields to add to the result message.
        """
        self._success_fields.update(fields)

    # PEP 8 variant:
    addSuccessFields = add_success_fields

    @contextmanager
    def context(self):
        """
        Create a context manager that ensures code runs within action's context.
        The action does NOT finish when the context is exited.
        """
        parent = _ACTION_CONTEXT.set(self)
        try:
            yield self
        finally:
            _ACTION_CONTEXT.reset(parent)

    def __enter__(self) -> Action:
        """
        Push this action onto the execution context.
        """
        self._parent_token = _ACTION_CONTEXT.set(self)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """
        Pop this action off the execution context, log finish message.
        """
        _ACTION_CONTEXT.reset(self._parent_token)
        self._parent_token = None
        self.finish(exc_value)

    # Message logging
    def log(self, message_type: str, **fields: Any) -> None:
        """Log individual message."""
        fields[TIMESTAMP_FIELD] = time.time()
        fields[TASK_UUID_FIELD] = self._identification[TASK_UUID_FIELD]
        fields[TASK_LEVEL_FIELD] = self._next_task_level().as_list()
        fields[MESSAGE_TYPE_FIELD] = message_type
        logger = fields.pop("__logxpy_logger__", self._logger)
        logger.write(fields, fields.pop("__logxpy_serializer__", None))


# ============================================================================
# Exception Classes
# ============================================================================

class WrongTask(Exception):
    """Tried to add a message to an action, but the message was from another task."""

    def __init__(self, action: Action, message: Any) -> None:
        super().__init__(
            f"Tried to add {message} to {action}. Expected task_uuid = {action.task_uuid}, "
            f"got {message.task_uuid}"
        )


class WrongTaskLevel(Exception):
    """Tried to add a message to an action, but the task level indicated it was not a direct child."""

    def __init__(self, action: Action, message: Any) -> None:
        super().__init__(
            f"Tried to add {message} to {action}, but {message.task_level} is not a sibling of {action.task_level}"
        )


class WrongActionType(Exception):
    """Tried to end a message with a different action_type than the beginning."""

    def __init__(self, action: Action, message: Any) -> None:
        super().__init__(
            f"Tried to end {action} with {message}. Expected action_type = {action.action_type}, "
            f"got {message.contents.get(ACTION_TYPE_FIELD, '<undefined>')}"
        )


class InvalidStatus(Exception):
    """Tried to end a message with an invalid status."""

    def __init__(self, action: Action, message: Any) -> None:
        super().__init__(
            f"Tried to end {action} with {message}. Expected status {ActionStatus.SUCCEEDED} or "
            f"{ActionStatus.FAILED}, got {message.contents.get(ACTION_STATUS_FIELD, '<undefined>')}"
        )


class DuplicateChild(Exception):
    """Tried to add a child to an action that already had a child at that task level."""

    def __init__(self, action: Action, message: Any) -> None:
        super().__init__(
            f"Tried to add {message} to {action}, but already had child at {message.task_level}"
        )


class InvalidStartMessage(Exception):
    """Tried to start an action with an invalid message."""

    def __init__(self, message: Any, reason: str) -> None:
        super().__init__(f"Invalid start message {message}: {reason}")

    @classmethod
    def wrong_status(cls, message: Any) -> InvalidStartMessage:
        return cls(message, 'must have status "STARTED"')

    @classmethod
    def wrong_task_level(cls, message: Any) -> InvalidStartMessage:
        return cls(message, "first message must have task level ending in 1")


# ============================================================================
# WrittenAction Class
# ============================================================================

class WrittenAction(PClass):
    """
    An Action that has been logged.

    @ivar WrittenMessage start_message: A start message whose task UUID and
        level match this action, or None if it is not yet set.
    @ivar WrittenMessage end_message: An end message whose task UUID and
        level match this action. Can be None if the action is unfinished.
    @ivar TaskLevel task_level: The action's task level.
    @ivar str task_uuid: The UUID of the task to which this action belongs.
    @ivar _children: A pmap from TaskLevel to WrittenAction and WrittenMessage objects.
    """

    start_message = field(type=optional(WrittenMessage), mandatory=True, initial=None)
    end_message = field(type=optional(WrittenMessage), mandatory=True, initial=None)
    task_level = field(type=TaskLevel, mandatory=True)
    task_uuid = field(type=str, mandatory=True, factory=str)
    _children = pmap_field(TaskLevel, object)

    @classmethod
    def from_messages(
        cls,
        start_message: WrittenMessage | None = None,
        children: pvector = pvector(),
        end_message: WrittenMessage | None = None,
    ) -> WrittenAction:
        """
        Create a WrittenAction from WrittenMessages and other WrittenActions.

        @param start_message: A start message with proper status and level.
        @param children: An iterable of WrittenMessage and WrittenAction.
        @param end_message: An end message with same action_type as start.
        @return: A new WrittenAction.
        """
        # Use walrus to get the first non-None message
        messages = [m for m in [start_message, end_message] + list(children) if m]
        if not messages:
            raise ValueError("At least one message is required")

        actual_message = messages[0]
        action = cls(
            task_level=actual_message.task_level.parent(),
            task_uuid=actual_message.task_uuid,
        )

        if start_message:
            action = action._start(start_message)
        for child in children:
            if action._children.get(child.task_level, child) != child:
                raise DuplicateChild(action, child)
            action = action._add_child(child)
        if end_message:
            action = action._end(end_message)
        return action

    @property
    def action_type(self) -> str | None:
        """The type of this action."""
        # Use pattern matching for cleaner property access
        match (self.start_message, self.end_message):
            case (WrittenMessage(), _):
                return self.start_message.contents[ACTION_TYPE_FIELD]
            case (_, WrittenMessage()):
                return self.end_message.contents[ACTION_TYPE_FIELD]
            case _:
                return None

    @property
    def status(self) -> str | None:
        """One of STARTED_STATUS, SUCCEEDED_STATUS, FAILED_STATUS or None."""
        message = self.end_message if self.end_message else self.start_message
        return message.contents[ACTION_STATUS_FIELD] if message else None

    @property
    def start_time(self) -> float | None:
        """The Unix timestamp of when the action started."""
        return self.start_message.timestamp if self.start_message else None

    @property
    def end_time(self) -> float | None:
        """The Unix timestamp of when the action ended."""
        return self.end_message.timestamp if self.end_message else None

    @property
    def exception(self) -> str | None:
        """The exception name if the action failed, otherwise None."""
        if self.end_message:
            return self.end_message.contents.get(EXCEPTION_FIELD, None)

    @property
    def reason(self) -> str | None:
        """The reason the action failed if applicable."""
        if self.end_message:
            return self.end_message.contents.get(REASON_FIELD, None)

    @property
    def children(self) -> pvector:
        """Child messages and actions sorted by task level."""
        return pvector(sorted(self._children.values(), key=lambda m: m.task_level))

    def _validate_message(self, message: WrittenMessage | WrittenAction) -> None:
        """
        Is message a valid direct child of this action?

        @param message: Either a WrittenAction or a WrittenMessage.
        @raise WrongTask: If message has a different task_uuid.
        @raise WrongTaskLevel: If message is not a direct child.
        """
        if message.task_uuid != self.task_uuid:
            raise WrongTask(self, message)
        if message.task_level.parent() != self.task_level:
            raise WrongTaskLevel(self, message)

    def _add_child(self, message: WrittenMessage | WrittenAction) -> WrittenAction:
        """
        Return a new action with message added as a child.

        @param message: Either a WrittenAction or a WrittenMessage.
        @return: A new WrittenAction.
        """
        self._validate_message(message)
        level = message.task_level
        return self.transform(("_children", level), message)

    def _start(self, start_message: WrittenMessage) -> WrittenAction:
        """
        Start this action given its start message.

        @param start_message: A start message with the same level as this action.
        """
        if start_message.contents.get(ACTION_STATUS_FIELD, None) != ActionStatus.STARTED:
            raise InvalidStartMessage.wrong_status(start_message)
        if start_message.task_level.level[-1] != 1:
            raise InvalidStartMessage.wrong_task_level(start_message)
        return self.set(start_message=start_message)

    def _end(self, end_message: WrittenMessage) -> WrittenAction:
        """
        End this action with end_message.

        @param end_message: An end message with the same level as this action.
        @return: A new, completed WrittenAction.
        """
        action_type = end_message.contents.get(ACTION_TYPE_FIELD, None)
        if self.action_type not in (None, action_type):
            raise WrongActionType(self, end_message)
        self._validate_message(end_message)
        status = end_message.contents.get(ACTION_STATUS_FIELD, None)
        if status not in (ActionStatus.FAILED, ActionStatus.SUCCEEDED):
            raise InvalidStatus(self, end_message)
        return self.set(end_message=end_message)


# ============================================================================
# Public API Functions
# ============================================================================

def current_action() -> Action | None:
    """
    @return: The current Action in context, or None if none were set.
    """
    return _ACTION_CONTEXT.get(None)


def start_action(
    logger: Any | None = None,
    action_type: str = "",
    _serializers: Any | None = None,
    **fields: Any,
) -> Action:
    """
    Create a child Action, figuring out the parent Action from execution
    context, and log the start message.

    You can use the result as a Python context manager:

        with start_action(logger, "yourapp:subsystem:dosomething", entry=x) as action:
            do(x)
            result = something(x * 2)
            action.add_success_fields(result=result)

    @param logger: The ILogger to which to write messages, or None.
    @param action_type: The type of this action.
    @param _serializers: Either an _ActionSerializers instance or None.
    @param fields: Additional fields to add to the start message.
    @return: A new Action.
    """
    parent = current_action()
    if parent is None:
        return start_task(logger, action_type, _serializers, **fields)
    else:
        action = parent.child(logger, action_type, _serializers)
        action._start(fields)
        return action


def start_task(
    logger: Any | None = None,
    action_type: str = "",
    _serializers: Any | None = None,
    **fields: Any,
) -> Action:
    """
    Like start_action, but creates a new top-level Action with no parent.

    @param logger: The ILogger to which to write messages, or None.
    @param action_type: The type of this action.
    @param _serializers: Either an _ActionSerializers instance or None.
    @param fields: Additional fields to add to the start message.
    @return: A new Action.
    """
    action = Action(
        logger, str(uuid4()), TaskLevel(level=[]), action_type, _serializers
    )
    action._start(fields)
    return action


# Backwards compatibility
startTask = start_task


class TooManyCalls(Exception):
    """
    The callable was called more than once.
    This typically indicates a coding bug: the result of preserve_context
    should only be called once.
    """


def preserve_context(f: Callable[..., T]) -> Callable[..., T]:
    """
    Package up the given function with the current context, and then
    restore context and call given function when the resulting callable is
    run. This allows continuing the action context within a different thread.

    @param f: A callable.
    @return: One-time use callable that calls given function in context of
        a child of current action.
    """
    action = current_action()
    if action is None:
        return f
    task_id = action.serialize_task_id()
    called = threading.Lock()

    @wraps(f)
    def restore_logxpy_context(*args: Any, **kwargs: Any) -> T:
        # Make sure the function has not already been called:
        if not called.acquire(False):
            raise TooManyCalls(f)

        with Action.continue_task(task_id=task_id):
            return f(*args, **kwargs)

    return restore_logxpy_context


def log_call(
    wrapped_function: Callable[..., T] | None = None,
    *,
    action_type: str | None = None,
    include_args: list[str] | None = None,
    include_result: bool = True,
) -> Callable[..., T]:
    """
    Decorator/decorator factory that logs inputs and the return result.

    @param action_type: The action type to use. If not given the function name will be used.
    @param include_args: If given, should be a list of strings, the arguments to log.
    @param include_result: True by default. If False, the return result isn't logged.
    """
    if wrapped_function is None:
        return partial(
            log_call,
            action_type=action_type,
            include_args=include_args,
            include_result=include_result,
        )

    if action_type is None:
        action_type = f"{wrapped_function.__module__}.{wrapped_function.__qualname__}"

    if include_args is not None:
        from inspect import signature

        sig = signature(wrapped_function)
        if set(include_args) - set(sig.parameters):
            raise ValueError(
                f"include_args ({include_args}) lists arguments not in the wrapped function"
            )

    @wraps(wrapped_function)
    def logging_wrapper(*args: Any, **kwargs: Any) -> T:
        callargs = getcallargs(wrapped_function, *args, **kwargs)

        # Remove self if it's included:
        callargs.pop("self", None)

        # Filter arguments to log, if necessary:
        if include_args is not None:
            callargs = {k: callargs[k] for k in include_args}

        with start_action(action_type=action_type, **callargs) as ctx:
            result = wrapped_function(*args, **kwargs)
            if include_result:
                ctx.add_success_fields(result=result)
            return result

    return logging_wrapper


# Import at end to deal with circular imports:
from . import _output
# Import log_message from _message to avoid circular import
from ._message import log_message
