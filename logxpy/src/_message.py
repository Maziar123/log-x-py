"""
Log messages and related utilities.

Python 3.12+ features used:
- Type aliases (PEP 695): `type Name = ...`
- Pattern matching (PEP 634): Clean value routing
- Walrus operator (PEP 572): Assignment expressions

Boltons features used:
- boltons.dictutils: Advanced dictionary operations (subdict, OMD)
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any
from uuid import uuid4
from warnings import warn

from boltons.dictutils import OMD, subdict
from pyrsistent import PClass, PMap, pmap, pmap_field

# ============================================================================
# Type Aliases (PEP 695 - Python 3.12+)
# ============================================================================

type MessageDict = dict[str, object]
type FieldDict = dict[str, object]


# ============================================================================
# Field Name Constants (Compact)
# ============================================================================

MESSAGE_TYPE_FIELD = "mt"      # was: message_type
TASK_UUID_FIELD = "tid"        # was: task_uuid  
TASK_LEVEL_FIELD = "lvl"       # was: task_level
TIMESTAMP_FIELD = "ts"         # was: timestamp

EXCEPTION_FIELD = "exc"        # was: exception
REASON_FIELD = "reason"        # kept: reason (already short)


# ============================================================================
# Message Class
# ============================================================================

class Message:
    """
    A log message.

    Messages are basically dictionaries, mapping "fields" to "values". Field
    names should not start with '_', as those are reserved for system use
    (e.g. "_id" is used by Elasticsearch for unique message identifiers and
    may be auto-populated by logstash).

    This implementation uses boltons.dictutils.OMD (OrderedMultiDict) for
    efficient field operations and maintains insertion order.
    """

    # Overrideable for testing purposes:
    _time: Callable[[], float] = time.time

    @classmethod
    def new(_cls, _serializer: object | None = None, **fields: object) -> Message:
        """
        Create a new Message.

        The keyword arguments will become the initial contents of the Message.

        @param _serializer: A positional argument, either None or a
            _MessageSerializer with which a ILogger may choose to serialize
            the message. If you're using MessageType this will be populated.

        @return: The new Message
        """
        warn(
            "Message.new() is deprecated since 1.11.0, "
            "use log_message() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return _cls(fields, _serializer)

    @classmethod
    def log(_cls, **fields: object) -> None:
        """
        Write a new Message to the default Logger.

        The keyword arguments will become contents of the Message.
        """
        warn(
            "Message.log() is deprecated since 1.11.0, "
            "use Action.log() or log_message() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        _cls(fields).write()

    def __init__(self, contents: MessageDict, serializer: object | None = None):
        """
        Initialize a Message.

        @param contents: The contents of this Message, a dict whose keys
           must be str, or text that has been UTF-8 encoded to bytes.

        @param serializer: Either None, or _MessageSerializer with which a
            Logger may choose to serialize the message. If you're using
            MessageType this will be populated for you.
        """
        # Use OMD (OrderedMultiDict) from boltons for efficient operations
        self._contents: OMD = OMD(contents)
        self._serializer: object | None = serializer

    def bind(self, **fields: object) -> Message:
        """
        Return a new Message with this message's contents plus the
        additional given bindings.

        Uses OMD.update() for efficient merging while preserving order.
        """
        # Create new OMD with merged contents
        new_contents: OMD = OMD(self._contents)
        new_contents.update(fields)
        return Message(dict(new_contents), self._serializer)

    def contents(self) -> MessageDict:
        """
        Return a copy of Message contents.

        Uses OMD for efficient copy operation.
        """
        return dict(self._contents)

    def _timestamp(self) -> float:
        """
        Return the current time.
        """
        return self._time()

    def write(self, logger: object | None = None, action: object | None = None) -> None:
        """
        Write the message to the given logger.

        This will additionally include a timestamp, the action context if any,
        and any other fields.

        Byte field names will be converted to Unicode.

        @param logger: ILogger or None indicating the default one.
            Should not be set if the action is also set.

        @param action: The Action which is the context for this message. If
            None, the Action will be deduced from the current call stack.
        """
        # Use pattern matching for cleaner logic
        match (self._serializer, action, logger):
            case (serializer, None, None):
                fields = dict(self._contents)
                if "message_type" not in fields:
                    fields["message_type"] = ""
                if serializer is not None:
                    fields["__logxpy_serializer__"] = serializer
                log_message(**fields)

            case (serializer, None, _logger):
                fields = dict(self._contents)
                if "message_type" not in fields:
                    fields["message_type"] = ""
                if serializer is not None:
                    fields["__logxpy_serializer__"] = serializer
                fields["__logxpy_logger__"] = _logger
                log_message(**fields)

            case (_, _action, _):
                _action.log(**dict(self._contents))


# ============================================================================
# WrittenMessage Class
# ============================================================================

class WrittenMessage(PClass):
    """
    A Message that has been logged.

    Uses pyrsistent PClass for immutable, persistent data structures.

    @ivar _logged_dict: The originally logged dictionary.
    """

    _logged_dict = pmap_field((str, str), object)

    @property
    def timestamp(self) -> float:
        """
        The Unix timestamp of when the message was logged.
        """
        return self._logged_dict[TIMESTAMP_FIELD]

    @property
    def task_uuid(self) -> str:
        """
        The UUID of the task in which the message was logged.
        """
        return self._logged_dict[TASK_UUID_FIELD]

    @property
    def task_level(self) -> TaskLevel:
        """
        The TaskLevel of this message appears within the task.
        """
        return TaskLevel(level=self._logged_dict[TASK_LEVEL_FIELD])

    @property
    def contents(self) -> PMap:
        """
        A PMap, the message contents without logxpy metadata.

        Uses method chaining for cleaner code.
        """
        return (
            self._logged_dict.discard(TIMESTAMP_FIELD)
            .discard(TASK_UUID_FIELD)
            .discard(TASK_LEVEL_FIELD)
        )

    @classmethod
    def from_dict(cls, logged_dictionary: dict | PMap) -> WrittenMessage:
        """
        Reconstruct a WrittenMessage from a logged dictionary.

        @param logged_dictionary: A dict or PMap representing a parsed log entry.
        @return: A WrittenMessage for that dictionary.
        """
        if not isinstance(logged_dictionary, PMap):
            logged_dictionary = pmap(logged_dictionary)
        return cls(_logged_dict=logged_dictionary)

    def as_dict(self) -> PMap:
        """
        Return the dictionary that was used to write this message.

        @return: A dict, as might be logged by logxpy.
        """
        return self._logged_dict

    def get_subset(self, *keys: str) -> dict[str, object]:
        """
        Get a subset of fields using boltons.subdict.

        @param keys: Field names to extract.
        @return: Dict containing only the requested fields.
        """
        return subdict(self._logged_dict, keys)

    def with_fields(self, **fields: object) -> WrittenMessage:
        """
        Return a new WrittenMessage with additional fields.

        Uses boltons.OMD for efficient merging.

        @param fields: Additional fields to add.
        @return: New WrittenMessage with merged fields.
        """
        merged = OMD(self._logged_dict)
        merged.update(fields)
        return WrittenMessage.from_dict(dict(merged))


# ============================================================================
# Helper Functions using boltons
# ============================================================================

def merge_messages(*messages: Message) -> Message:
    """
    Merge multiple messages into one.

    Later messages override earlier ones for conflicting keys.
    Uses boltons.OMD for efficient merging.

    @param messages: Message objects to merge.
    @return: New Message with merged contents.
    """
    merged = OMD()
    for msg in messages:
        merged.update(msg._contents)
    return Message(dict(merged))


def extract_fields(message: Message | WrittenMessage, *keys: str) -> dict[str, object]:
    """
    Extract specific fields from a message using boltons.subdict.

    @param message: Message or WrittenMessage to extract from.
    @param keys: Field names to extract.
    @return: Dict containing extracted fields.
    """
    source = message._logged_dict if isinstance(message, WrittenMessage) else message._contents
    return subdict(source, keep=keys)


# ============================================================================
# Imports (avoid circular dependency)
# ============================================================================

from ._types import TaskLevel


# ============================================================================
# Message Logging Helper
# ============================================================================

def log_message(message_type: str, **fields: Any) -> None:
    """
    Log a message in the context of the current action.
    If there is no current action, a new UUID will be generated.
    """
    # Late import to avoid circular dependency
    from ._action import current_action, Action

    action = current_action()
    if action is None:
        logger = fields.pop("__logxpy_logger__", None)
        action = Action(logger, str(uuid4()), TaskLevel(level=[]), "")
    action.log(message_type, **fields)
