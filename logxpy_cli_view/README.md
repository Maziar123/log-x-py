# logxpy-cli-view

[![Python versions](https://img.shields.io/pypi/pyversions/logxpy-cli-view.svg)](https://pypi.org/project/logxpy-cli-view/)

Render [LogXPy](https://github.com/Maziar123/log-x-py) logs as an ASCII tree with powerful filtering, statistics, and real-time monitoring.

Forked from [eliottree](https://github.com/jonathanj/eliottree) by Jonathan Jacobs.
Modernized with new features and integrated with the LogXPy ecosystem.

## Features

- **Beautiful ASCII Trees** - Unicode box-drawing characters (├── └── │)
- **ANSI Colors** - Color-coded values (numbers: cyan, booleans: magenta, errors: red)
- **Emoji Icons** - Visual indicators (💾 database, 🔌 API, 🔐 auth)
- **Color Block Rendering** - Supports foreground/background colors from LogXPy
- **Powerful Filtering** - By status, action type, duration, keyword, JMESPath, date range
- **Statistics** - Success/failure rates, duration stats, action type counts
- **Export** - JSON, CSV, HTML, logfmt formats
- **Live Monitoring** - Tail mode with real-time updates and dashboard
- **Pattern Extraction** - Extract emails, IPs, URLs from logs
- **Theme Support** - Auto, dark, and light themes

## Example

Given this LogXPy log output (with modern compact field names):

```json
{"ts":1770562483.38,"tid":"Xa.1","lvl":[1],"at":"app:soap:client:request","st":"started","dump":"/home/user/dump.xml","uri":"http://example.org/soap"}
{"ts":1770562484.38,"tid":"Xa.1","lvl":[2,1],"at":"app:soap:client:success","st":"started"}
{"ts":1770562484.52,"tid":"Xa.1","lvl":[2,2],"at":"app:soap:client:success","st":"succeeded","dump":"/home/user/dump_res.xml"}
{"ts":1770562484.52,"tid":"Xa.1","lvl":[3],"at":"app:soap:client:request","st":"succeeded","status":200}
```

`logxpy-view` produces:

```text
Xa.1
└── 🔌 app:soap:client:request/1 ⇒ ▶️ started 17:18:03 ⧖ 1.238s
    ├── dump: /home/user/dump.xml
    ├── uri: http://example.org/soap
    ├── 🔌 app:soap:client:success/2/1 ⇒ ▶️ started 17:18:04 ⧖ 0.000s
    │   └── 🔌 app:soap:client:success/2/2 ⇒ ✔️ succeeded 17:18:04
    │       └── dump: /home/user/dump_res.xml
    └── 🔌 app:soap:client:request/3 ⇒ ✔️ succeeded 17:18:04
        └── status: 200
```

## Installation

```bash
pip install logxpy-cli-view
```

## CLI Usage

### Commands

```bash
# Render log file as tree (default)
logxpy-view app.log

# Show statistics
logxpy-view stats app.log

# Export to format
logxpy-view export app.log -f json -o output.json

# Live monitoring (tail)
logxpy-view tail app.log
```

### Filtering Options

```bash
# Filter by task UUID (Sqid)
logxpy-view --task-uuid Xa.1 app.log

# Filter by date range
logxpy-view --start 2024-01-01T00:00:00 --end 2024-01-02T00:00:00 app.log

# Filter by action status
logxpy-view --status failed app.log

# Filter by action type (supports wildcards)
logxpy-view --action-type "db:*" app.log

# Filter by action type (regex)
logxpy-view --action-type "db:.*" --action-type-regex app.log

# Filter by duration
logxpy-view --min-duration 1.0 --max-duration 60.0 app.log

# Filter by field existence
logxpy-view --has-field error app.log

# Filter by keyword search
logxpy-view --keyword "database" app.log

# Filter by task level (depth)
logxpy-view --min-level 1 --max-level 3 app.log

# JMESPath query (multiple allowed)
logxpy-view --select "action_status == \`failed\`" app.log
logxpy-view --select "level == \`error\`" --select "duration > 1.0" app.log
```

### Output Options

```bash
# Output format
logxpy-view --format tree app.log    # Tree format (default)
logxpy-view --format oneline app.log  # One-line format

# Theme selection
logxpy-view --theme auto app.log    # Auto-detect (default)
logxpy-view --theme dark app.log    # Dark theme
logxpy-view --theme light app.log   # Light theme

# Field value length limit
logxpy-view --field-limit 50 app.log

# Hide line numbers
logxpy-view --no-line-numbers app.log

# Disable tree line coloring
logxpy-view --no-color-tree app.log

# ASCII mode (no Unicode/emoji)
logxpy-view --ascii app.log

# Disable emojis only
logxpy-view --no-emojis app.log

# Disable all colors
logxpy-view --no-colors app.log
```

### Statistics Options

```bash
# Show statistics
logxpy-view stats app.log

# Export statistics to JSON file
logxpy-view stats app.log -o stats.json
```

### Export Options

```bash
# Export to JSON
logxpy-view export app.log -f json -o output.json

# Export to CSV
logxpy-view export app.log -f csv -o output.csv

# Export to HTML
logxpy-view export app.log -f html -o output.html

# Export to logfmt
logxpy-view export app.log -f logfmt -o output.log

# Include/exclude fields
logxpy-view export app.log --include-fields tid,at,msg -o out.json
logxpy-view export app.log --exclude-fields tid,lvl -o out.json

# Set HTML title
logxpy-view export app.log -f html --title "My App Logs" -o out.html
```

### Tail/Monitoring Options

```bash
# Tail log file (like tail -f)
logxpy-view tail app.log

# Initial lines to show
logxpy-view tail app.log -n 20

# Don't follow file
logxpy-view tail app.log --no-follow

# Show live dashboard
logxpy-view tail app.log --dashboard

# Show periodic statistics aggregation
logxpy-view tail app.log --aggregate

# Aggregation interval (seconds)
logxpy-view tail app.log --aggregate -i 10

# Dashboard refresh rate (milliseconds)
logxpy-view tail app.log --dashboard -r 500
```

### Configuration File

Create `~/.config/logxpy-cli-view/config.json`:

```json
{
  "color": "auto",
  "field_limit": 100,
  "theme": "dark",
  "format": "tree"
}
```

## Python API

### Core Functions

```python
from logxpy_cli_view import render_tasks, render_oneline, tasks_from_iterable
import json

# Parse LogXPy log messages
tasks = tasks_from_iterable([
    json.loads(line)
    for line in open("app.log")
])

# Render as tree
render_tasks(tasks, write=print)

# Render as one-line format
render_oneline(tasks, write=print)
```

### Filter Functions

```python
from logxpy_cli_view import (
    filter_by_action_status,
    filter_by_action_type,
    filter_by_duration,
    filter_by_keyword,
    filter_by_jmespath,
    filter_by_uuid,
    filter_by_start_date,
    filter_by_end_date,
    filter_by_field_exists,
)

# Filter by status
failed_tasks = filter_by_action_status(tasks, "failed")

# Filter by action type (supports wildcards)
db_tasks = filter_by_action_type(tasks, "db:*")

# Filter by duration (min_seconds, max_seconds=None)
slow_tasks = filter_by_duration(tasks, 1.0, 60.0)

# Filter by keyword in field values
error_tasks = filter_by_keyword(tasks, "error")

# JMESPath query
filtered = filter_by_jmespath(tasks, "[?action_status == `failed`]")

# Filter by task UUID (Sqid)
specific_task = filter_by_uuid(tasks, "Xa.1")

# Filter by date range
recent = filter_by_start_date(tasks, "2024-01-01")
old = filter_by_end_date(tasks, "2024-12-31")

# Filter by field existence
has_error = filter_by_field_exists(tasks, "error")
```

### Export Functions

```python
from logxpy_cli_view import export_json, export_csv, export_html, export_logfmt

# Export to JSON
export_json(tasks, "output.json", pretty=True)

# Export to CSV
export_csv(tasks, "output.csv", flatten=True)

# Export to HTML
export_html(tasks, "output.html")

# Export to logfmt
export_logfmt(tasks, "output.log")
```

### Statistics Functions

```python
from logxpy_cli_view import calculate_statistics, print_statistics, create_time_series

# Calculate statistics
stats = calculate_statistics(tasks)

print(f"Total tasks: {stats.total_tasks}")
print(f"Success rate: {stats.success_rate:.1%}")
print(f"Failed actions: {stats.failed_count}")
print(f"Average duration: {stats.avg_duration:.3f}s")

# Print formatted statistics
print_statistics(stats)

# Create time series data
ts = create_time_series(tasks, interval_minutes=5)
```

### Pattern Extraction

```python
from logxpy_cli_view import extract_emails, extract_ips, extract_urls, extract_uuids

# Extract email addresses
emails = extract_emails(entries)

# Extract IP addresses
ips = extract_ips(entries)

# Extract URLs
urls = extract_urls(entries)

# Extract UUIDs
uuids = extract_uuids(entries)
```

### Live Monitoring

```python
from logxpy_cli_view import tail_logs, LiveDashboard, watch_and_aggregate

# Simple tailing
tail_logs("app.log")

# Live dashboard
dashboard = LiveDashboard()
dashboard.run()

# Watch and aggregate
watch_and_aggregate("app.log", interval=10)
```

## 🎨 Color Rendering from LogXPy

`logxpy-cli-view` supports rendering foreground/background colors from LogXPy log entries:

```python
from logxpy import log

# Set colors that will be rendered by the CLI viewer
log.set_foreground("cyan")
log.info("This renders with cyan text")

log.set_background("yellow").set_foreground("black")
log.error("Black text on yellow background")

# One-shot colored message
log.colored(
    "╔════════════════════════════════════╗\n"
    "║  ⚠️  IMPORTANT HIGHLIGHTED BLOCK  ║\n"
    "╚════════════════════════════════════╝",
    foreground="black",
    background="yellow"
)

log.reset_foreground().reset_background()
```

When viewed with `logxpy-view`, entries with `fg`/`bg` or `logxpy:foreground`/`logxpy:background` fields will render with those colors.

**Available colors**: black, red, green, yellow, blue, magenta, cyan, white, light_gray, dark_gray, light_red, light_green, light_blue, light_yellow, light_magenta, light_cyan

## Color System

### Type-based Colors

| Type | Color | ANSI Code |
|------|-------|-----------|
| Numbers | Cyan | `\033[36m` |
| Booleans | Magenta | `\033[35m` |
| Keys | Bright Blue | `\033[94m` |
| Error strings | Bright Red | `\033[91m` |
| Success strings | Bright Green | `\033[92m` |
| Regular strings | White | `\033[37m` |
| Timestamps | Dim Gray | `\033[90m` |
| Task IDs (Sqid) | Bright Magenta | `\033[95m` |

### Level-based Colors

| Level | Color |
|-------|-------|
| DEBUG | Gray |
| INFO | White |
| SUCCESS | Bright Green |
| NOTE | Yellow |
| WARNING | Bright Yellow |
| ERROR | Red |
| CRITICAL | Bright Red with background |

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

## Development

```bash
# Clone the repository
git clone https://github.com/Maziar123/log-x-py.git
cd log-x-py/logxpy_cli_view

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src

# Run type checker
mypy src/logxpy_cli_view
```

## Requirements

- Python 3.9+
- jmespath - JMESPath query support
- iso8601 - ISO8601 timestamp parsing
- colored - Terminal color output
- toolz - Functional utilities

## License

MIT License - see [LICENSE](LICENSE) file.
