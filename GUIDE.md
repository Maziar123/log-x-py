# LogXPy Complete Guide

Detailed guides for using log-x-py ecosystem.

---

## Table of Contents

1. [LoggerX Fluent API Guide](#loggerx-fluent-api-guide)
2. [Async Logging Guide](#async-logging-guide)
3. [Data Type Methods](#data-type-methods)
4. [Context Management](#context-management)
5. [Color and Style](#color-and-style)
6. [Decorators](#decorators)
7. [CLI Viewer Guide](#cli-viewer-guide)
8. [Log Parser Guide](#log-parser-guide)

---

## LoggerX Fluent API Guide

### Level Methods

All level methods return `self` for chaining:

```python
from logxpy import log

# Method chaining
log.debug("starting").info("processing").success("done")

# With fields
log.info("User action", user_id=123, action="login")
```

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

### Flexible __call__

```python
# Usage: Equivalent To
log("msg")           # log.info("msg")
log("title", data)  # log.info("title", value=data)
log(data)           # log.send("Data:Type", data)
```

---

## Async Logging Guide

### Configuration

```python
log.init(
    "app.log",
    async_en=True,      # Enable async (default)
    queue=10000,        # Queue size
    size=100,           # Batch size (0=disable)
    flush=0.1,          # Flush interval seconds
    deadline=None,      # Max message age
    policy="block",     # Backpressure policy
    writer_type="block",  # line | block | mmap
    writer_mode="trigger", # trigger | loop | manual
    tick=0.01,          # Poll interval for loop mode
)
```

### Writer Modes

Choose how the writer flushes logs:

**1. Trigger Mode (`trigger`) - DEFAULT**
```python
# Event-driven: Flushes on batch_size OR explicit events
# Best for: Maximum throughput (200K+ L/s)
log.init("app.log", writer_mode="trigger", size=100)
```

**2. Loop Mode (`loop`)**
```python
# Timer-based: Flushes periodically AND on batch_size
# Best for: Predictable flush timing
log.init("app.log", writer_mode="loop", flush=0.1)  # Every 100ms
```

**3. Manual Mode (`manual`)**
```python
# Explicit control: Only flushes when you call trigger()
# Best for: Full control over batching
log.init("app.log", writer_mode="manual")
log.info("Message 1")
log.info("Message 2")
log.flush()  # Explicit flush
```

### Writer Types

Choose the writer that best fits your use case:

**1. Line Buffered (`line`)**
```python
# Immediate flush per line - best for real-time monitoring
log.init("app.log", writer_type="line")
log.info("Appears immediately in file")
```

**2. Block Buffered (`block`) - DEFAULT**
```python
# 64KB buffer - best balance of performance and durability
log.init("app.log", writer_type="block", size=500)  # 275K+ L/s
```

**3. Memory Mapped (`mmap`)**
```python
# OS-managed memory mapping - maximum throughput
log.init("app.log", writer_type="mmap", size=1000)
```

### Writer Modes

Control when logs are flushed to disk:

**1. Trigger Mode (`trigger`) - DEFAULT**
```python
# Event-driven: wakes immediately on each message
log.init("app.log", writer_mode="trigger", size=100)
# Flushes when batch is full or flush interval expires
```

**2. Loop Mode (`loop`)**
```python
# Periodic poll: checks queue every tick seconds
log.init("app.log", writer_mode="loop", tick=0.1)  # 100ms
# Good for predictable flush intervals
```

**3. Manual Mode (`manual`)**
```python
# Full control: only flushes when you call trigger()
log.init("app.log", writer_mode="manual")
log.info("Message 1")
log.info("Message 2")
log.trigger()  # Manually flush
```

### Flush Techniques

**1. Timer-Based:**
```python
log.init("app.log", flush=0.1)  # Flush every 100ms
```

**2. Size-Based:**
```python
log.init("app.log", size=500)   # Flush every 500 messages
```

**3. On-Demand:**
```python
log.info("Critical")
log.flush()  # Force immediate flush (blocks until done)
```

**4. Sync Mode:**
```python
with log.sync_mode():
    log.critical("Blocks until written")
```

**5. Adaptive:**
```python
from logxpy import AdaptiveFlushConfig
config = AdaptiveFlushConfig(min_batch_size=10, max_batch_size=1000)
log._async_writer.enable_adaptive(config)
```

See [FLUSH_TECHNIQUES.md](docs/FLUSH_TECHNIQUES.md) for comprehensive details.

### Performance Optimization

**Achieving 275K+ logs/sec:**

```python
# Optimal configuration for maximum throughput
log.init(
    "app.log",
    writer_type="block",    # 64KB buffer (best balance)
    writer_mode="trigger",  # Event-driven (lowest latency)
    size=500,               # Batch 500 messages
    queue=10000,            # Large queue
)
```

**Performance by writer type:**

| Writer | Throughput | Best For |
|--------|------------|----------|
| `block` | ~275K L/s | General use (default) |
| `line` | ~260K L/s | Real-time monitoring |
| `mmap` | ~250K L/s | Batch processing |

**Optimization details:**
- **Fast JSON**: Uses f-string building instead of `json.dumps()` (3x faster)
- **Cached UUID**: Root task ID generated once per process (1.5x speedup)
- **Zero-copy**: Minimal allocations in hot path

**Benchmark your setup:**
```bash
python benchmarks/optimize_logging.py
python benchmarks/benchmark_before_after.py
```

### Backpressure Policies

| Policy | Behavior | Use Case |
|--------|----------|----------|
| `block` | Pause until written | No data loss |
| `replace` | Replace oldest | Fixed memory |
| `skip` | Skip new message | Overflow OK |
| `warn` | Skip + warning | Debug |

### Task ID Mode

Choose between Sqid (short, hierarchical) or UUID4 (standard, distributed):

**Sqid Mode (default)**
```python
# Short hierarchical IDs: "Xa.1", "Xa.1.1" (4-12 chars)
log.init("app.log", task_id_mode="sqid")
log.info("User action")  # tid: "Xa.1"
```
- ✅ 89% smaller than UUID (4-12 chars vs 36)
- ✅ Human-readable hierarchy in ID
- ✅ Best for single-process applications

**UUID Mode**
```python
# Standard UUID4: "59b00749-eb24-4c31-a2c8-aac523d7bfd9" (36 chars)
log.init("app.log", task_id_mode="uuid")
log.info("User action")  # tid: "59b00749-eb24-..."
```
- ✅ Globally unique across distributed systems
- ✅ Compatible with external tracing systems
- ✅ Best for microservices/multi-process apps

| Mode | Example | Length | Use Case |
|------|---------|--------|----------|
| `sqid` | `Xa.1`, `Xa.1.2` | 4-12 chars | Single-process (default) |
| `uuid` | `59b00749-eb24-...` | 36 chars | Distributed systems |

---

## Data Type Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `log.color(value, title)` | RGB/hex colors | `log.color((255, 0, 0), "Theme")` |
| `log.currency(amount, code)` | Currency | `log.currency("19.99", "USD")` |
| `log.datetime(dt, title)` | Datetime | `log.datetime(dt, "Start")` |
| `log.enum(enum_value, title)` | Enum | `log.enum(Status.ACTIVE)` |
| `log.ptr(obj, title)` | Object identity | `log.ptr(my_object)` |
| `log.variant(value, title)` | Any value with type | `log.variant(data, "Input")` |
| `log.sset(s, title)` | Set/frozenset | `log.sset({1, 2, 3}, "Tags")` |
| `log.df(df, title)` | DataFrame | `log.df(df, "Results")` |
| `log.tensor(data, title)` | Tensor | `log.tensor(tensor, "Weights")` |
| `log.json(data, title)` | JSON | `log.json({"key": "val"}, "Config")` |
| `log.img(data, title)` | Image | `log.img(image, "Screenshot")` |
| `log.plot(fig, title)` | Plot/Figure | `log.plot(fig, "Chart")` |
| `log.tree(data, title)` | Tree structure | `log.tree(data, "Hierarchy")` |
| `log.table(data, title)` | Table | `log.table(rows, "Users")` |
| `log.system_info()` | OS/platform info | `log.system_info()` |
| `log.memory_status()` | Memory stats | `log.memory_status()` |

---

## Context Management

### Scope Context Manager

```python
with log.scope(user_id=123, request_id="abc"):
    log.info("Processing")  # Includes context fields
```

### Fluent Context

```python
log.ctx(user_id=123).info("User logged in")
```

### Child Logger

```python
db_log = log.new("database")
db_log.info("Query")  # Shows "root.database"
```

---

## Color and Style

```python
# Set colors
log.set_foreground("cyan")
log.info("Cyan text")
log.reset_foreground()

# One-shot colored
log.colored(
    "╔══════════════╗\n"
    "║  IMPORTANT  ║\n"
    "╚══════════════╝",
    foreground="black",
    background="yellow"
)
```

**Available colors:** black, red, green, yellow, blue, magenta, cyan, white, light_gray, dark_gray, light_red, light_green, light_blue, light_yellow, light_magenta, light_cyan

---

## Decorators

```python
from logxpy import logged, timed, retry

@logged(level="DEBUG")
def my_func():
    pass

@timed("db.query")
def query_db():
    pass

@retry(attempts=5, delay=1.0)
def unreliable_call():
    pass
```

---

## CLI Viewer Guide

### Commands

```bash
# View logs
logxpy-view app.log

# Statistics
logxpy-view stats app.log

# Export
logxpy-view export app.log -f json -o out.json

# Live tail
logxpy-view tail app.log
```

### Filtering

```bash
# By status
logxpy-view --status failed app.log

# By action type
logxpy-view --action-type "db:*" app.log

# By duration
logxpy-view --min-duration 1.0 app.log

# JMESPath query
logxpy-view --select "level == \`error\`" app.log
```

### Output Options

```bash
# Format
logxpy-view --format tree app.log      # Tree (default)
logxpy-view --format oneline app.log   # One-line

# Theme
logxpy-view --theme dark app.log
logxpy-view --theme light app.log

# Other
logxpy-view --ascii app.log            # ASCII only
logxpy-view --no-colors app.log        # No colors
logxpy-view --no-emojis app.log        # No emojis
```

---

## Log Parser Guide

### One-Line API

```python
from logxy_log_parser import parse_log, analyze_log

# Parse
entries = parse_log("app.log")

# Analyze
report = analyze_log("app.log")
report.print_summary()
```

### Filtering

```python
from logxy_log_parser import LogParser, LogFilter

parser = LogParser("app.log")
logs = parser.parse()

result = (LogFilter(logs)
    .by_level("error", "warning")
    .by_time_range("2024-01-01", "2024-12-31")
    .slow_actions(1.0))
```

### Time Series Analysis

```python
from logxy_log_parser import LogParser, TimeSeriesAnalyzer

parser = LogParser("app.log")
logs = parser.parse()

analyzer = TimeSeriesAnalyzer(logs)

# Anomalies
for anomaly in analyzer.detect_anomalies():
    print(f"Anomaly: {anomaly}")

# Heatmap
heatmap = analyzer.activity_heatmap()
```

### CLI Commands

```bash
# Query
logxy-query app.log --level error --output errors.json

# Analyze
logxy-analyze app.log --slowest 20 --format html

# View
logxy-view app.log --level error

# Tree
logxy-tree app.log --task Xa.1
```

---

See [README.md](./README.md) for overview and [AGENTS.md](./AGENTS.md) for development details.
