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

- **⚡ High Performance** - **140,000+ logs/sec** (async), **5x faster** than sync
- **🆔 Sqid Task IDs** - 89% smaller than UUID4 (4-12 chars vs 36)
- **🔗 Fluent API** - Method chaining for clean code
- **📊 Structured** - JSON output with compact 1-2 char field names
- **🎨 Colored Output** - ANSI colors and emoji indicators
- **🔍 Powerful Filtering** - JMESPath, date ranges, action types
- **📈 Analytics** - Statistics, time series, anomaly detection
- **🔧 Minimal Dependencies** - Uses boltons and standard library

### Performance Benchmarks

| Mode | Throughput | Latency | vs Sync |
|------|------------|---------|---------|
| **Async** | **140,000+ logs/sec** | ~7 μs | **5x faster** |
| Sync | ~22,000 logs/sec | ~45 μs | baseline |

> **Note:** Your results may vary based on hardware and system load. Run `python benchmarks/bench_async_1000.py` to measure on your system.

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

**Async logging with configurable flush modes:**

```python
from logxpy import log

# Mode 1: Balanced (Timer OR Size)
log.init("app.log", size=100, flush=0.1)

# Mode 2: Time Only
log.init("app.log", size=0, flush="10ms")

# Mode 3: On-Demand Flush
log.init("app.log")
log.info("Critical")
log.flush()  # Force immediate

# Mode 4: Sync Mode
with log.sync_mode():
    log.critical("Blocks until written")
```

**Key Features:**
- **Sqid Task IDs** - `Xa.1`, `Xa.1.1` hierarchical IDs
- **Compact Fields** - `ts`, `tid`, `lvl`, `mt`, `msg`
- **Data Types** - `log.json()`, `log.df()`, `log.tensor()`, etc.
- **Context** - `log.scope()`, `log.ctx()`, `log.new()`
- **Colors** - `log.set_foreground()`, `log.colored()`

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
