# AGENTS.md

Guide for AI agents and assistants working on the log-x-py project.

## Project Overview

**log-x-py** is a structured logging ecosystem with three components:
1. **logxpy** - Structured logging library with minimal dependencies (boltons)
2. **logxpy-cli-view** - Colored tree viewer for LogXPy logs
3. **logxy-log-parser** - Log parsing, analysis, and monitoring library

---

## Component 1: logxpy (Logging Library)

### Location
- `logxpy/logxpy/` - Core library source code

### Purpose
Modern structured logging that outputs causal chains of actions. Forked from Eliot, modernized with Python 3.12+ features.

### Key Features
- **Minimal Dependencies** - Uses boltons (pure Python utility library)
- **Type Safe** - Full type hints with modern syntax
- **Fast** - Dataclasses with slots (-40% memory), pattern matching (+10% speed)
- **Fluent API** - All methods return self for method chaining
- **Nested Actions** - Track hierarchical operations with context
- **Status Tracking** - Automatic start/success/failed tracking
- **Color Support** - Foreground/background colors for CLI viewer rendering
- **Sqid Task IDs** - 89% smaller IDs (4 chars vs 36), hierarchical, human-readable

### Python Version
**3.12+ only** - Uses modern Python features:
- Type aliases (PEP 695): `type LogEntry = dict[str, Any]`
- Pattern matching (PEP 634): `match value: case int():`
- Dataclasses with slots (PEP 681): `@dataclass(slots=True)`
- StrEnum (PEP 663): Type-safe enums
- Walrus operator (PEP 572): `if tid := entry.get("task_uuid")`
- **Sqid Task IDs** - Hierarchical short IDs (4-12 chars vs 36-char UUID4)

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

### LoggerX - Fluent API

LoggerX provides a **fluent API** where all methods return `self` for method chaining:

```python
from logxpy import log

# Method chaining
log.debug("starting").info("processing").success("done")

# All level methods return self
log.set_foreground("cyan").info("Cyan text").reset_foreground()
```

### LoggerX Level Methods

All level methods return `self` for chaining:

| Method | Level | Example |
|--------|-------|---------|
| `log.debug(msg, **fields)` | DEBUG | `log.debug("starting", count=5)` |
| `log.info(msg, **fields)` | INFO | `log.info("user login", user="alice")` |
| `log.success(msg, **fields)` | SUCCESS | `log.success("completed", total=100)` |
| `log.note(msg, **fields)` | NOTE | `log.note("checkpoint", step=3)` |
| `log.warning(msg, **fields)` | WARNING | `log.warning("slow query", ms=5000)` |
| `log.error(msg, **fields)` | ERROR | `log.error("failed", code=500)` |
| `log.critical(msg, **fields)` | CRITICAL | `log.critical("system down")` |
| `log.checkpoint(msg, **fields)` | CHECKPOINT (📍 prefix) | `log.checkpoint("step1")` |
| `log.exception(msg, **fields)` | ERROR + traceback | `except: log.exception("error")` |

### LoggerX Flexible __call__

The `log()` callable provides flexible shortcuts:

| Usage | Equivalent To | Example |
|-------|---------------|---------|
| `log("msg")` | `log.info("msg")` | `log("Starting")` |
| `log("title", data)` | `log.info("title", value=data)` | `log("User", {"id": 1})` |
| `log(data)` | `log.send(auto_title, data)` | `log({"key": "val"})` |

### LoggerX Data Type Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `log.color(value, title)` | Log RGB/hex colors | `log.color((255, 0, 0), "Theme")` |
| `log.currency(amount, code)` | Log currency with precision | `log.currency("19.99", "USD")` |
| `log.datetime(dt, title)` | Log datetime in multiple formats | `log.datetime(dt, "StartTime")` |
| `log.enum(enum_value, title)` | Log enum with name/value | `log.enum(Status.ACTIVE)` |
| `log.ptr(obj, title)` | Log object identity | `log.ptr(my_object)` |
| `log.variant(value, title)` | Log any value with type info | `log.variant(data, "Input")` |
| `log.sset(s, title)` | Log set/frozenset | `log.sset({1, 2, 3}, "Tags")` |
| `log.df(data, title)` | Log DataFrame | `log.df(df, "Results")` |
| `log.tensor(data, title)` | Log Tensor | `log.tensor(tensor, "Weights")` |
| `log.json(data, title)` | Log JSON with formatted output | `log.json({"key": "val"}, "Config")` |
| `log.img(data, title)` | Log Image | `log.img(image, "Screenshot")` |
| `log.plot(fig, title)` | Log Plot/Figure | `log.plot(fig, "Chart")` |
| `log.tree(data, title)` | Log tree structure | `log.tree(data, "Hierarchy")` |
| `log.table(data, title)` | Log table (list of dicts) | `log.table(rows, "Users")` |
| `log.system_info()` | Log OS/platform info | `log.system_info()` |
| `log.memory_status()` | Log memory statistics | `log.memory_status()` |
| `log.memory_hex(data)` | Log bytes as hex dump | `log.memory_hex(buffer)` |
| `log.stack_trace(limit)` | Log current call stack | `log.stack_trace(limit=10)` |
| `log.file_hex(path)` | Log file as hex dump | `log.file_hex("data.bin")` |
| `log.file_text(path)` | Log text file contents | `log.file_text("app.log")` |
| `log.stream_hex(stream)` | Log binary stream as hex | `log.stream_hex(bio)` |
| `log.stream_text(stream)` | Log text stream contents | `log.stream_text(io)` |

### LoggerX Context Management

| Method | Purpose | Example |
|--------|---------|---------|
| `log.scope(**ctx)` | Nested scope context manager | `with log.scope(user_id=123):` |
| `log.ctx(**ctx)` | Add context (returns new logger) | `log.ctx(user_id=123).info("...")` |
| `log.new(name)` | Create child logger | `child_log = log.new("database")` |

**Example:**
```python
from logxpy import log

# Context manager for nested scope
with log.scope(user_id=123, request_id="abc"):
    log.info("Processing request")  # Includes user_id and request_id

# Fluent context addition
log.ctx(user_id=123).info("User logged in")

# Create child logger
db_log = log.new("database")
db_log.info("Query executed")  # Shows "root.database" as logger name
```

### LoggerX Initialization

```python
from logxpy import log

# Auto-generate log filename from caller script (e.g., script.py -> script.log)
log.init()

# Specify file
log.init("app.log")

# With level and mode
log.init("app.log", level="INFO", mode="w")

# Full configuration
log.configure(
    level="DEBUG",
    destinations=["console", "file://app.log"],
    format="rich",
    mask_fields=["password", "token"]
)
```

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

### OpenTelemetry Integration

```python
from logxpy import log

# OpenTelemetry span context manager
with log.span("database_query", table="users", sql="SELECT *"):
    # Your code here
    results = db.query("SELECT * FROM users")
```

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
| `@logged(level, ...)` | Universal logging decorator | `@logged(level="DEBUG")` |
| `@timed(metric)` | Timing-only decorator | `@timed("db.query")` |
| `@retry(attempts, delay)` | Retry with backoff | `@retry(attempts=5)` |
| `@generator` | Generator logging | `@generator` |
| `@aiterator` | Async iterator logging | `@aiterator` |
| `@trace` | Tracing decorator | `@trace` |
| `@log_call(action_type)` | Log function calls | `@log_call(action_type="func")` |

### System Message Types

| Message Type | Purpose |
|--------------|---------|
| `logxpy:traceback` | Exception traceback |
| `loggerx:debug` | Debug messages (or just `debug`) |
| `loggerx:info` | Info messages (or just `info`) |
| `loggerx:success` | Success messages (or just `success`) |
| `loggerx:warning` | Warning messages (or just `warning`) |
| `loggerx:error` | Error messages (or just `error`) |
| `loggerx:critical` | Critical messages |

### Color Fields for CLI Viewer

Log entries can include color hints that are rendered by logxpy-cli-view:

```python
# Set colors in log entry
{
    "fg": "cyan",              # Foreground color (compact)
    "bg": "yellow",            # Background color (compact)
    "logxpy:foreground": "cyan",     # Legacy form (also supported)
    "logxpy:background": "yellow",   # Legacy form (also supported)
    "message": "This renders with cyan on yellow"
}
```

### Module Structure

```
logxpy/logxpy/
├── __init__.py          # Main exports
├── _action.py           # Action context management
├── _message.py          # Message logging
├── _sqid.py             # Hierarchical task ID generation (Sqid)
├── loggerx.py           # LoggerX class with fluent API
├── _output.py           # Output destinations
├── _cache.py            # Caching utilities
├── decorators.py        # Logging decorators
├── _validation.py       # Schema validation
├── category.py          # Category management with colors
├── data_types.py        # Data type helpers
├── file_stream.py       # File/stream operations
├── system_info.py       # System info logging
├── _traceback.py        # Exception handling
├── _types.py            # Core type definitions
├── _base.py             # Base utilities (uuid, sqid, now)
├── _fmt.py              # Value formatting
├── _async.py            # Async support
└── _mask.py             # Field masking
```

---

## Component 2: logxpy-cli-view (Tree Viewer)

### Location
- `logxpy_cli_view/src/logxpy_cli_view/` - Viewer source code

### Purpose
Render LogXPy logs as beautiful colored ASCII trees with filtering, export, statistics, and monitoring capabilities.

### Key Features
- **ANSI Colors** - Color-coded values (numbers: cyan, booleans: magenta, errors: red)
- **Emoji Icons** - Visual indicators (💾 database, 🔌 API, 🔐 auth)
- **Tree Structure** - Unicode box-drawing characters (├── └── │)
- **Color Block Rendering** - Supports `fg`/`bg` fields
- **Powerful Filtering** - By status, action type, duration, keyword, JMESPath, date range
- **Statistics** - Success/failure rates, duration stats, action type counts
- **Export** - JSON, CSV, HTML, logfmt
- **Live Monitoring** - Tail mode with real-time updates and dashboard
- **Pattern Extraction** - Extract emails, IPs, URLs from logs
- **Theme Support** - Auto, dark, and light themes

### Python Version
**3.9+** - Uses modern but widely-compatible Python features.

### CLI Commands

| Command | Description |
|---------|-------------|
| `logxpy-view render <file>` | View log as tree (default) |
| `logxpy-view stats <file>` | Show statistics |
| `logxpy-view export <file>` | Export to format |
| `logxpy-view tail <file>` | Live log monitoring |

### CLI Options

#### Filtering Options
| Option | Description |
|--------|-------------|
| `--task-uuid <uuid>` | Filter by task UUID (Sqid) |
| `--select <jmespath>` | JMESPath query (multiple allowed) |
| `--start <date>` | Filter after ISO8601 date |
| `--end <date>` | Filter before ISO8601 date |
| `--status <status>` | Filter by action status (started/succeeded/failed) |
| `--action-type <pattern>` | Filter by action type (supports wildcards) |
| `--action-type-regex` | Treat action-type as regex pattern |
| `--min-duration <seconds>` | Filter by minimum duration |
| `--max-duration <seconds>` | Filter by maximum duration |
| `--has-field <name>` | Filter by field existence |
| `--keyword <text>` | Search in all field values |
| `--min-level <n>` | Filter by minimum task level (depth) |
| `--max-level <n>` | Filter by maximum task level (depth) |

#### Output Options
| Option | Description |
|--------|-------------|
| `--format tree\|oneline` | Output format (default: tree) |
| `--theme auto\|dark\|light` | Color theme (default: auto) |
| `--field-limit <n>` | Limit field value length |
| `--no-line-numbers` | Hide line numbers |
| `--no-color-tree` | Disable tree line coloring |
| `--ascii` | Use ASCII characters instead of Unicode |
| `--no-emojis` | Remove emoji icons |
| `--no-colors` | Disable all colors |

### Core API

#### Core Functions
| Function | Purpose | Example |
|----------|---------|---------|
| `tasks_from_iterable(lines)` | Parse log lines | `tasks = tasks_from_iterable(f)` |
| `render_tasks(tasks)` | Render as tree | `print(render_tasks(tasks))` |
| `render_oneline(tasks)` | Render one-line format | `print(render_oneline(tasks))` |

#### Filter Functions
| Function | Purpose | Example |
|----------|---------|---------|
| `filter_by_action_status(tasks, status)` | Filter by status | `filter_by_action_status(tasks, "failed")` |
| `filter_by_action_type(tasks, pattern)` | Filter by action name | `filter_by_action_type(tasks, "db_*")` |
| `filter_by_duration(tasks, min, max)` | Filter by duration | `filter_by_duration(tasks, 1.0)` |
| `filter_by_keyword(tasks, keyword)` | Search values | `filter_by_keyword(tasks, "error")` |
| `filter_by_jmespath(tasks, query)` | JMESPath query | `filter_by_jmespath(tasks, "[?level=='error']")` |
| `filter_by_uuid(tasks, *uuids)` | Filter by task UUID | `filter_by_uuid(tasks, "Xa.1")` |
| `filter_by_start_date(tasks, date)` | Filter by start date | `filter_by_start_date(tasks, "2024-01-01")` |
| `filter_by_end_date(tasks, date)` | Filter by end date | `filter_by_end_date(tasks, "2024-12-31")` |
| `filter_by_field_exists(tasks, field)` | Filter by field existence | `filter_by_field_exists(tasks, "error")` |

#### Export Functions
| Function | Purpose | Example |
|----------|---------|---------|
| `export_json(tasks, file)` | Export as JSON | `export_json(tasks, "out.json")` |
| `export_csv(tasks, file)` | Export as CSV | `export_csv(tasks, "out.csv")` |
| `export_html(tasks, file)` | Export as HTML | `export_html(tasks, "out.html")` |
| `export_logfmt(tasks, file)` | Export as logfmt | `export_logfmt(tasks, "out.log")` |

#### Statistics Functions
| Function | Purpose | Example |
|----------|---------|---------|
| `calculate_statistics(tasks)` | Calculate statistics | `stats = calculate_statistics(tasks)` |
| `print_statistics(stats)` | Print formatted stats | `print_statistics(stats)` |
| `create_time_series(tasks)` | Create time series data | `ts = create_time_series(tasks)` |

#### Pattern Extraction
| Function | Purpose | Example |
|----------|---------|---------|
| `extract_emails(entries)` | Extract email addresses | `emails = extract_emails(entries)` |
| `extract_ips(entries)` | Extract IP addresses | `ips = extract_ips(entries)` |
| `extract_urls(entries)` | Extract URLs | `urls = extract_urls(entries)` |
| `extract_uuids(entries)` | Extract UUIDs | `uuids = extract_uuids(entries)` |

#### Live Monitoring
| Function | Purpose | Example |
|----------|---------|---------|
| `tail_logs(path)` | Tail log file | `tail_logs("app.log")` |
| `LiveDashboard()` | Live dashboard class | `LiveDashboard().run()` |
| `watch_and_aggregate(path)` | Watch and aggregate | `watch_and_aggregate("app.log")` |

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
Python library for parsing, analyzing, and querying LogXPy log files with rich export formats, real-time monitoring, indexing, and time-series analysis.

### Key Features
- **Simple One-Line API** - Parse entire files in one call
- **Indexing System** - Fast lookups for large log files
- **Powerful Filtering** - By level, time, action type, field values
- **Time Series Analysis** - Anomaly detection, heatmaps, burst detection
- **Aggregation** - Multi-file analysis and aggregation
- **Analysis** - Performance stats, error summaries, task trees
- **Export** - JSON, CSV, HTML, Markdown, DataFrame
- **Real-time Monitoring** - Watch logs as they grow
- **CLI Tools** - Query, analyze, view, and visualize logs

### Python Version
**3.12+** - Modern Python with optional pandas/rich support.

### Simple API (One-Liners)

| Function | Purpose | Returns |
|----------|---------|---------|
| `parse_log(source)` | Parse log file | `ParseResult` |
| `parse_line(line)` | Parse single line | `LogXPyEntry` or `None` |
| `check_log(source)` | Parse + validate | `CheckResult` |
| `analyze_log(source)` | Full analysis | `AnalysisReport` |

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
| `LogIndex` | Fast lookups via indexing | `index = LogIndex.build("app.log")` |
| `IndexedLogParser` | Parser with index support | `parser = IndexedLogParser("app.log")` |
| `TimeSeriesAnalyzer` | Time-series analysis | `analyzer = TimeSeriesAnalyzer(logs)` |
| `LogAggregator` | Multi-file aggregation | `agg = LogAggregator(files)` |
| `MultiFileAnalyzer` | Cross-file analysis | `multi = MultiFileAnalyzer(files)` |

### LogFile API (Real-time Monitoring)

| Method | Purpose | Example |
|--------|---------|---------|
| `LogFile.open(path)` | Open and validate | `logfile = LogFile.open("app.log")` |
| `logfile.entry_count` | Get entry count (fast) | `count = logfile.entry_count` |
| `logfile.contains_error()` | Check for errors | `if logfile.contains_error():` |
| `logfile.watch()` | Iterate new entries | `for entry in logfile.watch():` |
| `logfile.wait_for_message(text, timeout)` | Wait for message | `entry = logfile.wait_for_message("ready", 30)` |
| `logfile.wait_for_error(timeout)` | Wait for error | `error = logfile.wait_for_error(60)` |
| `logfile.contains(**criteria)` | Check contains | `logfile.contains(level="error")` |
| `logfile.find_first(**criteria)` | Find first match | `first = logfile.find_first(level="error")` |
| `logfile.find_all(**criteria)` | Find all matches | `all_errors = logfile.find_all(level="error")` |
| `logfile.tail(n)` | Get last N entries | `last = logfile.tail(10)` |

### LogFilter Methods

All filter methods return `LogEntries` for chaining:

| Method | Purpose | Example |
|--------|---------|---------|
| `by_level(*levels)` | Filter by log level | `.by_level("error", "warning")` |
| `by_message(pattern)` | Filter by message text | `.by_message("database")` |
| `by_time_range(start, end)` | Filter by time range | `.by_time_range("2024-01-01", "2024-12-31")` |
| `by_task_uuid(*uuids)` | Filter by task ID (Sqid) | `.by_task_uuid("Xa.1")` |
| `by_action_type(*types)` | Filter by action type | `.by_action_type("db:*")` |
| `by_field(field, value)` | Filter by field value | `.by_field("user_id", 123)` |
| `by_duration(min, max)` | Filter by duration | `.by_duration(min=1.0)` |
| `by_nesting_level(min, max)` | Filter by depth | `.by_nesting_level(1, 3)` |
| `with_traceback()` | Entries with tracebacks | `.with_traceback()` |
| `failed_actions()` | Failed actions only | `.failed_actions()` |
| `succeeded_actions()` | Succeeded actions only | `.succeeded_actions()` |
| `slow_actions(threshold)` | Slow actions only | `.slow_actions(5.0)` |
| `fast_actions(threshold)` | Fast actions only | `.fast_actions(0.001)` |

### LogAnalyzer Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `slowest_actions(n)` | Get slowest actions | `list[ActionStat]` |
| `fastest_actions(n)` | Get fastest actions | `list[ActionStat]` |
| `duration_by_action()` | Duration by action type | `dict[str, DurationStats]` |
| `error_summary()` | Error analysis summary | `ErrorSummary` |
| `error_patterns()` | Find error patterns | `list[ErrorPattern]` |
| `failure_rate_by_action()` | Failure rate per action | `dict[str, float]` |
| `deepest_nesting()` | Maximum nesting depth | `int` |
| `orphans()` | Unmatched entries | `LogEntries` |
| `timeline(interval)` | Timeline data | `Timeline` |
| `peak_periods(n)` | Busiest time periods | `list[TimePeriod]` |
| `generate_report(format)` | Generate report | `str` (html/text/json) |

### Indexing System

For fast lookups in large log files:

| Class/Method | Purpose | Example |
|--------------|---------|---------|
| `LogIndex.build(path)` | Build index | `index = LogIndex.build("app.log")` |
| `index.find_by_task(uuid)` | Find by task UUID | `index.find_by_task("Xa.1")` |
| `index.find_by_level(level)` | Find by level | `index.find_by_level("error")` |
| `index.find_by_time_range(start, end)` | Find by time range | `index.find_by_time_range(start, end)` |
| `IndexedLogParser(path)` | Indexed parser | `parser = IndexedLogParser("app.log")` |
| `parser.query(**criteria)` | Query with criteria | `parser.query(task_uuid="Xa.1")` |

### Time Series Analysis

| Method | Purpose | Returns |
|--------|---------|---------|
| `bucket_by_interval(seconds)` | Bucket by time interval | `list[TimeBucket]` |
| `detect_anomalies(window, threshold)` | Detect anomalies | `list[Anomaly]` |
| `error_rate_t(interval)` | Error rate over time | `list[tuple]` |
| `level_distribution(interval)` | Level distribution | `dict` |
| `activity_heatmap(hour_granularity)` | Activity heatmap | `dict` |
| `burst_detection(threshold, min_interval)` | Detect bursts | `list[Burst]` |

### Aggregation & Multi-File Analysis

| Class/Method | Purpose | Example |
|--------------|---------|---------|
| `LogAggregator(files)` | Aggregate multiple files | `agg = LogAggregator(["f1.log", "f2.log"])` |
| `aggregator.aggregate()` | Aggregate all files | `result = agg.aggregate()` |
| `MultiFileAnalyzer(files)` | Analyze multiple files | `multi = MultiFileAnalyzer(files)` |
| `multi.analyze_all()` | Analyze all files | `multi.analyze_all()` |
| `multi.time_series_analysis(interval)` | Time series across files | `multi.time_series_analysis(3600)` |

### CLI Commands

| Command | Description |
|---------|-------------|
| `logxy-query <file>` | Query log file with filters |
| `logxy-analyze <file>` | Analyze log file and generate report |
| `logxy-view <file>` | View log file with colored output |
| `logxy-tree <file>` | Visualize task tree from log file |

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
├── index.py             # LogIndex, IndexedLogParser
├── aggregation.py       # LogAggregator, TimeSeriesAnalyzer
├── types.py             # Type definitions
├── export.py            # Export functions
├── cli.py               # CLI commands
├── config.py            # Configuration management
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
logxpy-view file.log --max-level 3
```

---

## Key Concepts

### Log Entry Structure (Compact Field Names)

LogXPy uses **1-2 character field names** to minimize log size:

```python
{
    "ts": 1770562483.38,      # Timestamp (was: timestamp)
    "tid": "Xa.1",            # Task ID - Sqid format (was: task_uuid)
    "lvl": [1],               # Task level hierarchy (was: task_level)
    "mt": "info",             # Message type (was: message_type)
    "at": "http:request",     # Action type - determines emoji (was: action_type)
    "st": "succeeded",        # Action status (was: action_status)
    "dur": 0.145,             # Duration in seconds (was: duration_ns)
    "msg": "User logged in",  # Message text (was: message)
    # ... additional user-defined key-value pairs
}
```

**Field Name Mapping:**

| Compact | Legacy | Meaning |
|---------|--------|---------|
| `ts` | `timestamp` | Unix timestamp (seconds) |
| `tid` | `task_uuid` | Task ID (Sqid format) |
| `lvl` | `task_level` | Hierarchy level array |
| `mt` | `message_type` | Log level: `info`, `success`, `error`, etc. |
| `at` | `action_type` | Action type (for emoji): `db:query`, `http:request` |
| `st` | `action_status` | started/succeeded/failed |
| `dur` | `duration` | Duration in seconds |
| `msg` | `message` | Log message text (the actual message) |

**Compact Field Constants:**
```python
from logxpy import TS, TID, LVL, MT, AT, ST, DUR, MSG

# Use compact names
entry[TS] = time.time()
entry[TID] = sqid()
entry[MT] = "info"
```

**Example Log Entry:**
```json
{"ts":1770563890.7861168,"tid":"gD.1","lvl":[1],"mt":"info","msg":"Hello, World!"}
```

### Task ID Format (Sqid)

**Sqids** replace UUID4 with ultra-short hierarchical IDs:

| Format | Example | Length | Use Case |
|--------|---------|--------|----------|
| Root | `"Xa.1"` | 4 chars | Top-level task |
| Child | `"Xa.1.1"` | 6 chars | Nested action |
| Deep | `"Xa.1.1.2"` | 8 chars | 3 levels deep |
| UUID4 (legacy) | `"59b00749-eb24-..."` | 36 chars | Distributed mode |

**Benefits:**
- **89% smaller** than UUID4 (4-12 chars vs 36)
- **Human readable** - Shows hierarchy in ID
- **Process-isolated** - PID prefix prevents cross-process collisions
- **Collision safe** - 238K entries per process before wrap

**Format:** `PID_PREFIX.COUNTER[.CHILD_INDEX...]`
- `Xa` = 2-char PID prefix (base62)
- `1` = Entry counter (base62, sequential)
- `1`, `2` = Child indices for nested actions

**Environment variable for distributed mode:**
```bash
LOGXPY_DISTRIBUTED=1  # Forces UUID4 for distributed tracing
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
| Task IDs (`tid`) | Bright Magenta | `\033[95m` |

---

## Common Tasks

### Adding a New Example

1. Create `example_XX_name.py` in `examples-log-view/`
2. Import from logxpy: `from logxpy import start_action, Message, to_file`
3. Set output: `to_file(open("example_XX_name.log", "w"))`
4. Write logging code
5. Update `README.md` example table

### Working with Sqid Task IDs

**Generate Sqid manually:**
```python
from logxpy import sqid, SqidGenerator

# Simple generation
id = sqid()  # "Xa.1"

# With generator for hierarchy
gen = SqidGenerator()
root = gen.generate()       # "Xa.1"
child = gen.child(root, 1)  # "Xa.1.1"
```

**Force UUID4 for distributed systems:**
```python
import os
os.environ["LOGXPY_DISTRIBUTED"] = "1"  # Use UUID4

# Or via uuid()
from logxpy._base import uuid
task_id = uuid(use_sqid=False)  # UUID4 format
```

**Parse Sqid hierarchy:**
```python
from logxpy._sqid import SqidGenerator

gen = SqidGenerator()
sqid = "Xa.1.2.1"

level = sqid.count(".")  # 3 = depth
parent = sqid.rsplit(".", 1)[0]  # "Xa.1.2"
```

**Using compact field names:**
```python
from logxpy import TS, TID, LVL, MT, AT, ST, DUR, MSG

# Instead of:
entry["timestamp"] = time.time()
entry["task_uuid"] = sqid()
entry["message_type"] = "info"

# Use compact names:
entry[TS] = time.time()      # "ts"
entry[TID] = sqid()          # "tid"
entry[MT] = "info"           # "mt"
```

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
- [PLAN_DOCUMENTATION_UPDATE.md](PLAN_DOCUMENTATION_UPDATE.md) - Documentation update plan

---

## Included Dependencies

### Included Dependency: boltons (v25.0.0)

> 250+ pure-Python utilities — no dependencies · Battle-tested · 26 modules

**Key Modules:**

| Module | Purpose | Key Functions/Classes |
|--------|---------|----------------------|
| `cacheutils` | Caching | `LRU`, `LRI`, `@cached`, `cachedproperty`, `ThresholdCounter` |
| `debugutils` | Debugging | `pdb_on_exception`, `wrap_trace`, `pdb_on_signal` |
| `dictutils` | Mapping types | `OrderedMultiDict`, `OneToOne`, `ManyToMany`, `FrozenDict` |
| `ecoutils` | Environment | `get_profile()`, `get_python_info()` |
| `fileutils` | Filesystem | `atomic_save`, `mkdir_p`, `iter_find_files`, `FilePerms` |
| `formatutils` | Format strings | `get_format_args`, `DeferredValue` |
| `funcutils` | Functions | `wraps`, `FunctionBuilder`, `InstancePartial`, `noop` |
| `gcutils` | Garbage collect | `GCToggler`, `get_all()` |
| `ioutils` | I/O helpers | `SpooledBytesIO`, `MultiFileReader` |
| `iterutils` | Iteration | `remap` ★, `research`, `chunked`, `backoff`, `bucketize` |
| `jsonutils` | JSON | `JSONLIterator`, `reverse_iter_lines` |
| `listutils` | Lists | `BarrelList`, `SplayList` |
| `mathutils` | Math | `clamp`, `ceil`, `floor`, `Bits` |
| `pathutils` | Paths | `augpath`, `expandpath`, `shrinkuser` |
| `queueutils` | Priority queues | `HeapPriorityQueue`, `PriorityQueue` |
| `setutils` | Sets | `IndexedSet`, `complement` |
| `socketutils` | Sockets | `BufferedSocket`, `NetstringSocket` |
| `statsutils` | Statistics | `Stats`, `describe`, `format_histogram` |

📖 **Full Reference**: See [DOC/boltons-ref.md](DOC/boltons-ref.md) for complete API documentation.

## Contributing

1. **Python 3.12+ only** - Use modern features
2. **Type hints** - Required for new code
3. **Tests** - Add examples for new features
4. **Documentation** - Update relevant docs

---

## Project Goals

- Beautiful, readable log visualization
- Minimal dependencies (boltons)
- Modern Python 3.12+ features
- Type-safe throughout
- Fast and memory efficient
- Clear, maintainable code
