# log-x-py - Complete User API

Full API for using logxpy (logging) + logxpy-cli-view (viewer). 100% of public features.

---

## Quick Start

### Basic Logging

```python
# app.py
from logxpy import start_action, Message, to_file

to_file("app.log")

with start_action("main"):
    Message.log(info="starting")
    with start_action("step1", user="alice"):
        Message.log(result="done")
```

```bash
python app.py
logxpy-view app.log
```

### Hierarchical Actions (Task Levels)

```python
from logxpy import start_action, current_action

# Task levels: /1, /2/1, /3/2/1 (nested hierarchy)
with start_action("process_request", request_id="123"):
    action = current_action()
    print(action.task_level)      # "/1"
    print(action.task_uuid)       # unique ID

    with start_action("db_query", table="users"):
        print(action.task_level)  # "/1/1"
        Message.log(rows_found=5)
```

### Decorators

```python
from logxpy import log_call, log_message, aaction

@log_call(action_type="function_call")
def my_function(x, y):
    return x + y

@log_message(message_type="custom_event")
def handler():
    pass

@aaction("async_task", timeout=30)
async def process():
    await asyncio.sleep(1)
```

### Validation Schemas

```python
from logxpy import MessageType, ActionType, Field, fields

class UserLogin(MessageType):
    username = Field(fields.text)
    success = Field(fields.success)
    ip_address = Field(fields.text)

class DatabaseAction(ActionType):
    table = Field(fields.text)
    query = Field(fields.text)

UserLogin().bind(username="alice", success=True)
```

### Exception Logging

```python
from logxpy import write_traceback, write_failure

try:
    risky_operation()
except Exception:
    write_traceback()  # Full traceback in logs
```

### Filtering & Export

```python
from logxpy_cli_view import (
    tasks_from_iterable,
    filter_by_action_type,
    filter_by_duration,
    export_json,
    render_tasks
)

# Parse log file
with open("app.log") as f:
    tasks = list(tasks_from_iterable(f))

# Filter
db_tasks = filter_by_action_type(tasks, "db_*")
slow_tasks = filter_by_duration(tasks, min_seconds=5.0)

# Export
export_json(slow_tasks, "output.json")

# Render as tree
print(render_tasks(tasks))
```

### Live Tail

```python
from logxpy_cli_view import tail_logs, watch_and_aggregate

# Simple tail (prints to stdout)
tail_logs("app.log")

# Or watch and process
for tasks in watch_and_aggregate("app.log"):
    for task in tasks:
        print(f"Task: {task.get('action_type')}")
```

### CLI Commands

```bash
# View as tree
logxpy-view app.log

# Only failed actions
logxpy-view app.log --failed

# Filter by action name
logxpy-view app.log --filter "db_*"

# Export formats
logxpy-view app.log --export json > out.json
logxpy-view app.log --export csv > out.csv
logxpy-view app.log --export html > out.html

# Live monitoring
logxpy-view app.log --tail

# Statistics
logxpy-view app.log --stats

# Theme options
logxpy-view app.log --theme light
logxpy-view app.log --no-color
```

---

## Part 1: Logging Library (`logxpy`)

### Messaging - Complete API

| Category | Function | Prototype | Parameters | Returns | Explain | Examples |
|----------|----------|-----------|------------|---------|---------|----------|
| **Core** | `Message.log` | `log(**fields)` | Any key-value pairs | None | Log structured message (deprecated) | `Message.log(info="starting", count=5)` |
| **Core** | `Message.new` | `new(**fields)` | Any key-value pairs | `Message` | Create new message (deprecated) | `msg = Message.new(x=1)` |
| **Core** | `Message.bind` | `bind(**fields)` | **fields | `Message` | Add fields to message | `msg.bind(user="alice")` |
| **Core** | `Message.contents` | `contents()` | None | `dict` | Get message contents | `msg.contents()` |
| **Core** | `Message.write` | `write(logger, action)` | `logger`, `action` | None | Write to logger | `msg.write(logger)` |
| **Core** | `log` | `log(**fields)` | `message_type`: str, **fields | None | Log message in current action | `log(message_type="event", x=1)` |
| **Core** | `log_message` | `log_message(message_type, **fields)` | `message_type`: str, **fields | None | Log message in action context | `log_message("my_type", x=1)` |
| **Action** | `start_action` | `start_action(action_type='', **fields)` | `action_type`: str, **fields | Context manager | Begin hierarchical action | `with start_action("db_query", table="users"):` |
| **Action** | `start_task` | `start_task(action_type='', **fields)` | `action_type`: str, **fields | Context manager | Create top-level action | `with start_task("process"):` |
| **Action** | `action` | `action(action_type, level=Level.INFO, **fields)` | `action_type`: str, `level`: Level/str, **fields | Context manager | Sync action (LoggerX style) | `with action("task"):` |
| **Action** | `aaction` | `aaction(action_type, level=Level.INFO, **fields)` | `action_type`: str, `level`: Level/str, **fields | AsyncIterator | Async action context | `async with aaction("task"):` |
| **Action** | `current_action` | `current_action()` | None | `Action` or `None` | Get current action context | `action = current_action()` |
| **Action** | `preserve_context` | `preserve_context(fn)` | `fn`: callable | callable | Capture context for threads | `ctx = preserve_context(func)` |
| **Action** | `Action.continue_task` | `continue_task(task_id, **fields)` | `task_id`: str, **fields | `Action` | Continue task in new thread | `Action.continue_task(task_id="uuid@/1")` |
| **Action** | `Action.serialize_task_id` | `serialize_task_id()` | None | `bytes` | Serialize task location | `action.serialize_task_id()` |
| **Action** | `Action.finish` | `finish(exception=None)` | `exception`: Exception | None | Finish action with status | `action.finish()` |
| **Action** | `Action.child` | `child(logger, action_type)` | `logger`, `action_type` | `Action` | Create child action | `action.child(logger, "subtask")` |
| **Action** | `Action.run` | `run(f, *args, **kwargs)` | `f`: callable | Any | Run function in action context | `action.run(func, 1, 2)` |
| **Action** | `Action.add_success_fields` | `add_success_fields(**fields)` | **fields | None | Add fields on success | `action.add_success_fields(result=5)` |
| **Action** | `Action.context` | `context()` | None | Context manager | Run in action context (no finish) | `with action.context():` |
| **Action** | `Action.log` | `log(message_type, **fields)` | `message_type`, **fields | None | Log message within action | `action.log("event", x=1)` |
| **Task** | `TaskLevel` | Class | - | - | Task level hierarchy | `TaskLevel([1, 2])` |
| **Task** | `TaskLevel.as_list` | `as_list()` | None | `list` | Get level as list | `level.as_list()` |
| **Task** | `TaskLevel.from_string` | `from_string(s)` | `s`: "/1/2" | `TaskLevel` | Parse from string | `TaskLevel.from_string("/1/2")` |
| **Task** | `TaskLevel.to_string` | `to_string()` | None | `str` | Convert to string | `level.to_string()` |
| **Task** | `TaskLevel.next_sibling` | `next_sibling()` | None | `TaskLevel` | Get next sibling | `level.next_sibling()` |
| **Task** | `TaskLevel.child` | `child()` | None | `TaskLevel` | Get child level | `level.child()` |
| **Task** | `TaskLevel.parent` | `parent()` | None | `TaskLevel` or None | Get parent level | `level.parent()` |
| **Task** | `TaskLevel.is_sibling_of` | `is_sibling_of(other)` | `other`: TaskLevel | `bool` | Check if sibling | `level.is_sibling_of(other)` |
| **Scope** | `scope` | `scope(**ctx)` | **ctx | Context manager | Nested scope for fields | `with scope(user="alice"):` |
| **Scope** | `current_scope` | `current_scope()` | None | `dict` | Get current scope context | `ctx = current_scope()` |
| **Emitter** | `register_emitter` | `register_emitter(fn)` | `fn`: callable | None | Register custom emitter | `register_emitter(handler)` |
| **Decorator** | `@log_call` | `log_call(*args, **kwargs)` | `action_type`, `include_args`, `include_result` | Decorator | Log function calls | `@log_call(action_type="func")` |
| **Output** | `to_file` | `to_file(output_file)` | `output_file`: file | None | Set log file (JSON lines) | `to_file(open("app.log", "a"))` |
| **Output** | `add_destinations` | `add_destinations(*dests)` | `*dests`: callables | None | Add multiple outputs | `add_destinations(d1, d2)` |
| **Output** | `remove_destination` | `remove_destination(dest)` | `dest`: callable | None | Remove output | `remove_destination(dest)` |
| **Output** | `add_global_fields` | `add_global_fields(**fields)` | **fields | None | Add fields to all messages | `add_global_fields(app="myapp")` |
| **Output** | `FileDestination` | `FileDestination(file)` | `file`: file object | Destination | File output | `FileDestination(f)` |
| **Output** | `BufferingDestination` | `BufferingDestination()` | None | Destination | In-memory buffer (1000 msg) | `BufferingDestination()` |
| **Output** | `Destinations` | `Destinations()` | None | - | Manage destinations | `Destinations().add(dest)` |
| **Logger** | `Logger` | Class | - | - | Main logger class | `Logger._destinations.add(dest)` |
| **Logger** | `ILogger` | Interface | - | - | Logger interface | `class MyDest(ILogger):` |
| **Logger** | `MemoryLogger` | `MemoryLogger()` | None | Logger | In-memory for testing | `logger = MemoryLogger()` |
| **Logger** | `MemoryLogger.validate` | `validate()` | None | None | Validate all messages | `logger.validate()` |
| **Logger** | `MemoryLogger.serialize` | `serialize()` | None | `list` | Serialize messages | `logger.serialize()` |
| **Logger** | `MemoryLogger.reset` | `reset()` | None | None | Clear messages | `logger.reset()` |
| **Logger** | `MemoryLogger.flush_tracebacks` | `flush_tracebacks(exc_type)` | `exc_type`: type | `list` | Flush tracebacks | `logger.flush_tracebacks(ValueError)` |
| **Exception** | `write_traceback` | `write_traceback(logger, exc_info)` | `logger`, `exc_info` | None | Log exception traceback | `except: write_traceback()` |
| **Exception** | `write_failure` | `write_failure(failure, logger)` | `failure`: Failure, `logger` | None | Log Twisted Failure | `write_failure(failure)` |
| **Message** | `WrittenMessage` | Class | - | - | A logged message | `WrittenMessage.from_dict(d)` |
| **Message** | `WrittenMessage.timestamp` | Property | - | `float` | Message timestamp | `msg.timestamp` |
| **Message** | `WrittenMessage.task_uuid` | Property | - | `str` | Task UUID | `msg.task_uuid` |
| **Message** | `WrittenMessage.task_level` | Property | - | `TaskLevel` | Task level | `msg.task_level` |
| **Message** | `WrittenMessage.contents` | Property | - | `dict` | Message contents | `msg.contents` |
| **Action** | `WrittenAction` | Class | - | - | A logged action | `WrittenAction.from_messages()` |
| **Action** | `WrittenAction.start_message` | Property | - | `WrittenMessage` | Start message | `action.start_message` |
| **Action** | `WrittenAction.end_message` | Property | - | `WrittenMessage` | End message | `action.end_message` |
| **Action** | `WrittenAction.action_type` | Property | - | `str` | Action type | `action.action_type` |
| **Action** | `WrittenAction.status` | Property | - | `str` | Action status | `action.status` |
| **Action** | `WrittenAction.start_time` | Property | - | `float` | Start time | `action.start_time` |
| **Action** | `WrittenAction.end_time` | Property | - | `float` | End time | `action.end_time` |
| **Action** | `WrittenAction.exception` | Property | - | `str` or None | Exception type | `action.exception` |
| **Action** | `WrittenAction.reason` | Property | - | `str` or None | Failure reason | `action.reason` |
| **Action** | `WrittenAction.children` | Property | - | `list` | Child messages | `action.children` |
| **Action** | `AsyncAction` | Class | - | - | Async-native action | `AsyncAction("task", uuid, level)` |
| **Action** | `AsyncAction.fields` | Attribute | - | `dict` | Mutable fields | `act.fields["x"] = 1` |
| **Action** | `AsyncAction.child_level` | `child_level()` | None | `tuple` | Get next child level | `act.child_level()` |
| **Validation** | `MessageType` | Class base | Fields as class attrs | - | Define message schema | `class Msg(MessageType):` |
| **Validation** | `ActionType` | Class base | Fields as class attrs | - | Define action schema | `class Act(ActionType):` |
| **Validation** | `Field` | `Field(key, serializer)` | `key`, `serializer` | - | Define field | `Field("x", int)` |
| **Validation** | `Field.for_value` | `for_value(value)` | `value` | `Field` | Single value field | `Field.for_value(5)` |
| **Validation** | `Field.for_types` | `for_types(types)` | `types`: list | `Field` | Multi-type field | `Field.for_types([int, str])` |
| **Validation** | `Field.validate` | `validate(value)` | `value` | None | Validate value | `field.validate(5)` |
| **Validation** | `Field.serialize` | `serialize(value)` | `value` | Any | Serialize value | `field.serialize(5)` |
| **Validation** | `fields.integer` | Constant | - | - | Integer validator | `Field(fields.integer)` |
| **Validation** | `fields.text` | Constant | - | - | Text validator | `Field(fields.text)` |
| **Validation** | `fields.success` | Constant | - | - | Boolean success | `Field(fields.success)` |
| **Validation** | `ValidationError` | Exception | - | - | Validation failed | `except ValidationError:` |
| **Constants** | `TRACEBACK_MESSAGE` | MessageType | - | - | Traceback message type | `TRACEBACK_MESSAGE.log()` |
| **Constants** | `DESTINATION_FAILURE` | str | - | - | "eliot:destination_failure" | - |
| **Constants** | `SERIALIZATION_FAILURE` | str | - | - | "eliot:serialization_failure" | - |
| **Constants** | `REMOTE_TASK` | str | - | - | "eliot:remote_task" | - |
| **Constants** | `STARTED_STATUS` | str | - | - | "started" | - |
| **Constants** | `SUCCEEDED_STATUS` | str | - | - | "succeeded" | - |
| **Constants** | `FAILED_STATUS` | str | - | - | "failed" | - |
| **Constants** | `VALID_STATUSES` | tuple | - | - | All valid statuses | - |
| **Constants** | `MESSAGE_TYPE_FIELD` | str | - | - | "message_type" | - |
| **Constants** | `ACTION_TYPE_FIELD` | str | - | - | "action_type" | - |
| **Constants** | `ACTION_STATUS_FIELD` | str | - | - | "action_status" | - |
| **Constants** | `TASK_UUID_FIELD` | str | - | - | "task_uuid" | - |
| **Constants** | `TASK_LEVEL_FIELD` | str | - | - | "task_level" | - |
| **Constants** | `TIMESTAMP_FIELD` | str | - | - | "timestamp" | - |
| **Constants** | `EXCEPTION_FIELD` | str | - | - | "exception" | - |
| **Constants** | `REASON_FIELD` | str | - | - | "reason" | - |
| **Constants** | `RESERVED_FIELDS` | tuple | - | - | Reserved field names | - |
| **Integration** | `register_exception_extractor` | `register_exception_extractor(exc_class, extractor)` | `exc_class`, `extractor` | None | Register exception handler | `register_exception_extractor(ValueError, lambda e: {"code": 1})` |
| **Errors** | `WrongTask` | Exception | - | - | Wrong task UUID | `except WrongTask:` |
| **Errors** | `WrongTaskLevel` | Exception | - | - | Wrong task level | `except WrongTaskLevel:` |
| **Errors** | `WrongActionType` | Exception | - | - | Wrong action type | `except WrongActionType:` |
| **Errors** | `InvalidStatus` | Exception | - | - | Invalid status | `except InvalidStatus:` |
| **Errors** | `DuplicateChild` | Exception | - | - | Duplicate child | `except DuplicateChild:` |
| **Errors** | `InvalidStartMessage` | Exception | - | - | Invalid start | `except InvalidStartMessage:` |
| **Errors** | `TooManyCalls` | Exception | - | - | Context called twice | `except TooManyCalls:` |
| **Compat** | `add_destination` | `add_destination(dest)` | `dest` | None | Deprecated | `add_destination(dest)` |
| **Compat** | `use_asyncio_context` | `use_asyncio_context()` | None | None | No-op (deprecated) | `use_asyncio_context()` |
| **Compat** | `_parse` | Module | - | - | Parse compatibility | For eliot-tree |
| **Compat** | `addDestination` | Alias | - | - | Legacy camelCase | `addDestination(dest)` |
| **Compat** | `removeDestination` | Alias | - | - | Legacy camelCase | `removeDestination(dest)` |
| **Compat** | `addGlobalFields` | Alias | - | - | Legacy camelCase | `addGlobalFields(x=1)` |
| **Compat** | `writeTraceback` | Alias | - | - | Legacy camelCase | `except: writeTraceback()` |
| **Compat** | `writeFailure` | Alias | - | - | Legacy camelCase | `writeFailure(exc)` |
| **Compat** | `startAction` | Alias | - | - | Legacy camelCase | `with startAction("x"):` |
| **Compat** | `startTask` | Alias | - | - | Legacy camelCase | `with startTask("x"):` |
| **Info** | `__version__` | str | - | - | Package version | `print(__version__)` |

---

## System Message Types (Eliot & LoggerX)

### Eliot System Messages

| Message Type | Purpose | Fields |
|--------------|---------|--------|
| `eliot:traceback` | Exception traceback logging | `reason`, `traceback`, `exception` |
| `eliot:destination_failure` | Destination write failure | `reason`, `exception`, `message` |
| `eliot:serialization_failure` | Message serialization failure | `message` |
| `eliot:remote_task` | Remote/cross-process task | `action_type` |
| `eliot:stdlib` | Standard library events | Various |
| `eliot:duration` | Action duration (field) | Seconds (float) |

### LoggerX Message Types

| Message Type | Level | Purpose |
|--------------|-------|---------|
| `loggerx:debug` | DEBUG | Debug level messages |
| `loggerx:info` | INFO | Info level messages |
| `loggerx:success` | SUCCESS | Success level messages |
| `loggerx:note` | NOTE | Note level messages |
| `loggerx:warning` | WARNING | Warning level messages |
| `loggerx:error` | ERROR | Error level messages |
| `loggerx:critical` | CRITICAL | Critical level messages |

---

## Part 1.5: LoggerX API

### Logger Class - Level Methods

| Method | Signature | Returns | Explain | Examples |
|--------|-----------|---------|---------|----------|
| `debug` | `debug(msg, **fields)` | `Logger` | Log at DEBUG level | `log.debug("starting", count=5)` |
| `info` | `info(msg, **fields)` | `Logger` | Log at INFO level | `log.info("user logged in", user="alice")` |
| `success` | `success(msg, **fields)` | `Logger` | Log at SUCCESS level | `log.success("completed", total=100)` |
| `note` | `note(msg, **fields)` | `Logger` | Log at NOTE level | `log.note("checkpoint", step=3)` |
| `warning` | `warning(msg, **fields)` | `Logger` | Log at WARNING level | `log.warning("slow query", ms=5000)` |
| `error` | `error(msg, **fields)` | `Logger` | Log at ERROR level | `log.error("failed", code=500)` |
| `critical` | `critical(msg, **fields)` | `Logger` | Log at CRITICAL level | `log.critical("system down")` |
| `checkpoint` | `checkpoint(msg, **fields)` | `Logger` | Log checkpoint (📍 prefix) | `log.checkpoint("step1")` |
| `exception` | `exception(msg, **fields)` | `Logger` | Log exception with traceback | `except: log.exception("error")` |
| `__call__` | `__call__(msg, **fields)` | `Logger` | Shortcut for info | `log("message")` |
| `send` | `send(msg, data, **fields)` | `Logger` | Universal send with data | `log.send("result", data)` |

### Logger Class - Type Methods

| Method | Signature | Returns | Explain | Examples |
|--------|-----------|---------|---------|----------|
| `df` | `df(data, title, **opts)` | `Logger` | Log DataFrame/pandas-like | `log.df(df, "Sales Data")` |
| `tensor` | `tensor(data, title)` | `Logger` | Log tensor/PyTorch/TF | `log.tensor(tensor)` |
| `json` | `json(data, title)` | `Logger` | Log JSON dict | `log.json({"a": 1})` |
| `img` | `img(data, title, **opts)` | `Logger` | Log image/PIL/array | `log.img(image)` |
| `plot` | `plot(fig, title)` | `Logger` | Log plot/matplotlib | `log.plot(fig)` |
| `tree` | `tree(data, title)` | `Logger` | Log tree structure | `log.tree(data)` |
| `table` | `table(data, title)` | `Logger` | Log table/list of dicts | `log.table(rows)` |

### Logger Class - Context Methods

| Method | Signature | Returns | Explain | Examples |
|--------|-----------|---------|---------|----------|
| `scope` | `scope(**ctx)` | Context manager | Create nested scope | `with log.scope(user=123):` |
| `ctx` | `ctx(**ctx)` | `Logger` | Fluent context add | `log.ctx(app="myapp").info("msg")` |
| `new` | `new(name)` | `Logger` | Create child logger | `child = log.new("module")` |
| `span` | `span(name, **attributes)` | Context manager | OpenTelemetry span | `with log.span("operation"):` |

### Logger Class - Decorators (as methods)

| Decorator | Parameters | Explain | Examples |
|-----------|------------|---------|----------|
| `logged` | level, capture_args, capture_result, exclude, timer, when, max_depth, max_length, silent_errors | Universal logging decorator | `@log.logged()` |
| `timed` | metric | Timing-only decorator | `@log.timed()` |
| `retry` | attempts, delay, backoff, on_retry | Retry decorator | `@log.retry()` |
| `generator` | name, every | Generator progress | `@log.generator()` |
| `aiterator` | name, every | Async iterator progress | `@log.aiterator()` |
| `trace` | name, kind, attributes | OpenTelemetry trace | `@log.trace()` |

### Logger Class - Config

| Method | Parameters | Explain | Examples |
|--------|------------|---------|----------|
| `configure` | level, destinations, format, context, mask_fields | Configure logger | `log.configure(level="INFO")` |

### Global Logger Instance

| Symbol | Type | Explain |
|--------|------|---------|
| `log` | `Logger` | Global logger instance | `from logxpy import log` |

---

## Part 1.6: Decorators Module

### Decorator Functions

| Decorator | Parameters | Returns | Explain | Examples |
|-----------|------------|---------|---------|----------|
| `logged` | fn=None, level="INFO", capture_args=True, capture_result=True, capture_self=False, exclude=None, timer=True, when=None, max_depth=3, max_length=500, silent_errors=False | Decorator | Universal logging with entry/exit/timing | `@logged(level="DEBUG")` |
| `timed` | metric=None | Decorator | Timing-only decorator | `@timed("db.query")` |
| `retry` | attempts=3, delay=1.0, backoff=2.0, on_retry=None | Decorator | Retry with exponential backoff | `@retry(attempts=5)` |
| `generator` | name=None, every=100 | Decorator | Generator progress tracking | `@generator(every=50)` |
| `aiterator` | name=None, every=100 | Decorator | Async iterator progress | `@aiterator()` |
| `trace` | name=None, kind="internal", attributes=None | Decorator | OpenTelemetry trace decorator | `@trace(kind="external")` |

### Usage Examples

```python
from logxpy.decorators import logged, timed, retry, generator

@logged(level="DEBUG", capture_args=False)
def process_data(x, y):
    return x + y

@timed("database.query")
def query_db():
    ...

@retry(attempts=5, delay=0.5, backoff=2)
def fetch_api():
    ...

@generator(every=1000)
def process_large_dataset():
    for item in large_data:
        yield process(item)
```

---

## Part 2: Viewer (`logxpy-cli-view`)

### CLI Commands

| Command | Options | Type | Explain | Examples |
|---------|---------|------|---------|----------|
| `logxpy-view` | `<file>` | arg | View log as tree | `logxpy-view app.log` |
| `--failed` | - | flag | Show only failed actions | `--failed` |
| `--succeeded` | - | flag | Show only succeeded | `--succeeded` |
| `--filter` | `<pattern>` | string | Filter by action name | `--filter "db"` |
| `--export` | `json` / `csv` / `html` / `logfmt` | enum | Export format | `--export json` |
| `--tail` | - | flag | Live log monitoring | `--tail` |
| `--stats` | - | flag | Show statistics | `--stats` |
| `--theme` | `dark` / `light` | enum | Color theme | `--theme light` |
| `--color` | - | flag | Enable colors | `--color` |
| `--no-color` | - | flag | Disable colors | `--no-color` |

### Core API

| Function | Prototype | Parameters | Returns | Explain | Examples |
|----------|-----------|------------|---------|---------|----------|
| `render_tasks` | `render_tasks(tasks)` | `tasks`: list | `str` | Render tasks as ASCII tree | `print(render_tasks(tasks))` |
| `tasks_from_iterable` | `tasks_from_iterable(lines)` | `lines`: iterable | Iterator | Parse log lines into tasks | `tasks = tasks_from_iterable(f)` |
| `parser_context` | `parser_context()` | None | Context manager | Parse with context | `with parser_context():` |

### Filter Functions

| Function | Prototype | Parameters | Returns | Explain | Examples |
|----------|-----------|------------|---------|---------|----------|
| `filter_by_action_status` | `filter_by_action_status(tasks, status)` | `tasks`, `status`: "succeeded"/"failed"/"started" | Filtered tasks | Filter by completion status | `filter_by_action_status(tasks, "failed")` |
| `filter_by_action_type` | `filter_by_action_type(tasks, action_type)` | `tasks`, `action_type`: str pattern | Filtered tasks | Filter by action name pattern | `filter_by_action_type(tasks, "db_*")` |
| `filter_by_duration` | `filter_by_duration(tasks, min_seconds, max_seconds)` | `tasks`, `min_seconds`: float, `max_seconds`: float | Filtered tasks | Filter by duration range | `filter_by_duration(tasks, min=1.0)` |
| `filter_by_start_date` | `filter_by_start_date(tasks, date)` | `tasks`, `date`: datetime | Filtered tasks | Filter by start time | `filter_by_start_date(tasks, dt)` |
| `filter_by_end_date` | `filter_by_end_date(tasks, date)` | `tasks`, `date`: datetime | Filtered tasks | Filter by end time | `filter_by_end_date(tasks, dt)` |
| `filter_by_relative_time` | `filter_by_relative_time(tasks, time)` | `tasks`, `time`: str (e.g. "5m ago") | Filtered tasks | Filter by relative time | `filter_by_relative_time(tasks, "1h ago")` |
| `filter_by_field_exists` | `filter_by_field_exists(tasks, field)` | `tasks`, `field`: str | Filtered tasks | Has field exists | `filter_by_field_exists(tasks, "user_id")` |
| `filter_by_keyword` | `filter_by_keyword(tasks, keyword)` | `tasks`, `keyword`: str | Filtered tasks | Search in values | `filter_by_keyword(tasks, "error")` |
| `filter_by_jmespath` | `filter_by_jmespath(tasks, query)` | `tasks`, `query`: str (JMESPath) | Filtered tasks | JMESPath query | `filter_by_jmespath(tasks, "[?status=='failed']")` |
| `filter_by_task_level` | `filter_by_task_level(tasks, level)` | `tasks`, `level`: str pattern | Filtered tasks | By task level | `filter_by_task_level(tasks, "/1/*")` |
| `filter_by_uuid` | `filter_by_uuid(tasks, uuid)` | `tasks`, `uuid`: str | Filtered tasks | By task UUID | `filter_by_uuid(tasks, "123-abc")` |
| `filter_sample` | `filter_sample(tasks, ratio)` | `tasks`, `ratio`: float (0-1) | Filtered tasks | Random sample | `filter_sample(tasks, 0.1)` |
| `combine_filters_and` | `combine_filters_and(*filters)` | `*filters` | Filtered tasks | AND combine | `combine_filters_and(f1, f2)` |
| `combine_filters_or` | `combine_filters_or(*filters)` | `*filters` | Filtered tasks | OR combine | `combine_filters_or(f1, f2)` |
| `combine_filters_not` | `combine_filters_not(filter)` | `filter` | Filtered tasks | NOT filter | `combine_filters_not(f1)` |

### Export Functions

| Function | Prototype | Parameters | Returns | Explain | Examples |
|----------|-----------|------------|---------|---------|----------|
| `export_json` | `export_json(tasks, file)` | `tasks`, `file` | None | Export as JSON | `export_json(tasks, "out.json")` |
| `export_csv` | `export_csv(tasks, file)` | `tasks`, `file` | None | Export as CSV | `export_csv(tasks, "out.csv")` |
| `export_html` | `export_html(tasks, file)` | `tasks`, `file` | None | Export as HTML | `export_html(tasks, "out.html")` |
| `export_logfmt` | `export_logfmt(tasks, file)` | `tasks`, `file` | None | Export as logfmt | `export_logfmt(tasks, "out.log")` |
| `export_tasks` | `export_tasks(tasks, file, format)` | `tasks`, `file`, `format` | None | Generic export | `export_tasks(tasks, "out", "json")` |
| `EXPORT_FORMATS` | Constant | - | `list` of str | Available formats: ["json", "csv", "html", "logfmt"] | - |
| `ExportOptions` | Class | - | - | Export configuration options | `ExportOptions(human_readable=True)` |

### Statistics

| Function | Prototype | Parameters | Returns | Explain | Examples |
|----------|-----------|------------|---------|---------|----------|
| `calculate_statistics` | `calculate_statistics(tasks)` | `tasks` | `TaskStatistics` | Compute task stats | `stats = calculate_statistics(tasks)` |
| `TaskStatistics` | Class | - | - | Stats with total_actions, succeeded_count, failed_count, duration_* | `stats.total_actions` |
| `create_time_series` | `create_time_series(tasks, interval)` | `tasks`, `interval` | `TimeSeriesData` | Time series data | `series = create_time_series(tasks, "1m")` |
| `TimeSeriesData` | Class | - | - | Time series with timestamps and counts | `series.timestamps` |
| `print_statistics` | `print_statistics(stats)` | `stats` | None | Print stats to stdout | `print_statistics(stats)` |

### Live Tail

| Function | Prototype | Parameters | Returns | Explain | Examples |
|----------|-----------|------------|---------|---------|----------|
| `tail_logs` | `tail_logs(path)` | `path`: str | None | Simple tail to stdout | `tail_logs("app.log")` |
| `watch_and_aggregate` | `watch_and_aggregate(path)` | `path`: str | Iterator | Watch and aggregate | `watch_and_aggregate("app.log")` |
| `LiveDashboard` | Class | - | - | - | Dashboard for tail | `dash = LiveDashboard()` |
| `LiveDashboard.update` | Method | `.update(tasks)` | `tasks`: list | None | Update dashboard | `dash.update(new_tasks)` |
| `LogTailer` | Class | - | `path`, `callback` | - | Tail with callback | `LogTailer("app.log", cb=func)` |
| `LogTailer.start` | Method | `.start()` | None | None | Start tailing | `tailer.start()` |
| `LogTailer.stop` | Method | `.stop()` | None | None | Stop tailing | `tailer.stop()` |

### Pattern Extraction

| Function | Prototype | Parameters | Returns | Explain | Examples |
|----------|-----------|------------|---------|---------|----------|
| `extract_urls` | `extract_urls(text)` | `text`: str | `list` of str | Find URLs | `urls = extract_urls(log_line)` |
| `extract_emails` | `extract_emails(text)` | `text`: str | `list` of str | Find emails | `emails = extract_emails(log_line)` |
| `extract_ips` | `extract_ips(text)` | `text`: str | `list` of str | Find IPs | `ips = extract_ips(log_line)` |
| `extract_uuids` | `extract_uuids(text)` | `text`: str | `list` of str | Find UUIDs | `uuids = extract_uuids(log_line)` |
| `compile_pattern` | `compile_pattern(pattern)` | `pattern`: str | Pattern | Compile regex pattern | `compile_pattern(r'\d+')` |
| `COMMON_PATTERNS` | Constant | - | `dict` | Built-in patterns: url, email, ip, uuid | - |
| `create_common_classifier` | `create_common_classifier()` | None | `LogClassifier` | Create classifier | `cls = create_common_classifier()` |
| `LogClassifier` | Class | - | - | Classify log entries | `cls.classify(entry)` |
| `LogClassifier.classify` | Method | `.classify(entry)` | `entry`: dict | Classification | Classify entry | `cls.classify(log_entry)` |
| `PatternExtractor` | Class | - | `patterns`: list | - | Extract patterns | `PatternExtractor([pat1, pat2])` |
| `PatternExtractor.extract` | Method | `.extract(text)` | `text`: str | `list` of PatternMatch | Extract all | `extractor.extract(log_line)` |
| `PatternMatch` | Class | - | - | Match with type, value, position | `match.type, match.value` |
| `create_extraction_pipeline` | `create_extraction_pipeline(patterns)` | `patterns`: list | Extractor | Multi-pattern extractor | `create_extraction_pipeline([url, email])` |

### Theme & Color

| Function | Prototype | Parameters | Returns | Explain | Examples |
|----------|-----------|------------|---------|---------|----------|
| `get_theme` | `get_theme(mode)` | `mode`: ThemeMode | `Theme` | Get color theme | `theme = get_theme(ThemeMode.LIGHT)` |
| `ThemeMode` | Enum | - | `DARK`, `LIGHT` | - | Theme mode enum | `ThemeMode.LIGHT` |
| `DarkBackgroundTheme` | Constant | - | - | `Theme` | Dark theme preset | `theme = DarkBackgroundTheme()` |
| `LightBackgroundTheme` | Constant | - | - | `Theme` | Light theme preset | `theme = LightBackgroundTheme()` |
| `Theme` | Class | - | - | - | Base theme class | Custom themes |
| `apply_theme_overrides` | `apply_theme_overrides(theme, **colors)` | `theme`, `**colors` | `Theme` | Override colors | `apply_theme_overrides(t, action_name="red")` |
| `color_factory` | `color_factory(human)` | `human`: bool | Color function | Create color function | `color = color_factory()` |
| `colored` | `colored(text, color, style)` | `text`, `color`, `style` | `str` | Colorize text | `colored("text", "cyan", "bold")` |
| `no_color` | Function | `no_color(text)` | `text` | `str` | No-op (plain text) | `no_color("text")` |

### Formatting

| Function | Prototype | Parameters | Returns | Explain | Examples |
|----------|-----------|------------|---------|---------|----------|
| `duration` | `duration(seconds)` | `seconds`: float | `str` | Format duration | `duration(123)` → "2m 3s" |
| `timestamp` | `timestamp(epoch)` | `epoch`: float | `str` | Format timestamp | `timestamp(1234567890.123)` |
| `text` | `text(value, encoding)` | `value`, `encoding`: str | `str` | Format as text | `text(b"bytes")` |
| `binary` | `binary(value)` | `value`: bytes | `str` | Format binary | `binary(b"\x00")` |
| `anything` | `anything(value)` | `value`: any | `str` | Format any value | `anything(obj)` |
| `some` | `some(value)` | `value`: any | `str` | Format optional | `some(None)` |
| `format_any` | `format_any(value)` | `value`: any | `str` | Format with type detection | `format_any(val)` |
| `truncate_value` | `truncate_value(value, max_len)` | `value`, `max_len`: int | `str` | Truncate long values | `truncate_value(s, 50)` |
| `escape_control_characters` | `escape_control_characters(text)` | `text`: str | `str` | Escape control chars | `escape_control_characters(data)` |
| `fields` | `fields(dict)` | `dict`: dict | `str` | Format dict as fields | `fields({"a": 1})` |

### Rendering

| Name | Type | Prototype | Parameters | Returns | Explain | Examples |
|-----|------|-----------|------------|---------|---------|----------|
| `ColorizedOptions` | Class | - | - | - | Rendering config | `ColorizedOptions(human_readable=True)` |
| `NodeFormatter` | Class | - | options | - | Format tree nodes | `NodeFormatter(options=opts)` |
| `format_node` | Function | `format_node(node, formatter)` | `node`, `formatter` | `str` | Format single node | `format_node(task, formatter)` |
| `DEFAULT_IGNORED_KEYS` | Constant | - | - | `list` of str | Keys hidden by default | - |
| `render_tasks` | Function | `render_tasks(tasks, options)` | `tasks`, `options` | `str` | Render tasks to tree | `render_tasks(tasks)` |
| `get_children` | Function | `get_children(task)` | `task` | `list` | Get child tasks | `get_children(task)` |
| `track_exceptions` | Function | `track_exceptions(tasks)` | `tasks` | `dict` | Track exceptions | `track_exceptions(tasks)` |

### Utilities

| Function | Prototype | Parameters | Returns | Explain | Examples |
|----------|-----------|------------|---------|---------|----------|
| `message_fields` | `message_fields(msg)` | `msg`: dict | `dict` | Get message fields | `message_fields(msg)` |
| `message_name` | `message_name(msg)` | `msg`: dict | `str` | Get message name | `message_name(msg)` |
| `eliot_ns` | `eliot_ns(**fields)` | `**fields` | `Namespace` | Create Eliot namespace | `eliot_ns(action_type="x")` |
| `format_namespace` | `format_namespace(ns)` | `ns` | `str` | Format namespace | `format_namespace(ns)` |
| `is_namespace` | `is_namespace(obj)` | `obj` | `bool` | Check if namespace | `is_namespace(obj)` |
| `namespaced` | `namespaced(**fields)` | `**fields` | `Namespace` | Create namespaced dict | `namespaced(x=1)` |
| `_Namespace` | Class | - | - | - | Namespace object | Eliot compatibility |
| `Writable` | Protocol | - | - | Write protocol | For file-like objects |

### Errors

| Exception | Explain | Examples |
|-----------|-------------|----------|
| `ConfigError` | Configuration errors | `raise ConfigError("Invalid")` |
| `EliotParseError` | Log parsing failed | `except EliotParseError:` |
| `JSONParseError` | Invalid JSON | `except JSONParseError:` |

### Compatibility

| Name | Type | Prototype | Explain | Examples |
|------|------|-----------|-------------|----------|
| `deprecated` | Decorator | `@deprecated(message)` | Mark deprecated | `@deprecated("Use X")` |
| `catch_errors` | Decorator / Context | - | Catch errors | `@catch_errors` |
| `dump_json_bytes` | Function | `dump_json_bytes(data)` | Dump as JSON bytes | `dump_json_bytes({"a": 1})` |
| `__version__` | `str` | - | Package version | `print(__version__)` |

