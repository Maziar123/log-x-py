# LogXPY & LogXPY-CLI-View Tutorial Examples

This directory contains comprehensive tutorial examples demonstrating how to use **logxpy** for logging and **logxpy-cli-view** for viewing logs.

## Overview

These tutorials show the complete workflow:
1. **Create logs** using the logxpy library
2. **View logs** using the logxpy-view CLI viewer

## Tutorials

### Tutorial 01: Basic Logging
**File:** `tutorial_01_basic_logging.py`
**Log Output:** `tutorial_01_basic.log`

Learn the fundamentals:
- Basic logging methods (info, warning, error, success)
- Structured logging with key-value pairs
- Different log levels (debug, info, warning, error, critical)
- Fluent interface (chaining log calls)

```bash
python tutorial_01_basic_logging.py
logxpy-view tutorial_01_basic.log
```

### Tutorial 02: Actions and Context
**File:** `tutorial_02_actions_and_context.py`
**Log Output:** `tutorial_02_actions.log`

Learn advanced structuring:
- Actions - grouping related log messages
- Nested actions - hierarchical logging
- Context managers (with start_action())
- Action success/failure states
- Automatic duration tracking

```bash
python tutorial_02_actions_and_context.py
logxpy-view tutorial_02_actions.log
```

### Tutorial 03: Decorators
**File:** `tutorial_03_decorators.py`
**Log Output:** `tutorial_03_decorators.log`

Learn automatic logging:
- `@log.logged` - automatic function entry/exit logging
- `@log.timed` - execution time tracking
- `@log.retry` - automatic retry with logging
- Combining decorators
- Decorator configuration options

```bash
python tutorial_03_decorators.py
logxpy-view tutorial_03_decorators.log
```

### Tutorial 04: Error Handling
**File:** `tutorial_04_error_handling.py`
**Log Output:** `tutorial_04_errors.log`

Learn error handling patterns:
- Exception logging with tracebacks
- Error recovery patterns
- Exception context preservation
- Nested error handling
- Batch processing with partial failures

```bash
python tutorial_04_error_handling.py
logxpy-view tutorial_04_errors.log
```

### Tutorial 05: Real-World API Scenario
**File:** `tutorial_05_real_world_api.py`
**Log Output:** `tutorial_05_api.log`

Complete real-world example:
- REST API request/response logging
- Authentication and authorization
- Database operations
- External service calls
- Complex nested operations
- Performance metrics
- Comprehensive error handling

```bash
python tutorial_05_real_world_api.py
logxpy-view tutorial_05_api.log
```

## Running All Tutorials

Run all tutorials at once:

```bash
python run_all_tutorials.py
```

This will:
1. Execute all tutorial scripts
2. Generate all log files
3. Display viewing commands

## Viewing Logs

### Basic Viewing

```bash
# View a log file with tree structure (default command)
logxpy-view tutorial_01_basic.log

# View with ASCII characters (no Unicode)
logxpy-view --ascii tutorial_01_basic.log

# View with colors disabled
logxpy-view --color never tutorial_01_basic.log
```

### Filtering

```bash
# Filter by task UUID (Sqid)
logxpy-view --task-uuid <task-uuid> tutorial_02_actions.log

# Filter by action status (succeeded, failed, started)
logxpy-view --status failed tutorial_04_errors.log

# Filter by action type (supports wildcards)
logxpy-view --action-type 'api:*' tutorial_05_api.log

# Filter by keyword
logxpy-view --keyword 'payment' tutorial_05_api.log

# Filter using JMESPath query
logxpy-view --select 'level == `ERROR`' tutorial_04_errors.log
```

### Statistics

```bash
# Show statistics
logxpy-view stats tutorial_05_api.log

# Export statistics to JSON
logxpy-view stats tutorial_05_api.log -o stats.json
```

### Exporting

```bash
# Export to JSON
logxpy-view export tutorial_05_api.log -f json -o report.json

# Export to CSV
logxpy-view export tutorial_05_api.log -f csv -o report.csv

# Export to HTML
logxpy-view export tutorial_05_api.log -f html -o report.html

# Export to logfmt
logxpy-view export tutorial_05_api.log -f logfmt -o report.log
```

### Live Monitoring

```bash
# Tail log file (like tail -f)
logxpy-view tail tutorial_05_api.log

# Show initial 20 lines
logxpy-view tail -n 20 tutorial_05_api.log

# Show live dashboard
logxpy-view tail --dashboard tutorial_05_api.log

# Show periodic statistics
logxpy-view tail --aggregate -i 10 tutorial_05_api.log
```

## Log File Formats

All log files are in JSON Lines format (one JSON object per line):

```json
{"at": "app:task", "st": "started", "ts": 1707149123.456, "tid": "Xa.1", "lvl": [1], ...}
{"msg": "Processing data", "ts": 1707149123.789, "tid": "Xa.1", "lvl": [1, 1], ...}
{"at": "app:task", "st": "succeeded", "ts": 1707149124.012, "tid": "Xa.1", "lvl": [2], "dur": 0.556, ...}
```

## Tips and Best Practices

### 1. Structured Logging
Always use key-value pairs instead of string interpolation:

```python
# ✓ Good - structured
log.info("User logged in", user_id=123, username="alice")

# ✗ Bad - unstructured
log.info(f"User {username} (ID: {user_id}) logged in")
```

### 2. Use Actions for Related Operations
Group related log messages with actions:

```python
with start_action(action_type="order:process", order_id=order_id):
    log.info("Validating order")
    log.info("Processing payment")
    log.success("Order completed")
```

### 3. Log Contextual Information
Include relevant context in every log:

```python
log.error("Database connection failed",
          host="localhost",
          port=5432,
          retry_count=3,
          last_error="Connection timeout")
```

### 4. Use Appropriate Log Levels
- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages
- `SUCCESS` - Successful completion of operations
- `WARNING` - Warning messages (recoverable issues)
- `ERROR` - Error messages (serious problems)
- `CRITICAL` - Critical errors (system failure)

## Requirements

- Python 3.9+ for logxpy-cli-view
- Python 3.12+ for logxpy
- logxpy (logging library)
- logxpy-cli-view (log viewer CLI)

## Installation

```bash
# Install logxpy (requires Python 3.12+)
pip install logxpy

# Install logxpy-cli-view (requires Python 3.9+)
pip install logxpy-cli-view

# Or install from source
cd ../logxpy && pip install -e .
cd ../logxpy_cli_view && pip install -e .
```

## Next Steps

1. Start with Tutorial 01 to learn the basics
2. Progress through tutorials 02-04 to learn advanced features
3. Study Tutorial 05 for a complete real-world example
4. Adapt these patterns to your own applications
5. Explore the logxpy and logxpy_cli_view documentation

## 🎨 Color Features

LogXPy supports foreground/background colors that render in the CLI viewer:

```python
from logxpy import log

# Set foreground color
log.set_foreground("cyan")
log.info("This is cyan text")
log.reset_foreground()

# Set background color
log.set_background("yellow")
log.warning("Yellow background")
log.reset_background()

# Combined colors
log.set_foreground("white").set_background("red")
log.error("White on red background")
log.reset_foreground().reset_background()

# One-shot colored message with multiline highlight
log.colored(
    "╔═══════════════════════════════════╗\n"
    "║  ⚠️  IMPORTANT HIGHLIGHTED BLOCK  ║\n"
    "╚═══════════════════════════════════╝",
    foreground="black",
    background="yellow"
)
```

Available colors: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, `light_cyan`, `dark_gray`, `light_gray`

For a comprehensive color demo, see: `../cli_view/comp-with-parser/`

## Additional Resources

- **LogXPY Documentation:** `../../docs/`
- **LogXPY Examples:** `../logxpy/`
- **CLI Viewer Examples:** `../cli_view/`

## Troubleshooting

### Import Errors
If you get import errors, make sure both packages are installed:

```bash
cd ../logxpy && pip install -e .
cd ../logxpy_cli_view && pip install -e .
```

### Log Files Not Created
Check that the script has write permissions in the tutorials directory.

### Viewer Not Found
Make sure logxpy_cli_view is installed and `logxpy-view` is in your PATH.

## Contributing

Found an issue or have a suggestion? Please contribute!

1. Add new tutorial examples
2. Improve existing tutorials
3. Fix bugs or documentation issues
4. Share your own patterns and best practices
