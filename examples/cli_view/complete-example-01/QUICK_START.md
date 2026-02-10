# Quick Start Guide - Using UV

All scripts now use **uv** for running Python code.

## 🚀 Fastest Way to Run

```bash
cd /mnt/N1/MZ/AMZ/Projects/Prog/a_cross/log-x-py/examples/cli_view

# Run any example (1-5) and view its log automatically
./run_single.sh 1  # Basic logging
./run_single.sh 2  # Actions and nested operations
./run_single.sh 3  # Error handling
./run_single.sh 4  # API server simulation
./run_single.sh 5  # Data pipeline
```

## 📋 What Each Script Does

### `run_single.sh <number>`
- Runs the specified example using `uv run`
- Automatically displays the log using the simple viewer
- Shows output in a readable format

**Example:**
```bash
./run_single.sh 1
```

### `run_all.sh`
- Runs all 5 examples sequentially
- Shows each log after generating it
- Pauses between examples (press Enter to continue)

**Example:**
```bash
./run_all.sh
```

## 📂 Manual Running (Step by Step)

### 1. Create a Log

```bash
# Using uv (recommended)
uv run example_01_basic.py

# Result: Creates example_01_basic.log
```

### 2. View the Log

```bash
# Using Python directly
python view_tree.py example_01_basic.log

# Result: Displays structured log with tree format
```

## 🎯 All Examples

| Number | Script | Description | Log Entries |
|--------|--------|-------------|-------------|
| 1 | `example_01_basic.py` | Basic logging messages | 6 |
| 2 | `example_02_actions.py` | Nested actions (tree structure) | 15 |
| 3 | `example_03_errors.py` | Error handling & recovery | 12 |
| 4 | `example_04_api_server.py` | REST API server simulation | 40 |
| 5 | `example_05_data_pipeline.py` | ETL data pipeline | 32 |
| 6 | `example_06_deep_nesting.py` | **Deep nesting (7 levels) ⭐** | 102 |

## 📝 Example Output

When you run `./run_single.sh 2`, you'll see:

```
======================================================================
Running: example_02_actions.py
======================================================================

✓ Log created: example_02_actions.log

======================================================================
Viewing log: example_02_actions.log
======================================================================

Task: 63150bf4...
----------------------------------------------------------------------
2026-02-05 12:49:31.541 | order:process [started]
  order_id: ORD-001
2026-02-05 12:49:31.541 | order:validate
  items: 3
  total: 99.99
  2026-02-05 12:49:31.591 | payment:charge [started]
    amount: 99.99
  2026-02-05 12:49:31.591 | payment:gateway
    gateway: stripe
  ...
```

## 🔧 Why UV?

**uv** is a fast Python package installer and runner:
- ✅ Faster than pip
- ✅ Better dependency management
- ✅ Automatic virtual environment handling
- ✅ Works across platforms

## 🆘 If You Don't Have UV

### Option 1: Install UV (Recommended)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Option 2: Use Python Directly
```bash
# Run example
python example_01_basic.py

# View log
python view_tree.py example_01_basic.log
```

## ✅ Summary

**Quickest way to see examples:**
```bash
./run_single.sh 1  # Replace 1 with any number 1-5
```

**Run all examples:**
```bash
./run_all.sh
```

**Manual control:**
```bash
python example_01_basic.py
python view_tree.py example_01_basic.log
```

That's it! All examples use **uv** for better performance and dependency management.
