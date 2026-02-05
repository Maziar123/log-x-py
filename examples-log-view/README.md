# 🌲 Log Examples with Beautiful Tree Visualization

Seven comprehensive examples showing how to create structured logs with **logxpy** and visualize them as beautiful trees with **colors, emojis, and Unicode**.

![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-green.svg) ![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)

Inspired by [eliottree](https://github.com/jonathanj/eliottree) but with modern Python 3.12+ features and zero external dependencies.

## Examples

### Example 01: Basic Logging
**File:** `example_01_basic.py`

Simple log messages demonstrating basic usage.

```bash
python example_01_basic.py
python view_tree.py example_01_basic.log
```

### Example 02: Actions (Nested Operations)
**File:** `example_02_actions.py`

Demonstrates nested actions creating a tree structure.

```bash
python example_02_actions.py
python view_tree.py example_02_actions.log
```

### Example 03: Error Handling
**File:** `example_03_errors.py`

Shows successful and failed operations with error handling.

```bash
python example_03_errors.py
python view_tree.py example_03_errors.log
```

### Example 04: API Server Simulation
**File:** `example_04_api_server.py`

Realistic API server handling multiple HTTP requests.

```bash
python example_04_api_server.py
python view_tree.py example_04_api_server.log
```

### Example 05: Data Pipeline
**File:** `example_05_data_pipeline.py`

Complex ETL data pipeline with multiple stages.

```bash
python example_05_data_pipeline.py
python view_tree.py example_05_data_pipeline.log
```

### Example 06: Deep Nesting (7 Levels) ⭐ NEW!
**File:** `example_06_deep_nesting.py`

Demonstrates deeply nested operations up to 7 levels showing complete tree structure with enter/exit at each level.

**Three patterns:**
- Functional nesting (Server → HTTP → Validation → Auth → Cache → DB → Level 7)
- Class-based nesting (Application → Service → Repository → Pool → Connection → Query → Parser)
- Recursive tree processing (Root → Branches → Leaves → Data → Validate → Transform → Output)

```bash
python example_06_deep_nesting.py
python view_tree.py example_06_deep_nesting.log
```

### Example 07: All Data Types & Objects ⭐ NEW!

**File:** `example_07_all_data_types.py`

Comprehensive test of all data types and structures:
- **Primitives**: int, float, bool, str, None, Unicode, emojis
- **Collections**: list, dict, tuple, set (empty, nested, deep)
- **Complex**: API responses, configs, nested objects
- **Special**: paths, URLs, SQL, JSON strings, special chars
- **Edge Cases**: infinity, NaN, very large/tiny numbers
- **Errors**: validation errors, exceptions, stacktraces
- **Metrics**: performance stats, timing data
- **Nested**: 4-level deep actions with complex data

```bash
python example_07_all_data_types.py
python view_tree.py example_07_all_data_types.log
```

Perfect for testing how different data types are displayed!

## Run All Examples

```bash
# Run all examples
./run_all.sh

# Run a single example
./run_single.sh 1  # Replace 1 with 1-7
```

## Modern Tree Visualization ✨

The `view_tree.py` viewer shows logs as a beautiful, modern tree structure with professional design:

### Features

- 🎨 **Color-coded output** - ANSI colors for status, types, and depth levels
- 😊 **Emoji support** - Visual icons for quick scanning (✔️ ❌ ⚡ 💾 🌐 🔐 etc.)
- 📊 **Clean design** - Minimal, professional output
- 🌲 **Deep nesting** - Enhanced visualization for deeply nested operations (7+ levels)
- ⏱️ **Smart formatting** - Compact timestamps, color-coded durations
- 🎯 **Type detection** - Auto-detects database, API, auth, payment operations
- ⚡ **Zero dependencies** - Pure Python, no external packages required
- 🔧 **Flexible options** - Colors, emojis, ASCII mode, depth limits

### Visual Indicators

**Status Colors:**
- ✔️ `succeeded` - Bright green
- ✖️ `failed` - Bright red  
- ▶️ `started` - Bright blue

**Type Emojis:**
- 💾 Database operations
- 🔌 API/HTTP requests
- 🔐 Authentication
- 💳 Payments
- 🖥️ Server operations
- 🔄 Pipelines/ETL

**Depth Colors:**
Automatic color cycling (cyan → blue → magenta → green → yellow) for visual separation of nesting levels.

### Usage Examples

```bash
# Default mode (colors + emojis)
python view_tree.py example_01_basic.log

# ASCII mode (plain text, no colors/emojis)
python view_tree.py example_01_basic.log --ascii

# Disable emojis only
python view_tree.py example_02_actions.log --no-emojis

# Disable colors only
python view_tree.py example_03_errors.log --no-colors

# Limit depth for deeply nested logs
python view_tree.py example_06_deep_nesting.log --depth-limit 5
```

### Example Output

**With Colors & Emojis:**
```text
──────────────────────────────────────────────────────────────────────
🌲 Log Tree: example_02_actions.log
──────────────────────────────────────────────────────────────────────

Total entries: 15

bbb84413-578b-429a-8542-c64dcb69cd18
├── ⚡ order:process/1 ⇒ ▶️ started 13:56:34
│   ├── order_id: ORD-001
├── 💬 order:validate/2 13:56:34
│   ├── items: 3
│   ├── total: 99.99
│   ├── 💳 payment:charge/3/1 ⇒ ▶️ started 13:56:34
│   │   ├── amount: 99.99
│   ├── 💬 payment:success/3/3 13:56:35
│   │   ├── transaction_id: txn_123
│   ├── 💳 payment:charge/3/4 ⇒ ✔️ succeeded 13:56:35 ⏱️45ms
```

**ASCII Mode:**
```text
----------------------------------------------------------------------
Log Tree: example_01_basic.log
----------------------------------------------------------------------

Total entries: 6

a0bba8f9-7e90-4d76-8c57-58ce8cb63ed5
+-- app:startup/1 => started 13:56:30
    |-- version: 1.0.0
    |-- environment: production
```

## Quick Start

```bash
# Run one example
python example_01_basic.py

# View with colors and emojis (default)
python view_tree.py example_01_basic.log

# View in ASCII mode
python view_tree.py example_01_basic.log --ascii

# View deeply nested with depth limit
python view_tree.py example_06_deep_nesting.log --depth-limit 5
```
