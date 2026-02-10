# CLI Viewer Examples

Examples demonstrating the **logxpy-cli-view** colored tree viewer for LogXPy logs.

## Quick Start

```bash
# View a log file as a colored tree
logxpy-view example-01-simple-task/simple_task.log

# Show statistics
logxpy-view stats example-03-errors/with_errors.log

# Export to HTML
logxpy-view export -f html -o report.html example-04-web-service/web_service.log

# Watch logs in real-time
logxpy-view tail -f example-01-simple-task/simple_task.log
```

## Numbered Examples (Recommended Learning Path)

| # | Example | Description | Files |
|---|---------|-------------|-------|
| 01 | [example-01-simple-task](example-01-simple-task/) | Basic rendering + export + stats | main.py, simple_task.log |
| 02 | [example-02-nested-tasks](example-02-nested-tasks/) | Nested tasks + task level analysis | main.py, nested_tasks.log |
| 03 | [example-03-errors](example-03-errors/) | Error handling + error analysis | main.py, with_errors.log |
| 04 | [example-04-web-service](example-04-web-service/) | HTTP logs + pattern extraction | main.py, web_service.log |
| 05 | [example-05-data-pipeline](example-05-data-pipeline/) | ETL pipeline + time series | main.py, pipeline.log |
| 06 | [example-06-filtering](example-06-filtering/) | All 16 filter functions | main.py, test.log |
| 07 | [example-07-color-themes](example-07-color-themes/) | ThemeMode enum + themes | main.py, colors.log |
| 08 | [example-08-metrics](example-08-metrics/) | Comprehensive metrics + analytics | main.py, metrics.log |
| 09 | [example-09-generating](example-09-generating/) | Log generation + export | main.py, output.log |
| 10 | [example-10-deep-functions](example-10-deep-functions/) | Deep function call tracking | main.py, deep.log |
| 11 | [example-11-async-tasks](example-11-async-tasks/) | Async task monitoring | main.py, async.log |

## Descriptive Examples (Advanced Topics)

| Example | Description |
|---------|-------------|
| [3level-nested-colored](3level-nested-colored/) | Deep nesting with color visualization |
| [colored_tests](colored_tests/) | Color rendering tests |
| [compact-color-demo](compact-color-demo/) | Compact format color demo |
| [complete-example-01](complete-example-01/) | Comprehensive reference (9 examples in one) |
| [comp-with-parser](comp-with-parser/) | Integration with log parser |

## CLI Commands

### Render (Default)

```bash
logxpy-view render <file>         # View as tree (default)
logxpy-view render <file> --format oneline
logxpy-view render <file> --theme dark
logxpy-view render <file> --ascii  # Use ASCII instead of Unicode
```

### Statistics

```bash
logxpy-view stats <file>          # Show statistics
logxpy-view stats <file> --by-level
logxpy-view stats <file> --by-action-type
```

### Export

```bash
logxpy-view export <file> -f json -o out.json
logxpy-view export <file> -f csv -o out.csv
logxpy-view export <file> -f html -o out.html
logxpy-view export <file> -f logfmt -o out.log
```

### Monitoring

```bash
logxpy-view tail <file>           # Tail log file
logxpy-view tail -f <file>        # Follow mode (like tail -f)
logxpy-view tail --dashboard <file>  # Live dashboard
```

## Filtering Options

| Option | Description |
|--------|-------------|
| `--task-uuid <uuid>` | Filter by task UUID (Sqid) |
| `--select <jmespath>` | JMESPath query |
| `--start <date>` | Filter after ISO8601 date |
| `--end <date>` | Filter before ISO8601 date |
| `--status <status>` | Filter by action status |
| `--action-type <pattern>` | Filter by action type |
| `--min-duration <sec>` | Filter by minimum duration |
| `--max-duration <sec>` | Filter by maximum duration |
| `--keyword <text>` | Search in all values |
| `--min-level <n>` | Filter by minimum depth |
| `--max-level <n>` | Filter by maximum depth |

## Color System

The viewer renders colors based on field types:

| Type | Color | Example |
|------|-------|---------|
| Numbers | Cyan | `count: 42` |
| Booleans | Magenta | `success: true` |
| Strings | White | `name: "test"` |
| Errors | Red | `error: "failed"` |
| Success | Green | `status: "succeeded"` |
| Timestamps | Gray | `ts: 1234567890.0` |
| Task IDs | Bright Magenta | `tid: "Xa.1"` |

## Custom Colors

Logs can include color hints:

```python
{
    "fg": "cyan",              # Foreground color
    "bg": "yellow",            # Background color
    "message": "Colored text"
}
```

Available colors: black, red, green, yellow, blue, magenta, cyan, white, light_gray, dark_gray, light_red, light_green, light_blue, light_yellow, light_magenta, light_cyan
