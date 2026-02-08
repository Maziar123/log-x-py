# AGENTS.md

Guide for AI agents and assistants working on the log-x-py project.

## Project Overview

**log-x-py** is a structured logging ecosystem with three components:
1. **logxpy** - Zero-dependency structured logging library for Python 3.12+
2. **logxpy-cli-view** - Colored tree viewer for LogXPy logs
3. **logxy-log-parser** - Log parsing, analysis, and monitoring library

---

## Component 1: logxpy (Logging Library)

### Location
- `logxpy/logxpy/` - Core library source code

### Purpose
Modern structured logging that outputs causal chains of actions. Forked from Eliot, modernized with Python 3.12+ features.

### Key Features
- **Zero Dependencies** - Pure Python 3.12+
- **Type Safe** - Full type hints with modern syntax
- **Fast** - Dataclasses with slots (-40% memory), pattern matching (+10% speed)
- **Nested Actions** - Track hierarchical operations with context
- **Status Tracking** - Automatic start/success/failed tracking
- **Color Support** - Foreground/background colors for CLI viewer rendering

### Python Version
**3.12+ only** - Uses modern Python features:
- Type aliases (PEP 695): `type LogEntry = dict[str, Any]`
- Pattern matching (PEP 634): `match value: case int():`
- Dataclasses with slots (PEP 681): `@dataclass(slots=True)`
- StrEnum (PEP 663): Type-safe enums
- Walrus operator (PEP 572): `if uuid := entry.get("task_uuid")`

### Core API

| Function | Purpose | Example |
|----------|---------|---------|
| `Message.log(**fields)` | Log structured message | `Message.log(info="starting")` |
| `start_action(action_type, **fields)` | Begin hierarchical action | `with start_action("db_query"):` |
| `start_task(action_type, **fields)` | Create top-level action | `with start_task("process"):` |
| `log(message_type, **fields)` | Log in current action | `log(message_type="event")` |
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
| `log.exception(msg, **fields)` | ERROR + traceback | `except: log.exception("error")` |

### Data Type Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `log.color(value, title)` | Log RGB/hex colors | `log.color((255, 0, 0), "Theme")` |
| `log.currency(amount, code)` | Log currency | `log.currency("19.99", "USD")` |
| `log.datetime(dt, title)` | Log datetime | `log.datetime(dt, "StartTime")` |
| `log.enum(enum_value, title)` | Log enum | `log.enum(Status.ACTIVE)` |
| `log.variant(value, title)` | Log any value | `log.variant(data, "Input")` |
| `log.system_info()` | Log OS/platform info | `log.system_info()` |
| `log.memory_status()` | Log memory statistics | `log.memory_status()` |
| `log.stack_trace(limit)` | Log current call stack | `log.stack_trace(limit=10)` |
| `log.file_hex(path)` | Log file as hex dump | `log.file_hex("data.bin")` |
| `log.file_text(path)` | Log text file contents | `log.file_text("app.log")` |
| `log.memory_hex(data)` | Log bytes as hex dump | `log.memory_hex(buffer)` |
| `log.stream_hex(stream)` | Log binary stream as hex | `log.stream_hex(bio)` |
| `log.stream_text(stream)` | Log text stream contents | `log.stream_text(io)` |

### Color and Style Methods (for CLI Viewer)

These methods create colored blocks or lines when viewed with logxpy-cli-view:

| Method | Purpose | Example |
|--------|---------|---------|
| `log.set_foreground(color)` | Set foreground color | `log.set_foreground("cyan")` |
| `log.set_background(color)` | Set background color | `log.set_background("yellow")` |
| `log.reset_foreground()` | Reset foreground color | `log.reset_foreground()` |
| `log.reset_background()` | Reset background color | `log.reset_background()` |
| `log.colored(msg, fg, bg)` | One-shot colored message | `log.colored("Important!", "red", "yellow")` |

**Available colors**: black, red, green, yellow, blue, magenta, cyan, white, light_gray, dark_gray, light_red, light_green, light_blue, light_yellow, light_magenta, light_cyan

### Category System

| Class/Function | Purpose | Example |
|----------------|---------|---------|
| `CategorizedLogger` | Logger with category prefix | `cat_log = CategorizedLogger("database")` |
| `category_context(name)` | Context manager for category | `with category_context("db"):` |
| `Category(name)` | Global category manager | `Category("database")` |
| `log.with_category(name)` | Create categorized logger | `db_log = log.with_category("database")` |

### Decorators

| Decorator | Purpose | Example |
|-----------|---------|---------|
| `@logged(level, ...)` | Universal logging | `@logged(level="DEBUG")` |
| `@timed(metric)` | Timing-only | `@timed("db.query")` |
| `@retry(attempts, delay)` | Retry with backoff | `@retry(attempts=5)` |
| `@log_call(action_type)` | Log function calls | `@log_call(action_type="func")` |

### System Message Types

| Message Type | Purpose |
|--------------|---------|
| `logxpy:traceback` | Exception traceback |
| `loggerx:debug` | Debug messages |
| `loggerx:info` | Info messages |
| `loggerx:success` | Success messages |
| `loggerx:warning` | Warning messages |
| `loggerx:error` | Error messages |
| `loggerx:critical` | Critical messages |

### Color Fields for CLI Viewer

Log entries can include color hints that are rendered by logxpy-cli-view:

```python
# Set colors in log entry
{
    "logxpy:foreground": "cyan",
    "logxpy:background": "yellow",
    "message": "This renders with cyan on yellow"
}
```

### Module Structure

```
logxpy/logxpy/
├── __init__.py          # Main exports
├── _action.py           # Action context management
├── _message.py          # Message logging
├── loggerx.py           # LoggerX class with level methods
├── _output.py           # Output destinations
├── decorators.py        # Logging decorators
├── _validation.py       # Schema validation
├── category.py          # Category management with colors
├── data_types.py        # Data type helpers
├── file_stream.py       # File/stream operations
├── system_info.py       # System info logging
├── _traceback.py        # Exception handling
├── _types.py            # Core type definitions
├── _base.py             # Base utilities
├── _fmt.py              # Value formatting
├── _async.py            # Async support
└── _mask.py             # Field masking
```

---

## Component 2: logxpy-cli-view (Tree Viewer)

### Location
- `logxpy_cli_view/src/logxpy_cli_view/` - Viewer source code

### Purpose
Render LogXPy logs as beautiful colored ASCII trees with filtering, export, and monitoring capabilities.

### Key Features
- **ANSI Colors** - Color-coded values (numbers: cyan, booleans: magenta, errors: red)
- **Emoji Icons** - Visual indicators (💾 database, 🔌 API, 🔐 auth)
- **Tree Structure** - Unicode box-drawing characters (├── └── │)
- **Color Block Rendering** - Supports `logxpy:foreground` and `logxpy:background` fields
- **Filtering** - By status, action type, duration, keyword, JMESPath
- **Export** - JSON, CSV, HTML, logfmt
- **Live Monitoring** - Tail mode with real-time updates
- **Theme Support** - Dark and light themes

### Python Version
**3.9+** - Uses modern but widely-compatible Python features.

### CLI Commands

| Command | Description |
|---------|-------------|
| `logxpy-view <file>` | View log as tree |
| `--failed` | Show only failed actions |
| `--succeeded` | Show only succeeded actions |
| `--filter "pattern"` | Filter by action name |
| `--export json/csv/html/logfmt` | Export format |
| `--tail` | Live log monitoring |
| `--stats` | Show statistics |
| `--theme dark/light` | Color theme |

### Core API

| Function | Purpose | Example |
|----------|---------|---------|
| `tasks_from_iterable(lines)` | Parse log lines | `tasks = tasks_from_iterable(f)` |
| `render_tasks(tasks)` | Render as tree | `print(render_tasks(tasks))` |
| `filter_by_action_status(tasks, status)` | Filter by status | `filter_by_action_status(tasks, "failed")` |
| `filter_by_action_type(tasks, pattern)` | Filter by action | `filter_by_action_type(tasks, "db_*")` |
| `filter_by_duration(tasks, min_seconds)` | Filter by duration | `filter_by_duration(tasks, 1.0)` |
| `filter_by_keyword(tasks, keyword)` | Search values | `filter_by_keyword(tasks, "error")` |
| `export_json(tasks, file)` | Export JSON | `export_json(tasks, "out.json")` |
| `export_csv(tasks, file)` | Export CSV | `export_csv(tasks, "out.csv")` |
| `export_html(tasks, file)` | Export HTML | `export_html(tasks, "out.html")` |

### Color System

**Supported Colors**:
- Foreground: red, green, blue, yellow, magenta, cyan, white, black, light_gray, dark_gray, light_red, light_green, light_blue, light_yellow, light_magenta, light_cyan
- Background: Same colors available
- Styles: bold, dim, underline, blink, reverse, hidden

**Level-based Colors**:
- DEBUG: Gray
- INFO: White
- SUCCESS: Bright Green
- NOTE: Yellow
- WARNING: Bright Yellow
- ERROR: Red
- CRITICAL: Bright Red with background

### Module Structure

```
logxpy_cli_view/src/logxpy_cli_view/
├── __init__.py          # Main exports
├── _parse.py            # Log parsing
├── _render.py           # Tree rendering
├── _color.py            # Color handling
├── _theme.py            # Theme management
├── _export.py           # Export functions
├── filter.py            # Filter functions
├── _stats.py            # Statistics
├── _tail.py             # Live monitoring
├── _patterns.py         # Pattern extraction
├── format.py            # Formatting utilities
├── _cli.py              # CLI interface
├── _errors.py           # Error classes
├── _compat.py           # Compatibility helpers
└── _util.py             # Utility functions
```

---

## Component 3: logxy-log-parser (Log Parser & Analyzer)

### Location
- `logxy-log-parser/logxy_log_parser/` - Parser source code

### Purpose
Python library for parsing, analyzing, and querying LogXPy log files with rich export formats and real-time monitoring.

### Key Features
- **Simple API** - One-line parsing: `entries = parse_log("app.log")`
- **Powerful Filtering** - By level, time, action type, field values
- **Analysis** - Performance stats, error summaries, task trees
- **Export** - JSON, CSV, HTML, Markdown, DataFrame
- **Real-time Monitoring** - Watch logs as they grow
- **Validation** - Quick log file checking

### Python Version
**3.12+** - Modern Python with optional pandas/rich support.

### Simple API (One-Liners)

| Function | Purpose | Example |
|----------|---------|---------|
| `parse_log(path)` | Parse log file | `entries = parse_log("app.log")` |
| `parse_line(line)` | Parse single line | `entry = parse_line(json_str)` |
| `check_log(path)` | Parse + validate | `result = check_log("app.log")` |
| `analyze_log(path)` | Full analysis | `report = analyze_log("app.log")` |

### Core Classes

| Class | Purpose | Example |
|-------|---------|---------|
| `LogFile` | File handle + real-time monitoring | `logfile = LogFile.open("app.log")` |
| `LogParser` | Parse log files | `parser = LogParser("app.log")` |
| `LogEntries` | Collection with filtering/export | `logs = parser.parse()` |
| `LogFilter` | Chainable filters | `errors = LogFilter(logs).by_level("error")` |
| `LogAnalyzer` | Performance/error analysis | `analyzer = LogAnalyzer(logs)` |
| `TaskTree` | Hierarchical task tree | `tree = parser.build_task_tree()` |
| `TaskNode` | Node in task tree | `node = tree.root` |

### LogFile API (Real-time Monitoring)

| Method | Purpose | Example |
|--------|---------|---------|
| `LogFile.open(path)` | Open and validate | `logfile = LogFile.open("app.log")` |
| `logfile.entry_count` | Get entry count (fast) | `count = logfile.entry_count` |
| `logfile.contains_error()` | Check for errors | `if logfile.contains_error():` |
| `logfile.watch()` | Iterate new entries | `for entry in logfile.watch():` |
| `logfile.wait_for_message(text, timeout)` | Wait for message | `entry = logfile.wait_for_message("ready", 30)` |
| `logfile.wait_for_error(timeout)` | Wait for error | `error = logfile.wait_for_error(60)` |

### Filter Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `by_level(*levels)` | Filter by log level | `by_level("error", "warning")` |
| `by_message(pattern)` | Filter by message text | `by_message("database")` |
| `by_time_range(start, end)` | Filter by time range | `by_time_range("2024-01-01", "2024-12-31")` |
| `by_task_uuid(*uuids)` | Filter by task UUID | `by_task_uuid("abc-123")` |
| `by_action_type(*types)` | Filter by action type | `by_action_type("db_*")` |
| `by_field(field, value)` | Filter by field value | `by_field("user_id", 123)` |
| `by_duration(min, max)` | Filter by duration | `by_duration(min=1.0)` |
| `with_traceback()` | Entries with tracebacks | `with_traceback()` |
| `failed_actions()` | Failed actions only | `failed_actions()` |
| `slow_actions(threshold)` | Slow actions only | `slow_actions(5.0)` |

### Module Structure

```
logxy-log-parser/logxy_log_parser/
├── __init__.py          # Main exports
├── simple.py            # Simple one-line API
├── core.py              # LogParser, LogEntry
├── filter.py            # LogFilter, LogEntries
├── analyzer.py          # LogAnalyzer
├── monitor.py           # LogFile (real-time)
├── tree.py              # TaskTree, TaskNode
├── types.py             # Type definitions
├── export.py            # Export functions
└── utils.py             # Helper functions
```

---

## Development Environment

- **OS**: Arch Linux
- **Python**: 3.12+ (managed via `uv`)
- **Package Manager**: `uv` (preferred)

### Working with Python

```bash
# Run with uv
uv run python script.py

# Or activate venv first
source .venv/bin/activate
python script.py
```

---

## Architecture

### Design Patterns Used

1. **Dataclasses with slots** - 40% memory reduction
2. **StrEnum** - Type-safe enums for colors/emojis
3. **Pattern matching** - Smart value routing
4. **Type aliases** - `type LogEntry = dict[str, Any]`
5. **Frozen configs** - Immutable settings

---

## Coding Conventions

### Naming Conventions
- **Modules**: `snake_case` (e.g., `view_tree.py`, `_message.py`)
- **Classes**: `PascalCase` (e.g., `Colors`, `EmojiIcon`)
- **Functions/methods**: `snake_case` (e.g., `get_icon`, `colorize`)
- **Constants**: `UPPER_SNAKE_CASE`
- **Private modules**: `_leading_underscore` (e.g., `_action.py`)

### Code Style
- **Type hints**: Required for all public functions
- **Docstrings**: Google style for modules/classes
- **Line length**: Not strictly enforced, aim for readability
- **Imports**: Standard library first, then local imports

---

## Working with the Codebase

### Running Examples

```bash
cd examples-log-view

# Generate log file
python example_01_basic.py

# View log with tree viewer
logxpy-view example_01_basic.log

# Run all examples
./run_all.sh
```

### Viewer Options

```bash
# Full features (colors + emoji + Unicode)
logxpy-view file.log

# ASCII mode (plain text)
logxpy-view file.log --ascii

# No colors (for piping/files)
logxpy-view file.log --no-colors

# No emojis
logxpy-view file.log --no-emojis

# Limit nesting depth
logxpy-view file.log --depth-limit 3
```

---

## Key Concepts

### Log Entry Structure

```python
{
    "task_uuid": "abc123-...",  # Groups related entries
    "timestamp": 14:30:00,      # HH:MM:SS format
    "action_type": "http:request",  # Determines emoji
    "task_level": [1],           # Hierarchical level (array format)
    "action_status": "succeeded", # started, succeeded, failed
    "duration_ns": 145000000,    # Nanoseconds
    # ... additional key-value pairs
}
```

### Task Level Format

```
[1]              # Root level, 1st action
[2, 1]           # Child of 2nd action, 1st sub-action
[3, 2, 1]        # 3 levels deep
[3, 3, 3, 3, 3, 3, 3]  # 7 levels deep (maximum tested)
```

### Emoji Auto-Detection

Based on `action_type` keywords:
- `database`, `db:`, `query` → 💾
- `http`, `api`, `request` → 🔌
- `auth`, `login` → 🔐
- `payment`, `charge` → 💳
- `server` → 🖥️
- `pipeline`, `etl` → 🔄
- `error`, `fail` → 🔥
- Default → ⚡

### Color Coding

| Type | Color | ANSI Code |
|------|-------|-----------|
| Numbers | Cyan | `\033[36m` |
| Booleans | Magenta | `\033[35m` |
| Keys | Bright Blue | `\033[94m` |
| Error strings | Bright Red | `\033[91m` |
| Success strings | Bright Green | `\033[92m` |
| Regular strings | White | `\033[37m` |
| Timestamps | Dim Gray | `\033[90m` |
| Task UUIDs | Bright Magenta | `\033[95m` |

---

## Common Tasks

### Adding a New Example

1. Create `example_XX_name.py` in `examples-log-view/`
2. Import from logxpy: `from logxpy import start_action, Message, to_file`
3. Set output: `to_file(open("example_XX_name.log", "w"))`
4. Write logging code
5. Update `README.md` example table

### Adding a New Color

1. Add to `Color` StrEnum in `view_tree.py`
2. Update `_format_value()` pattern matching
3. Update color documentation in README

### Adding a New Emoji

1. Add to `EmojiIcon` StrEnum in `view_tree.py`
2. Add pattern in `get_icon()` method
3. Update emoji table in README

---

## Performance Notes

- **Slots**: -40% memory vs regular dataclasses
- **Pattern matching**: +10% speed vs if/elif chains
- **Frozen dataclasses**: Allow optimizations
- **Zero string concatenation**: Use f-strings only

---

## Documentation

- [README.md](README.md) - Main project documentation
- [logxpy-api-reference.html](logxpy-api-reference.html) - Complete API reference
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project overview
- [DOC-X/cross-docs/cross-lib1.html](DOC-X/cross-docs/cross-lib1.html) - CodeSite cross-reference

---

## Contributing

1. **Zero dependencies** - Don't add external packages unless necessary
2. **Python 3.12+ only** - Use modern features
3. **Type hints** - Required for new code
4. **Tests** - Add examples for new features
5. **Documentation** - Update relevant docs

---

## Project Goals

- Beautiful, readable log visualization
- Zero dependencies for core logging library
- Modern Python 3.12+ features
- Type-safe throughout
- Fast and memory efficient
- Clear, maintainable code
