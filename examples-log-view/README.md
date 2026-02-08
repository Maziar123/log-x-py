# LogXPy Examples

This directory contains example projects demonstrating various LogXPy features.

## Examples Overview

| Example | Directory | Description |
|---------|-----------|-------------|
| **Basic Examples** | `complete-example-01/` | 13 examples from basic logging to advanced features |
| **Minimal Demo** | `compact-color-demo/` | **Ultra-compact** demo with symlink (105 lines total) |
| **Color Features** | `comp-with-parser/` | Comprehensive example with color rendering |
| **Nested Colored** | `3level-nested-colored/` | 3-level nested colored example |

## 📁 Directories

### compact-color-demo/

**Two ultra-compact demos** demonstrating different approaches:

#### Option A: `compact_color_demo.py` - Deep Tree + @logged + stack_trace()
```bash
cd compact-color-demo
./run_compact.sh
```

**Key concept:**
- **ONE yellow block** (Application Start)
- **ONE cyan block** (Critical Section)
- **@logged decorator** - 3 decorated functions
- **log.stack_trace()** - Error handling
- **4-level deep nesting** - functions inside functions

```
🟡 [1] ═══════════════  ← YELLOW BLOCK
   [2] app:main → started
    ├── [23] decorator:demo → started
   [24]   Testing @logged decorator
    ├── [25] __main__.process_item → started  ← @logged
    ├── [28] __main__.validate_email → started  ← @logged
    ├── [30] __main__.calculate_total → started  ← @logged
🟦 [35] ═══════════════  ← CYAN BLOCK
    ...
    ├── [60] error:test → started
   [66]   Stack Trace                   ← stack_trace()
```

| File | Lines | Purpose |
|------|-------|---------|
| `compact_color_demo.py` | ~120 | Deep nesting + @logged + stack_trace() |
| `compact_parser.py` | ~75 | Show function tree with depth |
| `run_compact.sh` | ~40 | Run pipeline |

**Output:** 74 entries, 4-level deep tree, decorators, stack trace

#### Option B: `minimal_color_demo.py` - Color API Features
Symlink to `complete-example-01/minimal_color_demo.py`:
- Shows color API methods (`set_foreground`, `set_background`, `colored`)
- Linear flow with colors at specific message points
- Demonstrates 7 feature categories separately

**Why use this folder?** Choose the demo style:
- **compact_color_demo.py** = Deep tree + @logged decorator + stack_trace()
- **minimal_color_demo.py** = Color API showcase (linear flow)

### complete-example-01/

Thirteen progressive examples demonstrating core logging features:

| Example | Description |
|---------|-------------|
| **example_01_basic.py** | Basic logging concepts |
| **example_02_actions.py** | Nested actions |
| **example_03_errors.py** | Error handling |
| **example_04_api_server.py** | HTTP simulation |
| **example_05_data_pipeline.py** | ETL pipeline |
| **example_06_deep_nesting.py** | 7-level nesting |
| **example_07_all_data_types.py** | All data types |
| **example_08_ultra_deep_nesting.py** | Ultra-deep nesting (up to 10 levels) |
| **example_09_comprehensive.log** | Comprehensive log sample |
| **minimal_color_demo.py** | Color API showcase |

View with `view_tree.py` for colored tree visualization.

### 3level-nested-colored/

Three-level nested colored example demonstrating color hierarchy:
- Yellow block at root level
- Cyan block for nested operations
- Demonstrates color inheritance and reset

### comp-with-parser/

Comprehensive example with **foreground/background color support**:

| File | Purpose |
|------|---------|
| **example_09_comprehensive.py** | Full color API demo |
| **run_and_analyze.sh** | Complete pipeline script |
| **parse_comprehensive.py** | Log parser with validation |
| **view_tree_colored.py** | Tree viewer with line numbers & colors |
| **view_log_colored.py** | Log viewer showing color hints |
| **view_line_colored.py** | Single line viewer with custom colors |

## 🎨 Color API

```python
from logxpy import log

# Method 1: Context colors (returns self for chaining)
log.set_foreground("cyan")
log.info("Cyan text")
log.reset_foreground()

# Method 2: Combined chaining
log.set_foreground("white").set_background("red")
log.error("White on red")
log.reset_foreground().reset_background()

# Method 3: One-shot colored message
log.colored(
    "╔═══════════════════════════════════════╗\n"
    "║  ⚠️  IMPORTANT HIGHLIGHTED BLOCK         ║\n"
    "╚═══════════════════════════════════════╝",
    foreground="black",
    background="yellow"
)
```

**Available colors**: black, red, green, yellow, blue, magenta, cyan, white, light_gray, dark_gray, light_red, light_green, light_blue, light_yellow, light_magenta, light_cyan

## 📋 Sqid Task ID Format

LogXPy uses **Sqids** - ultra-short hierarchical task IDs:

| Format | Example | Length | Use Case |
|--------|---------|--------|----------|
| Root | `"Xa.1"` | 4 chars | Top-level task |
| Child | `"Xa.1.1"` | 6 chars | Nested action |
| Deep | `"Xa.1.1.2"` | 8 chars | 3 levels deep |

**Benefits:**
- 89% smaller than UUID4 (4-12 chars vs 36)
- Human-readable hierarchy (dots show depth)
- Process-isolated (PID prefix prevents collisions)

## 📦 Compact Field Names

LogXPy uses 1-2 character field names to minimize log size:

| Compact | Legacy | Meaning |
|---------|--------|---------|
| `ts` | `timestamp` | Unix timestamp (seconds) |
| `tid` | `task_uuid` | Task ID (Sqid format) |
| `lvl` | `task_level` | Hierarchy level array |
| `mt` | `message_type` | Log level (info, success, error) |
| `at` | `action_type` | Action type (for emoji) |
| `st` | `action_status` | started/succeeded/failed |
| `dur` | `duration` | Duration in seconds |
| `msg` | `message` | Log message text |

## 🚀 Quick Start

```bash
# Basic examples
cd complete-example-01
python example_01_basic.py
python view_tree.py example_01_basic.log

# Color features
cd comp-with-parser
./run_and_analyze.sh

# Compact demo
cd compact-color-demo
./run_compact.sh
```

## 📖 Example Descriptions

### example_01_basic.py
**Basic logging concepts** - Simple introduction to LogXPy logging with Message.log() and start_action().

### example_02_actions.py
**Nested actions** - Demonstrates hierarchical action tracking with start_action() context managers.

### example_03_errors.py
**Error handling** - Shows exception logging with write_traceback() and error status tracking.

### example_04_api_server.py
**HTTP simulation** - Simulates HTTP request/response logging with action types like `http:request`.

### example_05_data_pipeline.py
**ETL pipeline** - Demonstrates data pipeline logging with `pipeline:etl` action type.

### example_06_deep_nesting.py
**7-level nesting** - Shows deeply nested action hierarchies for complex operations.

### example_07_all_data_types.py
**All data types** - Demonstrates all data type logging methods (color, currency, datetime, enum, etc.).

### example_08_ultra_deep_nesting.py
**Ultra-deep nesting** - Extends nesting to 10 levels, showing maximum depth capability.

### example_09_comprehensive.log
**Comprehensive sample** - Complete log file with all features demonstrated.

### minimal_color_demo.py
**Color API showcase** - Linear demonstration of all color API features separately.
