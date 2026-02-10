# log-x-py - AI Context (2026 Optimized)

> **Complete API reference for AI assistants working with log-x-py ecosystem**
>
> **Three Components:**
> 1. **logxpy** - Structured logging library (Python 3.12+)
> 2. **logxpy-cli-view** - CLI viewer tool (`logxpy-view`)
> 3. **logxy-log-parser** - Log parsing & analysis library

---

## Quick Reference for AI Assistants

### Installation & Setup

```bash
# Install all components
uv pip install -e ./logxpy
uv pip install -e ./logxpy_cli_view
uv pip install -e ./logxy_log_parser

# Or use pip
pip install -e ./logxpy
```

### Essential CLI Commands

```bash
# View logs as ASCII tree (default render command)
logxpy-view app.log
logxpy-view render app.log          # Explicit render

# Filter by status
logxpy-view --status failed app.log
logxpy-view --status succeeded app.log

# Export to formats (subcommand style)
logxpy-view export app.log -f json -o out.json
logxpy-view export app.log -f csv -o out.csv
logxpy-view export app.log -f html -o out.html
logxpy-view export app.log -f logfmt -o out.log

# Statistics
logxpy-view stats app.log
logxpy-view stats app.log -o stats.json

# Live monitoring
logxpy-view tail app.log
logxpy-view tail app.log -f          # Follow mode
logxpy-view tail app.log -d          # Live dashboard
```

### Python Quick Start

```python
# Basic logging
from logxpy import start_action, to_file, Message

to_file(open("app.log", "w"))
with start_action("main"):
    Message.log(info="starting")

# Parse logs
from logxy_log_parser import parse_log, analyze_log

entries = parse_log("app.log")
report = analyze_log("app.log")
report.print_summary()

# Filter and render
from logxpy_cli_view import tasks_from_iterable, filter_by_action_status, render_tasks

with open("app.log") as f:
    tasks = list(tasks_from_iterable(f))

failed = filter_by_action_status(tasks, "failed")
print(render_tasks(failed))
```

---

# Component 1: logxpy (Logging Library)

## Core Imports

```python
# Most commonly used imports
from logxpy import (
    start_action,      # Begin hierarchical action
    start_task,        # Top-level action
    Message,           # Structured messages
    to_file,           # Set output destination
    log,               # LoggerX instance
    current_action,    # Get active action
    write_traceback,   # Log exceptions
)
```

## Compact Field Names (Log Entry Structure)

LogXPy uses 1-2 character field names for minimal log size:

| Compact | Legacy | Meaning |
|---------|--------|---------|
| `ts` | `timestamp` | Unix timestamp (seconds) |
| `tid` | `task_uuid` | Task ID (Sqid format, 4-12 chars) |
| `lvl` | `task_level` | Hierarchy level array `[1, 2, 1]` |
| `mt` | `message_type` | Log level: info, success, error, etc. |
| `at` | `action_type` | Action type (for emoji: db:query, http:request) |
| `st` | `action_status` | started/succeeded/failed |
| `dur` | `duration` | Duration in seconds |

**Example log entry:**
```json
{"ts":1770563890.78,"tid":"gD.1","lvl":[1],"mt":"info","msg":"Hello"}
```

## Task ID Format (Sqid)

| Format | Example | Length | Use Case |
|--------|---------|--------|----------|
| Root | `"Xa.1"` | 4 chars | Top-level task |
| Child | `"Xa.1.1"` | 6 chars | Nested action |
| Deep | `"Xa.1.1.2"` | 8 chars | 3 levels deep |

**Environment variable for distributed mode (UUID4):**
```bash
LOGXPY_DISTRIBUTED=1  # Forces UUID4 for distributed tracing
```

## Core API Functions

| Function | Signature | Returns | Purpose | Example |
|----------|-----------|---------|---------|---------|
| `start_action` | `start_action(action_type='', **fields)` | Context manager | Begin hierarchical action | `with start_action("db_query", table="users"):` |
| `start_task` | `start_task(action_type='', **fields)` | Context manager | Top-level action | `with start_task("process"):` |
| `log` | `log(message_type, **fields)` | None | Log in current action | `log(message_type="event", x=1)` |
| `current_action` | `current_action()` | Action or None | Get active action | `action = current_action()` |
| `write_traceback` | `write_traceback(logger=None, exc_info=None)` | None | Log exception | `except: write_traceback()` |
| `to_file` | `to_file(output_file)` | None | Set log destination | `to_file(open("app.log", "a"))` |
| `Message.log` | `Message.log(**fields)` | None | Log structured message | `Message.log(info="starting", count=5)` |

## Action Context Manager Methods

| Method | Signature | Returns | Purpose | Example |
|--------|-----------|---------|---------|---------|
| `Action.finish` | `finish(exception=None)` | None | Complete action | `action.finish()` |
| `Action.child` | `child(logger, action_type)` | Action | Create child | `action.child(logger, "subtask")` |
| `Action.run` | `run(f, *args, **kwargs)` | Any | Run in context | `action.run(func, 1, 2)` |
| `Action.add_success_fields` | `add_success_fields(**fields)` | None | Add on success | `action.add_success_fields(result=5)` |
| `Action.context` | `context()` | Context manager | Run without finish | `with action.context():` |

## TaskLevel Class

| Method | Returns | Purpose | Example |
|--------|---------|---------|---------|
| `TaskLevel.from_string(s)` | TaskLevel | Parse from string | `TaskLevel.from_string("/1/2")` |
| `as_list()` | list | Get as list | `level.as_list()` |
| `to_string()` | str | Convert to string | `level.to_string()` |
| `next_sibling()` | TaskLevel | Next sibling | `level.next_sibling()` |
| `child()` | TaskLevel | Child level | `level.child()` |
| `parent()` | TaskLevel or None | Parent level | `level.parent()` |

## LoggerX Fluent API

### Level Methods (all return `Logger` for chaining)

| Method | Level | Example |
|--------|-------|---------|
| `log.debug(msg, **fields)` | DEBUG | `log.debug("starting", count=5)` |
| `log.info(msg, **fields)` | INFO | `log.info("user login", user="alice")` |
| `log.success(msg, **fields)` | SUCCESS | `log.success("completed", total=100)` |
| `log.note(msg, **fields)` | NOTE | `log.note("checkpoint", step=3)` |
| `log.warning(msg, **fields)` | WARNING | `log.warning("slow query", ms=5000)` |
| `log.error(msg, **fields)` | ERROR | `log.error("failed", code=500)` |
| `log.critical(msg, **fields)` | CRITICAL | `log.critical("system down")` |
| `log.checkpoint(msg, **fields)` | CHECKPOINT (📍) | `log.checkpoint("step1")` |
| `log.exception(msg, **fields)` | ERROR + traceback | `except: log.exception("error")` |

### Flexible `__call__` Method

| Usage | Equivalent To | Example |
|-------|---------------|---------|
| `log("msg")` | `log.info("msg")` | `log("Starting")` |
| `log("title", data)` | `log.info("title", value=data)` | `log("User", {"id": 1})` |
| `log(data)` | `log.send(auto_title, data)` | `log({"key": "val"})` |

### Context Methods

| Method | Returns | Purpose | Example |
|--------|---------|---------|---------|
| `log.scope(**ctx)` | Context manager | Nested scope | `with log.scope(user_id=123):` |
| `log.ctx(**ctx)` | Logger | Fluent context | `log.ctx(user_id=123).info("msg")` |
| `log.new(name)` | Logger | Child logger | `child = log.new("database")` |
| `log.span(name, **attrs)` | Context manager | OpenTelemetry span | `with log.span("query"):` |

### Color Methods (for CLI viewer)

| Method | Purpose | Example |
|--------|---------|---------|
| `log.set_foreground(color)` | Set text color | `log.set_foreground("cyan")` |
| `log.set_background(color)` | Set background | `log.set_background("yellow")` |
| `log.reset_foreground()` | Reset text | `log.reset_foreground()` |
| `log.reset_background()` | Reset background | `log.reset_background()` |
| `log.colored(msg, fg, bg)` | One-shot color | `log.colored("Important!", "red", "yellow")` |

**Colors:** black, red, green, yellow, blue, magenta, cyan, white, light_gray, dark_gray, light_red, light_green, light_blue, light_yellow, light_magenta, light_cyan

### Data Type Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `log.color(value, title)` | RGB/hex colors | `log.color((255, 0, 0), "Theme")` |
| `log.currency(amount, code)` | Currency with precision | `log.currency("19.99", "USD")` |
| `log.datetime(dt, title)` | DateTime formats | `log.datetime(dt, "StartTime")` |
| `log.enum(enum_value, title)` | Enum name/value | `log.enum(Status.ACTIVE)` |
| `log.json(data, title)` | JSON formatted | `log.json({"key": "val"}, "Config")` |
| `log.df(data, title)` | DataFrame | `log.df(df, "Results")` |
| `log.tensor(data, title)` | Tensor/PyTorch/TF | `log.tensor(tensor)` |
| `log.img(data, title)` | Image/PIL/array | `log.img(image)` |
| `log.plot(fig, title)` | Matplotlib plot | `log.plot(fig)` |
| `log.tree(data, title)` | Tree structure | `log.tree(data)` |
| `log.table(data, title)` | List of dicts | `log.table(rows)` |

### System Info Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `log.system_info()` | OS/platform info | `log.system_info()` |
| `log.memory_status()` | Memory statistics | `log.memory_status()` |
| `log.stack_trace(limit)` | Call stack | `log.stack_trace(10)` |

### LoggerX Initialization

| Method | Purpose | Example |
|--------|---------|---------|
| `log.init()` | Auto-generate log filename | `log.init()` |
| `log.init(path)` | Specify file | `log.init("app.log")` |
| `log.init(path, level, mode)` | Full config | `log.init("app.log", level="INFO", mode="w")` |
| `log.configure(**opts)` | Advanced config | `log.configure(level="DEBUG", destinations=[...])` |

## Decorators

| Decorator | Parameters | Purpose | Example |
|-----------|------------|---------|---------|
| `@logged` | level, capture_args, capture_result, exclude, timer, when, max_depth, max_length, silent_errors | Universal logging | `@logged(level="DEBUG")` |
| `@timed` | metric=None | Timing only | `@timed("db.query")` |
| `@retry` | attempts=3, delay=1.0, backoff=2.0, on_retry=None | Retry with backoff | `@retry(attempts=5)` |
| `@generator` | name=None, every=100 | Generator progress | `@generator(every=50)` |
| `@aiterator` | name=None, every=100 | Async iterator | `@aiterator()` |
| `@trace` | name=None, kind="internal", attributes=None | OpenTelemetry | `@trace(kind="external")` |

**Decorator access:**
```python
from logxpy import logged, timed, retry, generator, aiterator, trace

# Or via LoggerX
@log.logged()
def my_function():
    pass

@log.timed("metric.name")
def my_function():
    pass
```

## Category System

| Class/Function | Purpose | Example |
|----------------|---------|---------|
| `CategorizedLogger(name)` | Logger with prefix | `cat_log = CategorizedLogger("database")` |
| `category_context(name)` | Context manager | `with category_context("db"):` |
| `Category(name)` | Global manager | `Category("database")` |
| `log.with_category(name)` | Categorized logger | `db_log = log.with_category("database")` |

## Output Destinations

| Class/Function | Purpose | Example |
|----------------|---------|---------|
| `to_file(file)` | Set file output | `to_file(open("app.log", "a"))` |
| `add_destinations(*dests)` | Add multiple outputs | `add_destinations(d1, d2)` |
| `remove_destination(dest)` | Remove output | `remove_destination(dest)` |
| `add_global_fields(**fields)` | Add to all messages | `add_global_fields(app="myapp")` |
| `FileDestination(file)` | File output wrapper | `FileDestination(f)` |
| `BufferingDestination()` | In-memory buffer | `BufferingDestination()` |
| `Destinations()` | Manage destinations | `Destinations().add(dest)` |

## Testing Utilities

| Class | Purpose | Example |
|-------|---------|---------|
| `MemoryLogger()` | In-memory for testing | `logger = MemoryLogger()` |
| `MemoryLogger.validate()` | Validate messages | `logger.validate()` |
| `MemoryLogger.serialize()` | Get messages | `logger.serialize()` |
| `MemoryLogger.reset()` | Clear messages | `logger.reset()` |

## Exception Handling

| Function | Purpose | Example |
|----------|---------|---------|
| `write_traceback(logger, exc_info)` | Log exception | `except: write_traceback()` |
| `write_failure(failure, logger)` | Log Twisted Failure | `write_failure(failure)` |
| `register_exception_extractor(cls, fn)` | Custom handler | `register_exception_extractor(ValueError, lambda e: {"code": 1})` |

## Validation

| Class/Function | Purpose | Example |
|----------------|---------|---------|
| `MessageType` | Message schema base | `class Msg(MessageType): x = Field(int)` |
| `ActionType` | Action schema base | `class Act(ActionType): table = Field(str)` |
| `Field(key, serializer)` | Define field | `Field("x", int)` |
| `fields.integer` | Integer validator | `Field(fields.integer)` |
| `fields.text` | Text validator | `Field(fields.text)` |
| `fields.success` | Boolean validator | `Field(fields.success)` |

## Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `TRACEBACK_MESSAGE` | MessageType | Traceback message type |
| `STARTED_STATUS` | "started" | Action started |
| `SUCCEEDED_STATUS` | "succeeded" | Action succeeded |
| `FAILED_STATUS` | "failed" | Action failed |
| `MT` | "mt" | Message type key (compact) |
| `AT` | "at" | Action type key (compact) |
| `ST` | "st" | Action status key (compact) |
| `TID` | "tid" | Task ID key (compact) |
| `LVL` | "lvl" | Task level key (compact) |
| `TS` | "ts" | Timestamp key (compact) |
| `DUR` | "dur" | Duration key (compact) |
| `MSG` | "msg" | Message key (compact) |

## System Message Types

### LogXPy System Messages

| Message Type | Purpose |
|--------------|---------|
| `logxpy:traceback` | Exception traceback |
| `logxpy:destination_failure` | Destination write failure |
| `logxpy:serialization_failure` | Message serialization failure |
| `logxpy:remote_task` | Remote/cross-process task |

### LoggerX Message Types

| Message Type | Level | Purpose |
|--------------|-------|---------|
| `loggerx:debug` | DEBUG | Debug messages |
| `loggerx:info` | INFO | Info messages |
| `loggerx:success` | SUCCESS | Success messages |
| `loggerx:note` | NOTE | Note messages |
| `loggerx:warning` | WARNING | Warning messages |
| `loggerx:error` | ERROR | Error messages |
| `loggerx:critical` | CRITICAL | Critical messages |

## Emoji Auto-Detection (by action_type)

| Pattern | Emoji |
|---------|-------|
| database, db:, query | 💾 |
| http, api, request | 🔌 |
| auth, login | 🔐 |
| payment, charge | 💳 |
| server | 🖥️ |
| pipeline, etl | 🔄 |
| error, fail | 🔥 |
| default | ⚡ |

---

# Component 2: logxpy-cli-view (Viewer)

## CLI Structure

The CLI uses **subcommands** with legacy fallback (no subcommand = render):

```
logxpy-view [COMMAND] [OPTIONS] [FILE]
```

### Commands

| Command | Aliases | Purpose |
|---------|---------|---------|
| `render` | r, show | View logs as tree (default) |
| `stats` | s, statistics | Show statistics |
| `export` | e, convert | Export to formats |
| `tail` | t, watch, follow | Live monitoring |

### CLI Examples

```bash
# Render (default command, optional)
logxpy-view app.log
logxpy-view render app.log
logxpy-view r app.log

# Filtering
logxpy-view --status failed app.log
logxpy-view --action-type "db:*" app.log
logxpy-view --keyword "error" app.log
logxpy-view --min-duration 1.0 app.log
logxpy-view --select "[?level=='error']" app.log

# Display options
logxpy-view --human-readable app.log
logxpy-view --raw app.log
logxpy-view --ascii app.log
logxpy-view --no-color-tree app.log
logxpy-view --theme light app.log

# Export
logxpy-view export app.log -f json -o out.json
logxpy-view export app.log -f csv -o out.csv
logxpy-view export app.log -f html -o out.html
logxpy-view export app.log -f logfmt -o out.log

# Stats
logxpy-view stats app.log
logxpy-view stats app.log -o stats.json

# Tail/Live
logxpy-view tail app.log
logxpy-view tail app.log -f           # Follow mode
logxpy-view tail app.log -d           # Dashboard
logxpy-view tail app.log -a           # Aggregate stats
```

## Filtering Options (render command)

| Option | Type | Purpose | Example |
|--------|------|---------|---------|
| `-u, --task-uuid` | UUID | Filter by task ID | `--task-uuid "Xa.1"` |
| `--select` | JMESPath | JMESPath query | `--select "[?status=='failed']"` |
| `--start` | ISO8601 | Filter after date | `--start "2024-01-01"` |
| `--end` | ISO8601 | Filter before date | `--end "2024-12-31"` |
| `--status` | enum | Filter by status | `--status failed` |
| `--action-type` | pattern | Filter by action type | `--action-type "db:*"` |
| `--action-type-regex` | flag | Treat as regex | `--action-type-regex` |
| `--min-duration` | float | Min duration (sec) | `--min-duration 1.0` |
| `--max-duration` | float | Max duration (sec) | `--max-duration 10.0` |
| `--has-field` | field | Field exists | `--has-field "user_id"` |
| `--keyword` | text | Search values | `--keyword "error"` |
| `--min-level` | int | Min depth (1=top) | `--min-level 2` |
| `--max-level` | int | Max depth | `--max-level 3` |

## Display Options (render command)

| Option | Type | Purpose | Example |
|--------|------|---------|---------|
| `--human-readable` | flag | Format values (default) | on |
| `--raw` | flag | No formatting | `--raw` |
| `--local-timezone` | flag | Local timestamps | `--local-timezone` |
| `--color` | enum | Color mode | `--color always` |
| `--ascii` | flag | ASCII tree | `--ascii` |
| `--no-color-tree` | flag | Plain tree lines | `--no-color-tree` |
| `--theme` | enum | Color theme | `--theme light` |
| `-l, --field-limit` | int | Truncate values | `--field-limit 50` |
| `--no-line-numbers` | flag | Hide line numbers | `--no-line-numbers` |
| `--format` | enum | Output format | `--format tree` |

## Export Options (export command)

| Option | Type | Purpose | Example |
|--------|------|---------|---------|
| `-f, --format` | enum | Format: json/csv/html/logfmt | `-f json` |
| `-o, --output` | path | Output file | `-o out.json` |
| `--indent` | int | JSON indentation | `--indent 2` |
| `--include-fields` | list | Fields to include | `--include-fields timestamp` |
| `--exclude-fields` | list | Fields to exclude | `--exclude-fields traceback` |
| `--title` | string | HTML page title | `--title "My Logs"` |

## Tail Options (tail command)

| Option | Type | Purpose | Example |
|--------|------|---------|---------|
| `-n, --lines` | int | Initial lines | `-n 20` |
| `-f, --follow` | flag | Follow new entries | `-f` |
| `--no-follow` | flag | Don't follow | `--no-follow` |
| `-d, --dashboard` | flag | Live dashboard | `-d` |
| `-a, --aggregate` | flag | Periodic stats | `-a` |
| `-i, --interval` | int | Aggregation interval (sec) | `-i 5` |
| `-r, --refresh` | float | Dashboard refresh (sec) | `-r 1.0` |

## Core Python API

| Function | Signature | Returns | Purpose | Example |
|----------|-----------|---------|---------|---------|
| `tasks_from_iterable` | `tasks_from_iterable(lines)` | Iterator | Parse log lines | `tasks = list(tasks_from_iterable(f))` |
| `render_tasks` | `render_tasks(tasks, write=None, **options)` | str | Render tree | `print(render_tasks(tasks))` |
| `render_oneline` | `render_oneline(tasks, write=None, theme=None)` | None | One-line format | `render_oneline(tasks)` |

## Filter Functions

| Function | Signature | Returns | Purpose | Example |
|----------|-----------|---------|---------|---------|
| `filter_by_action_status` | `filter_by_action_status(tasks, status)` | Iterator | By status | `filter_by_action_status(tasks, "failed")` |
| `filter_by_action_type` | `filter_by_action_type(tasks, pattern, regex=False)` | Iterator | By action type | `filter_by_action_type(tasks, "db_*")` |
| `filter_by_duration` | `filter_by_duration(tasks, min_seconds=None, max_seconds=None)` | Iterator | By duration | `filter_by_duration(tasks, min_seconds=1.0)` |
| `filter_by_start_date` | `filter_by_start_date(tasks, date)` | Iterator | After date | `filter_by_start_date(tasks, dt)` |
| `filter_by_end_date` | `filter_by_end_date(tasks, date)` | Iterator | Before date | `filter_by_end_date(tasks, dt)` |
| `filter_by_field_exists` | `filter_by_field_exists(tasks, field)` | Iterator | Has field | `filter_by_field_exists(tasks, "user_id")` |
| `filter_by_keyword` | `filter_by_keyword(tasks, keyword)` | Iterator | Search values | `filter_by_keyword(tasks, "error")` |
| `filter_by_jmespath` | `filter_by_jmespath(tasks, query)` | Iterator | JMESPath | `filter_by_jmespath(tasks, "[?status=='failed']")` |
| `filter_by_task_level` | `filter_by_task_level(tasks, min_level=None, max_level=None)` | Iterator | By depth | `filter_by_task_level(tasks, min_level=2)` |
| `filter_by_uuid` | `filter_by_uuid(tasks, *uuids)` | Iterator | By task ID | `filter_by_uuid(tasks, "Xa.1")` |
| `filter_sample` | `filter_sample(tasks, ratio)` | Iterator | Random sample | `filter_sample(tasks, 0.1)` |
| `combine_filters_and` | `combine_filters_and(*filters)` | callable | AND combine | `combine_filters_and(f1, f2)` |
| `combine_filters_or` | `combine_filters_or(*filters)` | callable | OR combine | `combine_filters_or(f1, f2)` |
| `combine_filters_not` | `combine_filters_not(filter)` | callable | NOT filter | `combine_filters_not(f1)` |

## Export Functions

| Function | Signature | Returns | Purpose | Example |
|----------|-----------|---------|---------|---------|
| `export_json` | `export_json(tasks, file, **options)` | int (count) | Export JSON | `export_json(tasks, "out.json")` |
| `export_csv` | `export_csv(tasks, file, **options)` | int | Export CSV | `export_csv(tasks, "out.csv")` |
| `export_html` | `export_html(tasks, file, title=None)` | int | Export HTML | `export_html(tasks, "out.html")` |
| `export_logfmt` | `export_logfmt(tasks, file, **options)` | int | Export logfmt | `export_logfmt(tasks, "out.log")` |
| `export_tasks` | `export_tasks(tasks, output, format, options=None, title=None)` | int | Generic export | `export_tasks(tasks, "out", "json")` |
| `EXPORT_FORMATS` | Constant | list[str] | Available formats | `["json", "csv", "html", "logfmt"]` |

## Statistics Functions

| Function | Signature | Returns | Purpose | Example |
|----------|-----------|---------|---------|---------|
| `calculate_statistics` | `calculate_statistics(tasks)` | TaskStatistics | Compute stats | `stats = calculate_statistics(tasks)` |
| `print_statistics` | `print_statistics(stats)` | None | Print to stdout | `print_statistics(stats)` |
| `create_time_series` | `create_time_series(tasks, interval)` | TimeSeriesData | Time series | `create_time_series(tasks, "1m")` |

## Tail/Live Monitoring

| Function/Class | Signature | Returns | Purpose | Example |
|----------------|-----------|---------|---------|---------|
| `tail_logs` | `tail_logs(path, follow=True, lines=10, **opts)` | None | Tail to stdout | `tail_logs("app.log")` |
| `watch_and_aggregate` | `watch_and_aggregate(path, interval=5)` | Iterator | Watch & aggregate | `watch_and_aggregate("app.log")` |
| `LiveDashboard` | `LiveDashboard(path, refresh_rate=1.0)` | Class | Live dashboard | `LiveDashboard("app.log").run()` |

## Pattern Extraction

| Function | Signature | Returns | Purpose | Example |
|----------|-----------|---------|---------|---------|
| `extract_urls` | `extract_urls(text)` | list[str] | Find URLs | `extract_urls(log_line)` |
| `extract_emails` | `extract_emails(text)` | list[str] | Find emails | `extract_emails(log_line)` |
| `extract_ips` | `extract_ips(text)` | list[str] | Find IPs | `extract_ips(log_line)` |
| `extract_uuids` | `extract_uuids(text)` | list[str] | Find UUIDs | `extract_uuids(log_line)` |
| `COMMON_PATTERNS` | Constant | dict | Built-in patterns | `COMMON_PATTERNS["url"]` |

## Theme & Color

| Function | Signature | Returns | Purpose | Example |
|----------|-----------|---------|---------|---------|
| `get_theme` | `get_theme(dark_background=True, colored=None)` | Theme | Get theme | `get_theme()` |
| `ThemeMode` | Enum | DARK/LIGHT/AUTO | Theme mode | `ThemeMode.DARK` |
| `apply_theme_overrides` | `apply_theme_overrides(theme, **colors)` | Theme | Override colors | `apply_theme_overrides(t, action_name="red")` |
| `colored` | `colored(text, color, style=None)` | str | Colorize | `colored("text", "cyan", "bold")` |

## Formatting Utilities

| Function | Signature | Returns | Purpose | Example |
|----------|-----------|---------|---------|---------|
| `duration` | `duration(seconds)` | str | Format duration | `duration(123)` → "2m 3s" |
| `timestamp` | `timestamp(epoch)` | str | Format timestamp | `timestamp(1234567890.123)` |
| `truncate_value` | `truncate_value(value, max_len)` | str | Truncate | `truncate_value(s, 50)` |
| `format_any` | `format_any(value)` | str | Format with type | `format_any(val)` |

## Error Classes

| Exception | Purpose |
|-----------|---------|
| `ConfigError` | Configuration errors |
| `LogXPyParseError` | Log parsing failed |
| `EliotParseError` | Alias for LogXPyParseError |
| `JSONParseError` | Invalid JSON |

---

# Component 3: logxy-log-parser (Log Parser & Analyzer)

## Simple One-Line API

| Function | Returns | Purpose | Example |
|----------|---------|---------|---------|
| `parse_log(source)` | ParseResult | Parse log file | `entries = parse_log("app.log")` |
| `parse_line(line)` | LogXPyEntry or None | Parse single line | `entry = parse_line(json_str)` |
| `check_log(source)` | CheckResult | Parse + validate | `result = check_log("app.log")` |
| `analyze_log(source)` | AnalysisReport | Full analysis | `report = analyze_log("app.log")` |

## Core Classes

| Class | Purpose | Example |
|-------|---------|---------|
| `LogFile` | File handle + real-time monitoring | `logfile = LogFile.open("app.log")` |
| `LogParser` | Parse log files | `parser = LogParser("app.log")` |
| `LogEntries` | Collection with filtering/export | `logs = parser.parse()` |
| `LogFilter` | Chainable filters | `errors = LogFilter(logs).by_level("error")` |
| `LogAnalyzer` | Performance/error analysis | `analyzer = LogAnalyzer(logs)` |
| `TaskTree` | Hierarchical task tree | `tree = parser.build_task_tree()` |
| `TaskNode` | Node in task tree | `node = tree.root` |
| `LogIndex` | Fast lookups via indexing | `index = LogIndex.build("app.log")` |
| `IndexedLogParser` | Parser with index | `parser = IndexedLogParser("app.log")` |
| `TimeSeriesAnalyzer` | Time-series analysis | `analyzer = TimeSeriesAnalyzer(logs)` |
| `LogAggregator` | Multi-file aggregation | `agg = LogAggregator(files)` |
| `MultiFileAnalyzer` | Cross-file analysis | `multi = MultiFileAnalyzer(files)` |

## LogFile API (Real-time Monitoring)

| Method | Returns | Purpose | Example |
|--------|---------|---------|---------|
| `LogFile.open(path)` | LogFile | Open and validate | `logfile = LogFile.open("app.log")` |
| `entry_count` | int | Get entry count (fast) | `logfile.entry_count` |
| `contains_error()` | bool | Check for errors | `logfile.contains_error()` |
| `contains(**criteria)` | bool | Check contains | `logfile.contains(level="error")` |
| `find_first(**criteria)` | LogXPyEntry or None | Find first match | `logfile.find_first(level="error")` |
| `find_all(**criteria)` | LogEntries | Find all matches | `logfile.find_all(level="error")` |
| `tail(n)` | LogEntries | Last N entries | `logfile.tail(10)` |
| `watch()` | Iterator | Iterate new entries | `for entry in logfile.watch():` |
| `wait_for_message(text, timeout)` | LogXPyEntry | Wait for message | `logfile.wait_for_message("ready", 30)` |
| `wait_for_error(timeout)` | LogXPyEntry | Wait for error | `logfile.wait_for_error(60)` |

## LogFilter Methods (all return LogEntries for chaining)

| Method | Purpose | Example |
|--------|---------|---------|
| `by_level(*levels)` | Filter by log level | `.by_level("error", "warning")` |
| `by_message(pattern)` | Filter by message text | `.by_message("database")` |
| `by_time_range(start, end)` | Filter by time range | `.by_time_range("2024-01-01", "2024-12-31")` |
| `by_task_uuid(*uuids)` | Filter by task ID | `.by_task_uuid("Xa.1")` |
| `by_action_type(*types)` | Filter by action type | `.by_action_type("db:*")` |
| `by_field(field, value)` | Filter by field value | `.by_field("user_id", 123)` |
| `by_duration(min, max)` | Filter by duration | `.by_duration(min=1.0)` |
| `by_nesting_level(min, max)` | Filter by depth | `.by_nesting_level(1, 3)` |
| `with_traceback()` | Entries with tracebacks | `.with_traceback()` |
| `failed_actions()` | Failed actions only | `.failed_actions()` |
| `succeeded_actions()` | Succeeded actions only | `.succeeded_actions()` |
| `slow_actions(threshold)` | Slow actions only | `.slow_actions(5.0)` |
| `fast_actions(threshold)` | Fast actions only | `.fast_actions(0.001)` |

## LogAnalyzer Methods

| Method | Returns | Purpose | Example |
|--------|---------|---------|---------|
| `slowest_actions(n)` | list[ActionStat] | Slowest actions | `analyzer.slowest_actions(10)` |
| `fastest_actions(n)` | list[ActionStat] | Fastest actions | `analyzer.fastest_actions(10)` |
| `duration_by_action()` | dict[str, DurationStats] | Duration by action | `analyzer.duration_by_action()` |
| `error_summary()` | ErrorSummary | Error analysis | `analyzer.error_summary()` |
| `error_patterns()` | list[ErrorPattern] | Find error patterns | `analyzer.error_patterns()` |
| `failure_rate_by_action()` | dict[str, float] | Failure rate per action | `analyzer.failure_rate_by_action()` |
| `deepest_nesting()` | int | Maximum depth | `analyzer.deepest_nesting()` |
| `orphans()` | LogEntries | Unmatched entries | `analyzer.orphans()` |
| `timeline(interval)` | Timeline | Timeline data | `analyzer.timeline(3600)` |
| `peak_periods(n)` | list[TimePeriod] | Busiest periods | `analyzer.peak_periods(5)` |
| `generate_report(format)` | str | Generate report | `analyzer.generate_report("html")` |

## Indexing System

| Class/Method | Purpose | Example |
|--------------|---------|---------|
| `LogIndex.build(path)` | Build index | `index = LogIndex.build("app.log")` |
| `index.find_by_task(uuid)` | Find by task UUID | `index.find_by_task("Xa.1")` |
| `index.find_by_level(level)` | Find by level | `index.find_by_level("error")` |
| `index.find_by_time_range(start, end)` | Find by time range | `index.find_by_time_range(start, end)` |
| `IndexedLogParser(path)` | Indexed parser | `parser = IndexedLogParser("app.log")` |
| `parser.query(**criteria)` | Query with criteria | `parser.query(task_uuid="Xa.1")` |

## Time Series Analysis

| Method | Returns | Purpose | Example |
|--------|---------|---------|---------|
| `bucket_by_interval(seconds)` | list[TimeBucket] | Bucket by time | `analyzer.bucket_by_interval(3600)` |
| `detect_anomalies(window, threshold)` | list[Anomaly] | Detect anomalies | `analyzer.detect_anomalies(10, 2.0)` |
| `error_rate_t(interval)` | list[tuple] | Error rate over time | `analyzer.error_rate_t(60)` |
| `level_distribution(interval)` | dict | Level distribution | `analyzer.level_distribution(3600)` |
| `activity_heatmap(hour_granularity)` | dict | Activity heatmap | `analyzer.activity_heatmap(1)` |
| `burst_detection(threshold, min_interval)` | list[Burst] | Detect bursts | `analyzer.burst_detection(100, 60)` |

## Aggregation & Multi-File Analysis

| Class/Method | Purpose | Example |
|--------------|---------|---------|
| `LogAggregator(files)` | Aggregate multiple files | `agg = LogAggregator(["f1.log", "f2.log"])` |
| `aggregator.aggregate()` | AggregateResult | Aggregate all files | `agg.aggregate()` |
| `MultiFileAnalyzer(files)` | Analyze multiple files | `multi = MultiFileAnalyzer(files)` |
| `multi.analyze_all()` | list[AnalysisReport] | Analyze all files | `multi.analyze_all()` |
| `multi.time_series_analysis(interval)` | TimeSeriesResult | Cross-file time series | `multi.time_series_analysis(3600)` |

## Export Formats (LogEntries)

| Method | Purpose | Example |
|--------|---------|---------|
| `to_json(file)` | Export as JSON | `logs.to_json("out.json")` |
| `to_csv(file)` | Export as CSV | `logs.to_csv("out.csv")` |
| `to_html(file)` | Export as HTML | `logs.to_html("out.html")` |
| `to_markdown(file)` | Export as Markdown | `logs.to_markdown("out.md")` |
| `to_dataframe()` | pandas DataFrame | Export as DataFrame | `df = logs.to_dataframe()` |

## Helper Functions

| Function | Returns | Purpose | Example |
|----------|---------|---------|---------|
| `count_by(entries, field)` | dict | Count by field | `count_by(entries, "level")` |
| `group_by(entries, field)` | dict | Group by field | `group_by(entries, "action_type")` |
| `types(entries)` | set | Get unique types | `types(entries)` |

---

## CLI Tools (logxy-log-parser)

The parser library also provides CLI tools:

| Command | Purpose | Example |
|---------|---------|---------|
| `logxy-query <file>` | Query log file | `logxy-query app.log --level error` |
| `logxy-analyze <file>` | Analyze log file | `logxy-analyze app.log --output report.html` |
| `logxy-view <file>` | View with colored output | `logxy-view app.log` |
| `logxy-tree <file>` | Visualize task tree | `logxy-tree app.log` |

---

## Type Definitions

### LogXPyEntry

A single log entry (dataclass with slots):

| Field | Type | Purpose |
|-------|------|---------|
| `ts` | float | Unix timestamp |
| `tid` | str | Task ID (Sqid or UUID4) |
| `lvl` | list[int] | Hierarchy level |
| `mt` | str | Log level/type |
| `at` | str or None | Action type |
| `st` | str or None | started/succeeded/failed |
| `msg` | str | Message text |
| `dur` | float or None | Duration in seconds |

### ParseResult

| Field | Type | Purpose |
|-------|------|---------|
| `entries` | LogEntries | Parsed entries |
| `entry_count` | int | Total count |
| `source` | str | Source path |

### CheckResult

| Field | Type | Purpose |
|-------|------|---------|
| `is_valid` | bool | Validation status |
| `entry_count` | int | Total entries |
| `errors` | list[str] | Validation errors |
| `entries` | LogEntries | Parsed entries |

### AnalysisReport

| Method | Returns | Purpose |
|--------|---------|---------|
| `print_summary()` | None | Print to stdout |
| `to_dict()` | dict | Convert to dict |
| `to_json()` | str | Convert to JSON |

---

## Python Version Requirements

| Component | Min Version | Key Features Used |
|-----------|-------------|-------------------|
| logxpy | 3.12+ | Pattern matching, type aliases, dataclass slots, StrEnum |
| logxpy-cli-view | 3.9+ | Modern but widely compatible |
| logxy-log-parser | 3.12+ | Pattern matching, type aliases |

---

## Common Patterns

### Reading Logs

```python
from logxy_log_parser import parse_log

# Simple parse
entries = parse_log("app.log")

# Iterate
for entry in entries:
    print(entry.mt, entry.ts)

# Count by level
from logxy_log_parser import count_by
levels = count_by(entries, "mt")
print(levels)  # {'info': 100, 'error': 5, ...}
```

### Filtering Errors

```python
from logxy_log_parser import parse_log
from logxpy_cli_view import filter_by_action_status

entries = parse_log("app.log")
errors = filter_by_action_status(entries.entries, "failed")

for error in errors:
    print(error.get("action_type"), error.get("message"))
```

### Building Task Tree

```python
from logxy_log_parser import LogParser

parser = LogParser("app.log")
tree = parser.build_task_tree()

# Traverse tree
def print_tree(node, indent=0):
    print("  " * indent + node.action_type)
    for child in node.children:
        print_tree(child, indent + 1)

print_tree(tree.root)
```

### Real-time Monitoring

```python
from logxy_log_parser import LogFile

logfile = LogFile.open("app.log")

# Wait for specific event
try:
    entry = logfile.wait_for_message("Startup complete", timeout=30)
    print("Startup:", entry)
except TimeoutError:
    print("Startup timed out")

# Watch for errors
for entry in logfile.watch():
    if entry.mt == "error":
        print("Error:", entry.msg)
```

---

## Related Documentation

- [README.md](./README.md) - Main project documentation
- [CLAUDE.md](./CLAUDE.md) - Agent instructions
- [logxpy-api-reference.html](./logxpy-api-reference.html) - Complete API reference
- [DOC-X/cross-docs/cross-lib1.html](./DOC-X/cross-docs/cross-lib1.html) - CodeSite cross-reference
