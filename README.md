# log-x-py

Modern structured logging ecosystem with three components: logging library, tree viewer, and log parser.

> **📁 Complete API Reference**: [logxpy-api-reference.html](./logxpy-api-reference.html) - Full API docs with examples
>
> **📘 CodeSite Migration Guide**: [DOC-X/cross-docs/cross-lib1.html](./DOC-X/cross-docs/cross-lib1.html) - CodeSite vs logxpy cross-reference

---

## Component 1: logxpy - Logging Library

**Zero-dependency structured logging for Python 3.12+**

![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)
![Zero Dependencies](https://img.shields.io/badge/dependencies-0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

### Features
- **Type Safe** - Full type hints with Python 3.12+ syntax
- **Fast** - Dataclasses with slots (-40% memory), pattern matching (+10% speed)
- **Zero Dependencies** - Pure Python 3.12+
- **Nested Actions** - Track hierarchical operations with context
- **Status Tracking** - Automatic start/success/failed tracking
- **Color Support** - Foreground/background colors for CLI viewer rendering

### Quick Start
```bash
pip install logxpy
```

```python
from logxpy import start_action, Message, to_file

to_file(open("app.log", "w"))

with start_action(action_type="http:request", method="POST", path="/api/users"):
    with start_action(action_type="database:query", table="users"):
        Message.log(message_type="database:result", rows=10)
```

### Core API

> 📋 **Full API Reference**: See [logxpy-api-reference.html](./logxpy-api-reference.html) for complete documentation with all methods, parameters, and examples.

| Function | Purpose | Example |
|----------|---------|---------|
| `Message.log(**fields)` | Log structured message | `Message.log(info="starting", count=5)` |
| `start_action(action_type, **fields)` | Begin hierarchical action | `with start_action("db_query", table="users"):` |
| `start_task(action_type, **fields)` | Create top-level action | `with start_task("process"):` |
| `log(message_type, **fields)` | Log in current action | `log(message_type="event", x=1)` |
| `to_file(output_file)` | Set log output file | `to_file(open("app.log", "w"))` |
| `current_action()` | Get current action context | `action = current_action()` |
| `write_traceback()` | Log exception traceback | `except: write_traceback()` |

### LoggerX Level Methods

| Method | Level | Example |
|--------|-------|---------|
| `log.debug(msg, **fields)` | DEBUG | `log.debug("starting", count=5)` |
| `log.info(msg, **fields)` | INFO | `log.info("user login", user="alice")` |
| `log.success(msg, **fields)` | SUCCESS | `log.success("completed", total=100)` |
| `log.note(msg, **fields)` | NOTE | `log.note("checkpoint", step=3)` |
| `log.warning(msg, **fields)` | WARNING | `log.warning("slow query", ms=5000)` |
| `log.error(msg, **fields)` | ERROR | `log.error("failed", code=500)` |
| `log.critical(msg, **fields)` | CRITICAL | `log.critical("system down")` |
| `log.checkpoint(msg, **fields)` | CHECKPOINT | `log.checkpoint("step1")` |
| `log.exception(msg, **fields)` | ERROR + traceback | `except: log.exception("error")` |

### LoggerX Data Type Methods (Clean API)

| Method | Purpose | Example |
|--------|---------|---------|
| `log.color(value, title)` | Log RGB/hex colors | `log.color((255, 0, 0), "Theme")` |
| `log.currency(amount, code)` | Log currency with precision | `log.currency("19.99", "USD")` |
| `log.datetime(dt, title)` | Log datetime in multiple formats | `log.datetime(dt, "StartTime")` |
| `log.enum(enum_value, title)` | Log enum with name/value | `log.enum(Status.ACTIVE)` |
| `log.ptr(obj, title)` | Log object identity | `log.ptr(my_object)` |
| `log.variant(value, title)` | Log any value with type info | `log.variant(data, "Input")` |
| `log.sset(s, title)` | Log set/frozenset | `log.sset({1, 2, 3}, "Tags")` |
| `log.system_info()` | Log OS/platform info | `log.system_info()` |
| `log.memory_status()` | Log memory statistics | `log.memory_status()` |
| `log.memory_hex(data)` | Log bytes as hex dump | `log.memory_hex(buffer)` |
| `log.stack_trace(limit)` | Log current call stack | `log.stack_trace(limit=10)` |
| `log.file_hex(path)` | Log file as hex dump | `log.file_hex("data.bin")` |
| `log.file_text(path)` | Log text file contents | `log.file_text("app.log")` |
| `log.stream_hex(stream)` | Log binary stream as hex | `log.stream_hex(bio)` |
| `log.stream_text(stream)` | Log text stream contents | `log.stream_text(io)` |

### Color and Style Methods (for CLI Viewer)

These methods create **colored blocks or lines** when viewed with logxpy-cli-view:

| Method | Purpose | Example |
|--------|---------|---------|
| `log.set_foreground(color)` | Set foreground color | `log.set_foreground("cyan")` |
| `log.set_background(color)` | Set background color | `log.set_background("yellow")` |
| `log.reset_foreground()` | Reset foreground color | `log.reset_foreground()` |
| `log.reset_background()` | Reset background color | `log.reset_background()` |
| `log.colored(msg, fg, bg)` | One-shot colored message | `log.colored("Important!", "red", "yellow")` |

**Available colors**: black, red, green, yellow, blue, magenta, cyan, white, light_gray, dark_gray, light_red, light_green, light_blue, light_yellow, light_magenta, light_cyan

**Example: Creating colored blocks**
```python
from logxpy import log

# Set colors for subsequent messages
log.set_foreground("cyan")
log.info("This renders with cyan text")
log.reset_foreground()

# One-shot colored message for highlighted blocks
log.colored(
    "╔════════════════════════════════════╗\n"
    "║  ⚠️  IMPORTANT HIGHLIGHTED BLOCK  ║\n"
    "╚════════════════════════════════════╝",
    foreground="black",
    background="yellow"
)
```

### log() Callable (Flexible Shortcut)

| Usage | Equivalent To | Example |
|-------|---------------|---------|
| `log("msg")` | `log.info("msg")` | `log("Starting")` |
| `log("title", data)` | `log.send("title", data)` | `log("User", {"id": 1})` |
| `log(data)` | `log.send(auto_title, data)` | `log({"key": "val"})` |

### Decorators

| Decorator | Purpose | Example |
|-----------|---------|---------|
| `@logged(level, ...)` | Universal logging decorator | `@logged(level="DEBUG")` |
| `@timed(metric)` | Timing-only decorator | `@timed("db.query")` |
| `@retry(attempts, delay)` | Retry with backoff | `@retry(attempts=5)` |
| `@log_call(action_type)` | Log function calls | `@log_call(action_type="func")` |

### Category System

| Class/Function | Purpose | Example |
|----------------|---------|---------|
| `CategorizedLogger` | Logger with category prefix | `cat_log = CategorizedLogger("database")` |
| `category_context(name)` | Context manager for category | `with category_context("db"):` |
| `Category(name)` | Global category manager | `Category("database")` |
| `log.with_category(name)` | Create categorized logger | `db_log = log.with_category("database")` |

### System Message Types

| Message Type | Purpose |
|--------------|---------|
| `logxpy:traceback` | Exception traceback logging |
| `loggerx:debug` | Debug level messages |
| `loggerx:info` | Info level messages |
| `loggerx:success` | Success level messages |
| `loggerx:warning` | Warning level messages |
| `loggerx:error` | Error level messages |
| `loggerx:critical` | Critical level messages |

---

## Component 2: logxpy-cli-view - Colored Tree Viewer

**Render LogXPy logs as a beautiful colored ASCII tree**

![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

### Features
- **ANSI Colors** - Color-coded values (numbers: cyan, booleans: magenta, errors: red)
- **Emoji Icons** - Visual indicators for action types (💾 database, 🔌 API, 🔐 auth)
- **Tree Structure** - Unicode box-drawing characters (├── └── │)
- **Color Block Rendering** - Supports `logxpy:foreground` and `logxpy:background` fields
- **Flexible** - ASCII mode, depth limiting, color/emoji toggles

### Quick Start
```bash
# View logs with full colors
logxpy-view app.log

# Or use the standalone script
python examples-log-view/view_tree.py app.log
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `logxpy-view <file>` | View log as tree |
| `logxpy-view <file> --failed` | Show only failed actions |
| `logxpy-view <file> --filter "db_*"` | Filter by action name |
| `logxpy-view <file> --export json` | Export as JSON |
| `logxpy-view <file> --export csv` | Export as CSV |
| `logxpy-view <file> --export html` | Export as HTML |
| `logxpy-view <file> --tail` | Live log monitoring |
| `logxpy-view <file> --stats` | Show statistics |

### Filter Functions

| Function | Purpose |
|----------|---------|
| `filter_by_action_status(tasks, status)` | Filter by status (succeeded/failed) |
| `filter_by_action_type(tasks, pattern)` | Filter by action name pattern |
| `filter_by_duration(tasks, min_seconds)` | Filter by duration range |
| `filter_by_keyword(tasks, keyword)` | Search in values |
| `filter_by_jmespath(tasks, query)` | JMESPath query filter |

### Export Functions

| Function | Purpose |
|----------|---------|
| `export_json(tasks, file)` | Export as JSON |
| `export_csv(tasks, file)` | Export as CSV |
| `export_html(tasks, file)` | Export as HTML |
| `export_logfmt(tasks, file)` | Export as logfmt |

---

## Component 3: logxy-log-parser - Log Parser & Analyzer

**Python library for parsing, analyzing, and querying LogXPy log files**

![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)

### Features
- **Simple API** - One-line parsing: `entries = parse_log("app.log")`
- **Powerful Filtering** - By level, time, action type, field values
- **Analysis** - Performance stats, error summaries, task trees
- **Export** - JSON, CSV, HTML, Markdown, DataFrame
- **Real-time Monitoring** - Watch logs as they grow

### Quick Start
```bash
pip install logxy-log-parser
```

```python
from logxy_log_parser import parse_log, check_log, analyze_log

# One-line parsing
entries = parse_log("app.log")

# Parse + validate
result = check_log("app.log")
print(f"Valid: {result.is_valid}, Entries: {result.entry_count}")

# Full analysis
report = analyze_log("app.log")
report.print_summary()
```

### Core Classes

| Class | Purpose |
|-------|---------|
| `LogFile` | File handle + real-time monitoring |
| `LogParser` | Parse log files |
| `LogEntries` | Collection with filtering/export |
| `LogFilter` | Chainable filters |
| `LogAnalyzer` | Performance/error analysis |
| `TaskTree` | Hierarchical task tree |

### LogFile API (Real-time Monitoring)

| Method | Purpose |
|--------|---------|
| `LogFile.open(path)` | Open and validate |
| `logfile.entry_count` | Get entry count (fast) |
| `logfile.contains_error()` | Check for errors |
| `logfile.watch()` | Iterate new entries |
| `logfile.wait_for_message(text, timeout)` | Wait for message |
| `logfile.wait_for_error(timeout)` | Wait for error |

### Filter Methods

| Method | Purpose |
|--------|---------|
| `by_level(*levels)` | Filter by log level |
| `by_message(pattern)` | Filter by message text |
| `by_time_range(start, end)` | Filter by time range |
| `by_task_uuid(*uuids)` | Filter by task UUID |
| `by_action_type(*types)` | Filter by action type |
| `by_field(field, value)` | Filter by field value |
| `by_duration(min, max)` | Filter by duration |
| `with_traceback()` | Entries with tracebacks |
| `failed_actions()` | Failed actions only |
| `slow_actions(threshold)` | Slow actions only |

---

## Installation

Install any or all components:

```bash
# Just the logging library (zero dependencies)
pip install logxpy

# Just the tree viewer
pip install logxpy-cli-view

# Just the log parser
pip install logxy-log-parser

# All three (recommended)
pip install logxpy logxpy-cli-view logxy-log-parser
```

Or install from source:

```bash
# Library
cd logxpy && pip install -e .

# Viewer
cd logxpy_cli_view && pip install -e .

# Parser
cd logxy-log-parser && pip install -e .
```

---

## Live Output Example

**Terminal Output (with actual ANSI colors):**

```
56ffc3bf-08f7-4f71-8065-b91db2d54e1c
├── 🔌 http:request/1 ⇒ ▶️ started 14:30:00
│   ├── method: POST
│   └── path: /api/users
├── 🔐 auth:verify/2/1 ⇒ ▶️ started 14:30:00
│   ├── user_id: 123
│   └── valid: True
├── 💾 database:query/3/1 ⇒ ▶️ started 14:30:00
│   ├── table: users
│   └── 💾 database:result/3/2 14:30:01
│   ├── rows: 10
│   └── duration_ms: 45
└── 🔌 http:request/4 ⇒ ✔️ succeeded 14:30:01
```

**Color Legend:**
- **Cyan** = Numbers
- **Magenta** = Booleans, UUIDs
- **Bright Blue** = Started status, Field keys
- **Bright Green** = Succeeded status
- **Bright Red** = Failed status

---

## Quick Start (Try It Now)

```bash
cd examples-log-view
python example_01_basic.py
logxpy-view example_01_basic.log
```

## Complete Cheat Sheet

| Feature | Syntax/Example | Description |
|---------|----------------|-------------|
| **Commands** | | |
| Basic view | `logxpy-view file.log` | Full color + emoji + Unicode |
| ASCII mode | `logxpy-view file.log --ascii` | Plain text, no Unicode/emoji |
| No colors | `logxpy-view file.log --no-colors` | Remove ANSI colors |
| No emojis | `logxpy-view file.log --no-emojis` | Remove emoji icons |
| Depth limit | `logxpy-view file.log --depth-limit 3` | Max nesting levels |
| Help | `logxpy-view --help` | Show all options |

---

## Project Structure

```
log-x-py/
├── logxpy/                          # Component 1: Core logging library
│   ├── logxpy/                      # Main package
│   ├── setup.py                     # Installation config
│   └── examples/                    # Library usage examples
│
├── logxpy_cli_view/                 # Component 2: CLI tree viewer
│   ├── src/logxpy_cli_view/         # Main package
│   ├── pyproject.toml               # Installation config
│   └── tests/                       # Test suite
│
├── logxy-log-parser/                # Component 3: Log parser & analyzer
│   ├── logxy_log_parser/            # Main package
│   ├── pyproject.toml               # Installation config
│   └── examples/                    # Usage examples
│
├── examples-log-view/               # Standalone examples (demo both packages)
│   ├── view_tree.py                # Simple tree viewer script
│   ├── example_01_basic.py         # Basic logging
│   ├── example_02_actions.py       # Nested actions
│   ├── example_03_errors.py        # Error handling
│   ├── example_04_api_server.py    # API simulation
│   ├── example_05_data_pipeline.py # ETL pipeline
│   ├── example_06_deep_nesting.py  # 7-level nesting
│   ├── example_07_all_data_types.py # All data types
│   └── run_all.sh                  # Run all examples
│
├── tutorials/                       # Detailed tutorials
├── README.md                        # This file
├── AGENTS.md                        # AI agent guide
├── AI_CONTEXT.md                    # Complete API reference
└── PROJECT_SUMMARY.md               # Project overview
```

---

## Statistics

| Component | Lines | Dependencies | Python |
|-----------|-------|--------------|--------|
| **logxpy** (library) | ~2000 | 0 | 3.12+ |
| **logxpy-cli-view** (viewer) | ~500 | 4 (jmespath, iso8601, colored, toolz) | 3.9+ |
| **logxy-log-parser** (parser) | ~800 | 0 (optional: pandas, rich) | 3.12+ |

---

## Use Cases

**Development**: Debug nested operations, trace request flows, visualize errors
**Testing**: Verify log formats, test data types, validate structures
**Production**: Monitor performance, track errors, audit trails
**Documentation**: Generate examples, show API flows, training materials

---

## License

MIT License

---

## Credits & Attribution

This project is a fork and modernization of two excellent libraries:

### logxpy (Logging Library)
**Forked from [Eliot](https://github.com/itamarst/eliot)** by Itamar Turner-Trauring
- Original: Structured logging for complex & distributed systems
- Changes: Modernized for Python 3.12+, renamed to logxpy, enhanced API

### logxpy-cli-view (Tree Viewer)
**Forked from [eliottree](https://github.com/jonathanj/eliottree)** by Jonathan Jacobs
- Original: Render Eliot logs as ASCII trees
- Changes: Modernized codebase, renamed to logxpy-cli-view, added new features

### License
Both original projects are licensed under Apache 2.0. This fork maintains compatibility with the original Eliot log format while providing a modernized API and toolset.

---

**Python 3.12+ | Zero Dependencies | Type Safe**
