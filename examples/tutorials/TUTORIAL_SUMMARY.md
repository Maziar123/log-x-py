# LogXPY Tutorial Suite - Complete Summary

## Overview

This tutorial suite demonstrates the complete workflow of using **logxpy** (logging library) for creating structured logs and **logxpy-cli-view** for viewing them with a beautiful tree structure.

## What Was Created

### 5 Comprehensive Tutorials

1. **Tutorial 01: Basic Logging** (`tutorial_01_basic_logging.py`)
   - Basic logging methods (info, warning, error, success)
   - Structured logging with key-value pairs
   - Different log levels
   - Fluent interface (chaining)
   - **Generated:** `tutorial_01_basic.log` (4.1 KB, 21 entries)

2. **Tutorial 02: Actions and Context** (`tutorial_02_actions_and_context.py`)
   - Actions for grouping related operations
   - Nested actions with hierarchical structure
   - Context managers (`with start_action()`)
   - Success/failure tracking
   - Automatic duration measurement
   - **Generated:** `tutorial_02_actions.log` (14.1 KB, 81 entries, 18 actions)

3. **Tutorial 03: Decorators** (`tutorial_03_decorators.py`)
   - `@log.logged` - automatic function entry/exit logging
   - `@log.timed` - execution time tracking
   - `@log.retry` - automatic retry with exponential backoff
   - Combining multiple decorators
   - **Generated:** `tutorial_03_decorators.log` (8.1 KB, 37 entries)

4. **Tutorial 04: Error Handling** (`tutorial_04_error_handling.py`)
   - Exception logging with context
   - Error recovery patterns
   - Nested error handling
   - Batch processing with partial failures
   - Different error severity levels
   - **Generated:** `tutorial_04_errors.log` (11.9 KB, 63 entries)

5. **Tutorial 05: Real-World API** (`tutorial_05_real_world_api.py`)
   - Complete REST API server simulation
   - Authentication and authorization
   - Database operations
   - External service calls
   - Complex nested operations
   - Performance metrics
   - **Generated:** `tutorial_05_api.log` (20.2 KB, 108 entries, 26 actions)

### Helper Tools

- **`_setup_imports.py`** - Handles import setup for all tutorials
- **`run_all_tutorials.py`** - Batch runner for all tutorials
- **`view_logs.sh`** - Convenient shell script for viewing logs
- **`README.md`** - Comprehensive documentation

### Tree Viewer

Use **`../cli_view/complete-example-01/view_tree.py`** - Rich tree visualization (no dependencies required)

## Quick Start

### Step 1: Run All Tutorials

```bash
cd tutorials
python run_all_tutorials.py
```

This will execute all 5 tutorials and generate the log files.

### Step 2: View Logs

#### Option A: Tree Viewer (No Dependencies Required)

```bash
# View specific log file as a tree
python ../cli_view/complete-example-01/view_tree.py tutorial_01_basic.log

# ASCII mode (no Unicode)
python ../cli_view/complete-example-01/view_tree.py tutorial_01_basic.log --ascii
```

#### Option B: Full Featured Viewer (Requires Installation)

First, install logxpy-cli-view:

```bash
cd ../logxpy_cli_view
pip install -e .
# or if system python is protected:
# pip install --user -e .
```

Then use the powerful tree viewer:

```bash
# Basic view with tree structure
logxpy-view tutorial_01_basic.log

# View with human-readable timestamps
logxpy-view tutorial_02_actions.log

# Filter by action status
logxpy-view --status failed tutorial_04_errors.log

# Filter by action type
logxpy-view --action-type 'api:*' tutorial_05_api.log

# Search by keyword
logxpy-view --keyword 'payment' tutorial_05_api.log

# Export to HTML
logxpy-view export tutorial_05_api.log -f html -o report.html
```

## Log File Format

All logs are in **JSON Lines** format (one JSON object per line):

```json
{"ts":1770283176.851,"tid":"Xa.1","lvl":[1],"mt":"loggerx:info","msg":"Application started","version":"1.0.0"}
{"ts":1770283176.851,"tid":"Xa.2","lvl":[1],"mt":"loggerx:success","msg":"User logged in","user_id":"alice123"}
```

This format is:
- **Structured** - Each field is queryable
- **Streamable** - Can be processed line by line
- **Standard** - Compatible with Eliot ecosystem

## Key Concepts Demonstrated

### 1. Structured Logging

Instead of string concatenation:
```python
# ✗ Bad - unstructured
log.info(f"User {user_id} logged in from {ip}")

# ✓ Good - structured
log.info("User logged in", user_id=user_id, ip=ip)
```

### 2. Actions for Grouping

Group related log messages:
```python
with start_action(action_type="order:process", order_id=123):
    log.info("Validating order")
    log.info("Processing payment")
    log.success("Order completed")
```

### 3. Nested Operations

Create hierarchical log structures:
```python
with start_action(action_type="order:process"):
    with start_action(action_type="payment:charge"):
        log.info("Charging card")
    with start_action(action_type="inventory:reserve"):
        log.info("Reserving items")
```

### 4. Automatic Context

Decorators capture function behavior automatically:
```python
@log.logged
def process_data(items):
    # Automatically logs entry, exit, args, result, and timing
    return [process(item) for item in items]
```

## Real-World Use Cases Covered

### API Server Logging
- HTTP request/response tracking
- Authentication and authorization
- Database query logging
- External service calls
- Error handling and recovery

### Data Processing
- Batch operations
- Progress tracking
- Partial failure handling
- Performance metrics

### Error Tracking
- Exception logging with context
- Retry mechanisms
- Error recovery patterns
- Traceback preservation

## Statistics from Generated Logs

| Tutorial | Log Size | Entries | Actions | Success | Failed |
|----------|----------|---------|---------|---------|--------|
| Tutorial 01 | 4.1 KB | 21 | 0 | - | - |
| Tutorial 02 | 14.1 KB | 81 | 18 | 16 | 2 |
| Tutorial 03 | 8.1 KB | 37 | 4 | 4 | 0 |
| Tutorial 04 | 11.9 KB | 63 | 14 | 12 | 2 |
| Tutorial 05 | 20.2 KB | 108 | 26 | 22 | 4 |
| **Total** | **58.4 KB** | **310** | **62** | **54** | **8** |

## Next Steps

### For Learning
1. Start with Tutorial 01 to understand basics
2. Progress through tutorials 02-04 to learn advanced features
3. Study Tutorial 05 for a complete real-world example

### For Your Own Projects
1. Copy `_setup_imports.py` pattern for your imports
2. Adapt logging patterns from the tutorials
3. Use actions to group related operations
4. Always log structured data (key-value pairs)
5. Use decorators for automatic logging

### Advanced Features
Explore the full documentation:
- **LogXPY docs:** `../../docs/`
- **LogXPY examples:** `../logxpy/`
- **CLI viewer examples:** `../cli_view/`

## Viewing Options Comparison

### Tree Viewer (view_tree.py)
**Pros:**
- No installation required
- Works immediately
- Rich tree visualization with Unicode
- Color-coded output
- Shows hierarchies clearly
- Duration tracking
- ASCII mode available

**Cons:**
- Basic filtering only
- No export features

### Full Viewer (logxpy-tree2)
**Pros:**
- Beautiful tree structure
- Color-coded output
- Powerful filtering (JMESPath, status, type, keywords)
- Export to HTML/JSON/CSV
- Statistics and metrics
- Duration tracking
- Action hierarchies clearly visible

**Cons:**
- Requires installation
- Needs dependencies

## Common Viewing Commands

```bash
# View with tree structure
logxpy-view tutorial_02_actions.log

# Show only errors
logxpy-view --status failed tutorial_*.log

# Filter by action type
logxpy-view --action-type 'payment:*' tutorial_05_api.log

# Search for specific text
logxpy-view --keyword 'database' tutorial_*.log

# JMESPath query
logxpy-view --select 'level == `ERROR`' tutorial_04_errors.log

# ASCII output (no Unicode)
logxpy-view --ascii tutorial_*.log

# No colors
logxpy-view --color never tutorial_*.log

# Export to HTML
logxpy-view export tutorial_05_api.log -f html -o report.html

# View all tutorials together
logxpy-view tutorial_*.log
```

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError: No module named 'logxpy'`:
```bash
# The tutorials use _setup_imports.py which should handle this
# But if it fails, check that logxpy/__init__.py has been fixed
```

### Viewer Not Found
If `logxpy-tree2` is not found:
```bash
cd ../logxpy_cli_view
pip install -e .
# or
python -m pip install --user -e .
```

### Missing Dependencies
If logxpy_cli_view complains about missing modules:
```bash
cd ../logxpy_cli_view
pip install -e ".[dev]"
```

## Architecture

```
tutorials/
├── _setup_imports.py           # Import helper
├── tutorial_01_basic_logging.py
├── tutorial_02_actions_and_context.py
├── tutorial_03_decorators.py
├── tutorial_04_error_handling.py
├── tutorial_05_real_world_api.py
├── run_all_tutorials.py        # Batch runner
├── view_logs.sh               # Shell helper
├── README.md                   # Documentation
├── TUTORIAL_SUMMARY.md         # This file
└── *.log                       # Generated logs

Tree viewer:
../cli_view/complete-example-01/view_tree.py  # Rich tree visualization
```

## Key Files Modified

To make this work, one fix was applied to logxpy:

**File:** `logxpy/src/__init__.py`
**Fix:** Updated `_parse_compat()` function to handle both `eliot.parse` and `logxpy.parse` module names for backward compatibility.

## Conclusion

This tutorial suite provides:
- ✅ 5 comprehensive, working examples
- ✅ 310+ log entries demonstrating real-world patterns
- ✅ Structured logging best practices
- ✅ Action-based hierarchical logging
- ✅ Error handling patterns
- ✅ Decorator-based automatic logging
- ✅ Two viewing options (simple and advanced)
- ✅ Complete documentation
- ✅ Ready-to-run scripts

You now have a complete reference for using logxpy and logxpy_cli_view together!

## Contributing

To add more tutorials:
1. Create `tutorial_06_*.py` following the same pattern
2. Use `from _setup_imports import log, to_file, start_action`
3. Generate a `.log` file
4. Update `run_all_tutorials.py` to include it
5. Document the new tutorial in README.md

Happy logging! 📊🌳
