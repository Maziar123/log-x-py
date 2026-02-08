# LogXPy CLI View - Features

This document describes all features of the logxpy-cli-view tree viewer.

## Core Features

### 1. ASCII Tree Rendering

Render LogXPy logs as beautiful ASCII trees with Unicode box-drawing characters.

```bash
logxpy-view app.log
```

Output:
```
56ffc3bf-08f7-4f71-8065-b91db2d54e1c
├── 🔌 http:request/1 ⇒ ▶️ started 14:30:00
│   ├── method: POST
│   └── path: /api/users
├── 🔐 auth:verify/2/1 ⇒ ▶️ started 14:30:00
│   ├── user_id: 123
│   └── valid: True
└── 💾 database:query/3/1 ⇒ ▶️ started 14:30:00
    ├── table: users
    └── 💾 database:result/3/2 14:30:01
        ├── rows: 10
        └── duration_ms: 45
```

### 2. Color Support

Full ANSI color support with automatic color coding:

- **Cyan** - Numbers
- **Magenta** - Booleans, UUIDs
- **Bright Blue** - Started status, Field keys
- **Bright Green** - Succeeded status
- **Bright Red** - Failed status
- **White** - Regular strings
- **Dim Gray** - Timestamps

### 3. Color Block Rendering

Supports `logxpy:foreground` and `logxpy:background` fields from log entries:

```python
# In your logxpy code
log.colored("Important message", foreground="red", background="yellow")
```

When viewed with `logxpy-view`, the message will render with the specified colors.

### 4. Emoji Icons

Automatic emoji icons based on action type keywords:

| Keyword | Emoji |
|---------|-------|
| `database`, `db:`, `query` | 💾 |
| `http`, `api`, `request` | 🔌 |
| `auth`, `login` | 🔐 |
| `payment`, `charge` | 💳 |
| `server` | 🖥️ |
| `pipeline`, `etl` | 🔄 |
| `error`, `fail` | 🔥 |
| Default | ⚡ |

### 5. Filtering

#### Filter by Action Status

```bash
logxpy-view app.log --status failed
logxpy-view app.log --status succeeded
```

#### Filter by Action Type

```bash
logxpy-view app.log --filter "db_*"
logxpy-view app.log --action-type "database:query"
```

#### Filter by Duration

```bash
logxpy-view app.log --min-duration 1.0  # Slower than 1 second
logxpy-view app.log --max-duration 5.0  # Faster than 5 seconds
```

#### Filter by Time Range

```bash
logxpy-view app.log --start 2024-01-01T00:00:00
logxpy-view app.log --end 2024-12-31T23:59:59
```

#### JMESPath Queries

```bash
logxpy-view app.log --select "action_status == 'failed'"
```

### 6. Export Functions

#### JSON Export

```bash
logxpy-view app.log --export json -o output.json
```

#### CSV Export

```bash
logxpy-view app.log --export csv -o output.csv
```

#### HTML Export

```bash
logxpy-view app.log --export html -o output.html
```

#### Logfmt Export

```bash
logxpy-view app.log --export logfmt -o output.log
```

### 7. Live Monitoring

#### Tail Mode

```bash
logxpy-view app.log --tail
```

Monitor log file as it grows, displaying new entries in real-time.

#### Dashboard Mode

```bash
logxpy-view app.log --tail --dashboard
```

Show a live updating dashboard with statistics.

#### Aggregation

```bash
logxpy-view app.log --tail --aggregate --interval 60
```

Show periodic statistics every 60 seconds.

### 8. Statistics

```bash
logxpy-view app.log --stats
```

Display statistics including:
- Total actions
- Success/failure rates
- Duration statistics (mean, median, min, max, std dev)
- Timeline analysis
- Top action types
- Task depth distribution

### 9. Display Options

#### ASCII Mode

```bash
logxpy-view app.log --ascii
```

Use plain ASCII characters instead of Unicode box-drawing.

#### Color Control

```bash
logxpy-view app.log --color never      # No colors
logxpy-view app.log --color always     # Force colors
logxpy-view app.log --no-color-tree    # No tree colors
```

#### Emoji Control

```bash
logxpy-view app.log --no-emojis
```

#### Depth Limiting

```bash
logxpy-view app.log --depth-limit 3
```

Limit nesting depth in the tree display.

#### Field Limiting

```bash
logxpy-view app.log --field-limit 50
```

Truncate field values to specified length.

#### Human-Readable Format

```bash
logxpy-view app.log --human-readable
```

Format durations and timestamps in human-readable format.

#### Timezone

```bash
logxpy-view app.log --local-timezone    # Use local timezone
logxpy-view app.log --utc-timestamps    # Use UTC (default)
```

### 10. Theme Support

```bash
logxpy-view app.log --theme dark
logxpy-view app.log --theme light
logxpy-view app.log --theme auto        # Auto-detect (default)
```

### 11. Configuration File

Create `~/.config/logxpy-cli-view/config.json`:

```json
{
  "color": "auto",
  "field_limit": 100,
  "theme": "dark",
  "human_readable": true,
  "utc_timestamps": false
}
```

## Python API

### Basic Usage

```python
from logxpy_cli_view import render_tasks, tasks_from_iterable

# Parse log lines
tasks = tasks_from_iterable(open("app.log"))

# Render as tree
print(render_tasks(tasks))
```

### Filtering

```python
from logxpy_cli_view import (
    filter_by_action_status,
    filter_by_action_type,
    filter_by_duration,
    filter_by_keyword,
)

# Filter tasks
failed = filter_by_action_status(tasks, "failed")
db_tasks = filter_by_action_type(tasks, "db_*")
slow = filter_by_duration(tasks, min_seconds=5.0)
```

### Export

```python
from logxpy_cli_view import export_json, export_csv, export_html

export_json(tasks, "output.json")
export_csv(tasks, "output.csv")
export_html(tasks, "output.html")
```

## CLI Commands Reference

### Main Command: `logxpy-view`

| Argument | Description |
|----------|-------------|
| `<file>` | Log file to view (required) |
| `--color <mode>` | Color mode: auto, always, never |
| `--ascii` | Use ASCII instead of Unicode |
| `--field-limit <num>` | Truncate field values |
| `--human-readable` | Format durations/timestamps |
| `--local-timezone` | Use local timezone |
| `--theme <theme>` | Color theme: auto, dark, light |
| `--depth-limit <num>` | Max nesting depth |
| `--ignore-task-key <key>` | Ignore specific fields |
| `--no-emojis` | Disable emoji icons |
| `--no-color-tree` | Don't color tree lines |

### Filter Options

| Option | Description |
|--------|-------------|
| `--task-uuid <uuid>` | Filter by task UUID |
| `--select <jmespath>` | JMESPath query filter |
| `--start <date>` | Start date (ISO8601) |
| `--end <date>` | End date (ISO8601) |
| `--status <status>` | Filter by action status |
| `--action-type <type>` | Filter by action type |
| `--action-type-regex` | Treat action-type as regex |
| `--min-duration <sec>` | Minimum duration filter |
| `--max-duration <sec>` | Maximum duration filter |
| `--has-field <field>` | Field existence check |
| `--keyword <keyword>` | Keyword search |
| `--min-level <level>` | Minimum task level depth |
| `--max-level <level>` | Maximum task level depth |

### Subcommands

#### `render` (default)

Render log as tree. Same as main command.

#### `stats`

```bash
logxpy-view stats [FILE...]
logxpy-view s [FILE...]
```

Show statistics and analysis.

#### `export`

```bash
logxpy-view export -f FORMAT -o OUTPUT [FILE...]
logxpy-view e -f FORMAT -o OUTPUT [FILE...]
```

Export to different formats.

#### `tail`

```bash
logxpy-view tail [FILE...]
logxpy-view t [FILE...]
```

Live log monitoring.

## Color System

### Supported Colors

**Foreground**: red, green, blue, yellow, magenta, cyan, white, black, light_gray, dark_gray, light_red, light_green, light_blue, light_yellow, light_magenta, light_cyan

**Background**: Same colors available

**Styles**: bold, dim, underline, blink, reverse, hidden

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

## Examples

### Example 1: View Failed Database Queries

```bash
logxpy-view app.log --filter "database:*" --status failed
```

### Example 2: Find Slow HTTP Requests

```bash
logxpy-view app.log --filter "http:*" --min-duration 5.0
```

### Example 3: Export Today's Errors

```bash
logxpy-view app.log --start "$(date -Iseconds)" --status failed --export json -o errors.json
```

### Example 4: Live Monitor with Color

```bash
logxpy-view app.log --tail --color always --no-emojis
```

### Example 5: Statistics Dashboard

```bash
logxpy-view app.log --stats -o stats.json
```

## Performance Notes

- **Memory Efficient**: Processes large files using generators
- **Fast Parsing**: Optimized JSON parsing
- **Lazy Evaluation**: Filters are applied during iteration
- **Caching**: JMESPath expressions are cached
