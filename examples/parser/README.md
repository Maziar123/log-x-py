# Log Parser Examples

Examples demonstrating the **logxy-log-parser** library for parsing, analyzing, and querying LogXPy log files.

## Quick Start

```bash
# Run basic parsing example
python 01_basic.py

# Run filtering example
python 02_filtering.py

# Run analysis example
python 03_analysis.py
```

## Core Examples (01-09)

| # | File | Description |
|---|------|-------------|
| 01 | [01_basic.py](01_basic.py) | Basic log parsing and entry access |
| 02 | [02_filtering.py](02_filtering.py) | Filter logs by level, status, time, etc. |
| 03 | [03_analysis.py](03_analysis.py) | Performance analysis and statistics |

## Advanced Examples (10-16)

| # | File | Description |
|---|------|-------------|
| 10 | [10_check_presence.py](10_check_presence.py) | Check for specific log entries |
| 11 | [11_indexing_system.py](11_indexing_system.py) | Fast lookups with indexing |
| 12 | [12_time_series_analysis.py](12_time_series_analysis.py) | Time-based analysis and aggregation |
| 13 | [13_export_data.py](13_export_data.py) | Export to JSON, CSV, HTML, DataFrame |
| 14 | [14_realtime_monitoring.py](14_realtime_monitoring.py) | Real-time log monitoring with LogFile |
| 15 | [15_aggregation.py](15_aggregation.py) | Multi-file aggregation |
| 16 | [16_complete_reference.py](16_complete_reference.py) | Complete API reference |

## Descriptive Examples

| File | Description |
|------|-------------|
| [basic_usage.py](basic_usage.py) | Basic usage patterns |
| [error_analysis.py](error_analysis.py) | Error analysis techniques |
| [example_parser_usage.py](example_parser_usage.py) | Parser usage examples |
| [filtering.py](filtering.py) | Additional filtering examples |
| [monitoring.py](monitoring.py) | Monitoring patterns |
| [performance.py](performance.py) | Performance analysis |
| [task_tracing.py](task_tracing.py) | Task tracing examples |

## Features Demonstrated

### Simple API (One-Liners)

```python
from logxy_log_parser import parse_log, check_log, analyze_log

# Parse entire log file
entries = parse_log("app.log")

# Parse and validate
result = check_log("app.log")

# Parse, validate, and analyze
report = analyze_log("app.log")
report.print_summary()
```

### Core Classes

- **LogParser**: Parse log files into LogEntries
- **LogFilter**: Chainable filters for querying
- **LogAnalyzer**: Performance and error analysis
- **LogFile**: Real-time monitoring and fast checks
- **LogIndex**: Fast lookups via indexing
- **TaskTree**: Hierarchical task visualization

### Filtering Options

- `by_level()` - Filter by log level
- `by_message()` - Filter by message text
- `by_time_range()` - Filter by time range
- `by_action_type()` - Filter by action type
- `by_status()` - Filter by action status
- `by_duration()` - Filter by duration
- `by_field()` - Filter by field value
- `with_traceback()` - Entries with tracebacks

### Export Formats

- JSON
- CSV
- HTML
- Markdown
- DataFrame (pandas)
