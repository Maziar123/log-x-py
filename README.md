# log-x-py

Modern structured logging ecosystem with three components: logging library, tree viewer, and log parser.

![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

> **📁 Docs**: [API Reference](./logxpy-api-reference.html) | [Flush Guide](./FLUSH_TECHNIQUES.md) | [Complete Guide](./GUIDE.md) | [Agents](./AGENTS.md)

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Components](#components)
  - [logxpy](#component-1-logxpy---logging-library)
  - [logxpy-cli-view](#component-2-logxpy-cli-view---tree-viewer)
  - [logxy-log-parser](#component-3-logxy-log-parser---log-analyzer)
- [Documentation](#documentation)
- [Installation](#installation)

---

## Features

- **⚡ High Performance** - **275,000+ logs/sec** (async), **12x faster** than sync, **2.75x faster** than before optimization
- **🆔 Configurable Task IDs** - Sqid (4-12 chars, default) or UUID4 (36 chars, distributed)
- **🔗 Fluent API** - Method chaining for clean code
- **📊 Structured** - JSON output with compact 1-2 char field names
- **🎨 Colored Output** - ANSI colors and emoji indicators
- **🔍 Powerful Filtering** - JMESPath, date ranges, action types
- **📈 Analytics** - Statistics, time series, anomaly detection
- **🔧 Minimal Dependencies** - Uses boltons and standard library

### Performance Benchmarks

| Mode | Throughput | Latency | vs Sync | Notes |
|------|------------|---------|---------|-------|
| **Async (optimized)** | **275,000+ logs/sec** | ~3.6 μs | **12x faster** | Fast JSON + choose-L2 writer |
| Sync | ~22,000 logs/sec | ~45 μs | baseline | Direct file writes |

**Optimization highlights:**
- **Fast JSON serialization**: Direct f-string building (3x faster than `json.dumps()`)
- **Cached task UUID**: Root UUID generated once per process (1.5x speedup)
- **Choose-L2 writer**: Three optimized writer types (line/block/mmap)

**Configuration for best performance:**
```python
# Optimal settings for 275K+ L/s
log.init("app.log", writer_type="block", size=500, writer_mode="trigger")
```

**Writer Types:**
| Type | Buffer | Best For | Performance |
|------|--------|----------|-------------|
| `line` | 1 line | Real-time | ~260K L/s |
| `block` | 64KB | Balanced (default) | ~275K L/s |
| `mmap` | OS-managed | Max throughput | ~250K L/s |

**Writer Modes:**
| Mode | Behavior | Use Case |
|------|----------|----------|
| `trigger` | Event-driven | Default, lowest latency |
| `loop` | Periodic poll | Predictable flush intervals |
| `manual` | Explicit `trigger()` | Full control |

> **Note:** Your results may vary based on hardware, batch size, and message complexity. See [benchmarks/](./benchmarks/) for detailed benchmarks.

---

## Quick Start

```bash
pip install logxpy logxpy-cli-view
```

```python
from logxpy import log

# Auto-generate log filename
log.init()

# Simple logging
log.info("Hello, World!")
log.success("Operation completed")

# Structured with fields
log.info("User action", user_id=123, action="login")

# Method chaining
log.debug("starting").info("processing").success("done")
```

View logs:
```bash
logxpy-view script.log
```

---

## Components

### Component 1: logxpy - Logging Library

**Async logging with configurable writer types and modes:**

```python
from logxpy import log

# Fastest configuration (275K+ L/s)
log.init("app.log", writer_type="block", writer_mode="trigger", size=500)

# Real-time logging (immediate flush)
log.init("app.log", writer_type="line", writer_mode="trigger")

# Periodic sync (good for batch processing)
log.init("app.log", writer_mode="loop", tick=0.1)

# Manual control
log.init("app.log", writer_mode="manual")
log.info("Message 1")
log.info("Message 2")
log.trigger()  # Flush manually

# Force immediate flush
log.flush()  # Blocks until all pending logs written

# Sync mode for critical sections
with log.sync_mode():
    log.critical("Blocks until written")

# Task ID mode selection
log.init("app.log", task_id_mode="sqid")   # Short Sqid (default, 4-12 chars)
log.init("app.log", task_id_mode="uuid")   # UUID4 (36 chars, distributed)
```

**Key Features:**
- **⚡ High Performance** - 275K+ logs/sec with optimized writer
- **🆔 Sqid Task IDs** - `Xa.1`, `Xa.1.1` hierarchical IDs
- **📊 Compact Fields** - `ts`, `tid`, `lvl`, `mt`, `msg`
- **📦 Data Types** - `log.json()`, `log.df()`, `log.tensor()`, etc.
- **🔧 Context** - `log.scope()`, `log.ctx()`, `log.new()`
- **🎨 Colors** - `log.set_foreground()`, `log.colored()`

See [GUIDE.md](./GUIDE.md#loggerx-fluent-api-guide) for detailed API.

---

### Component 2: logxpy-cli-view - Tree Viewer

**Render logs as colored ASCII trees:**

```bash
# View with full colors
logxpy-view app.log

# Filter by status
logxpy-view --status failed app.log

# Filter by action type
logxpy-view --action-type "db:*" app.log

# JMESPath query
logxpy-view --select "level == \`error\`" app.log

# Export
logxpy-view export app.log -f json -o out.json

# Live tail
logxpy-view tail app.log
```

**Output:**
```
Xa.1
├── 🔌 http:request/1 ⇒ ▶️ started 14:30:00
│   ├── method: POST
│   └── path: /api/users
├── 💾 database:query/2/1 ⇒ ▶️ started 14:30:00
│   └── 💾 database:result/2/2 ⇒ ✔️ succeeded 14:30:01
│       └── rows: 10
└── 🔌 http:request/3 ⇒ ✔️ succeeded 14:30:01
```

See [GUIDE.md](./GUIDE.md#cli-viewer-guide) for complete CLI reference.

---

### Component 3: logxy-log-parser - Log Analyzer

**Parse, filter, and analyze logs:**

```python
from logxy_log_parser import parse_log, analyze_log, LogFilter

# One-line parsing
entries = parse_log("app.log")

# Analysis report
report = analyze_log("app.log")
report.print_summary()

# Chain filters
result = (LogFilter(entries)
    .by_level("error")
    .by_time_range("2024-01-01", "2024-12-31")
    .slow_actions(1.0))
```

**CLI Tools:**
```bash
# Query
logxy-query app.log --level error --output errors.json

# Analyze
logxy-analyze app.log --slowest 20 --format html

# View
logxy-view app.log --level error
```

See [GUIDE.md](./GUIDE.md#log-parser-guide) for detailed API.

---

## Documentation

| Document | Description |
|----------|-------------|
| [GUIDE.md](./GUIDE.md) | **Complete usage guide** with all APIs and examples |
| [FLUSH_TECHNIQUES.md](./FLUSH_TECHNIQUES.md) | Async logging flush mechanisms deep dive |
| [AGENTS.md](./AGENTS.md) | Developer guide for AI agents |
| [logxpy-api-reference.html](./logxpy-api-reference.html) | Full HTML API reference |

---

## Installation

```bash
# Just the library
pip install logxpy

# Library + Viewer (recommended)
pip install logxpy logxpy-cli-view

# All components
pip install logxpy logxpy-cli-view logxy-log-parser
```

---

## Project Structure

```
log-x-py/
├── logxpy/              # Logging library
├── logxpy_cli_view/     # CLI tree viewer  
├── logxy_log_parser/    # Log parser & analyzer
├── examples/            # Examples & tutorials
├── tests/               # Test suite
├── GUIDE.md             # Complete guide
├── FLUSH_TECHNIQUES.md  # Flush mechanisms
└── AGENTS.md            # Developer guide
```

---

## Quick Reference

| Task | Command |
|------|---------|
| View logs | `logxpy-view app.log` |
| Filter errors | `logxpy-view --status failed app.log` |
| Export JSON | `logxpy-view export -f json -o out.json app.log` |
| Query logs | `logxy-query app.log --level error` |
| Analyze | `logxy-analyze app.log --slowest 20` |

---

**Python 3.12+ | Sqid Task IDs | Fluent API | Async Logging**
