# LogXPy Log Parser & Analyzer

A Python library for parsing, analyzing, and querying LogXPy log files with rich export formats, powerful filtering capabilities, real-time monitoring, indexing, and time-series analysis.

## Features

- **Simple One-Line API** - Parse entire files in one call
- **Indexing System** - Fast lookups for large log files
- **Powerful Filtering** - By level, time, action type, field values
- **Time Series Analysis** - Anomaly detection, heatmaps, burst detection
- **Aggregation** - Multi-file analysis and aggregation
- **Analysis** - Performance stats, error summaries, task trees
- **Export** - JSON, CSV, HTML, Markdown, DataFrame
- **Real-time Monitoring** - Watch logs as they grow
- **CLI Tools** - Query, analyze, view, and visualize logs

## Installation

```bash
pip install logxy-log-parser
```

## Quick Start

### Simple One-Line API

```python
from logxy_log_parser import parse_log, check_log, analyze_log

# One-line parsing
entries = parse_log("app.log")
print(f"Parsed {len(entries)} entries")

# Parse + validate
result = check_log("app.log")
print(f"Valid: {result.is_valid}, Entries: {result.entry_count}")

# Full analysis
report = analyze_log("app.log")
report.print_summary()
```

### Core Classes

```python
from logxy_log_parser import LogParser, LogFilter, LogAnalyzer, LogFile

# Parse log file
parser = LogParser("app.log")
logs = parser.parse()

# Chain filters
result = (LogFilter(logs)
    .by_level("error", "warning")
    .by_time_range("2024-01-01", "2024-12-31")
    .slow_actions(1.0))

result.to_html("slow_errors.html")

# Analyze
analyzer = LogAnalyzer(logs)
for action in analyzer.slowest_actions(10):
    print(f"{action.action_type}: {action.duration:.3f}s")

# Real-time monitoring
logfile = LogFile.open("app.log")
for entry in logfile.watch():
    print(f"{entry.level}: {entry.message}")
```

## Simple API (One-Liners)

| Function | Purpose | Returns |
|----------|---------|---------|
| `parse_log(source)` | Parse log file | `ParseResult` |
| `parse_line(line)` | Parse single line | `LogXPyEntry` or `None` |
| `check_log(source)` | Parse + validate | `CheckResult` |
| `analyze_log(source)` | Full analysis | `AnalysisReport` |

## LogFile API (Real-time Monitoring)

The `LogFile` class provides fast file operations without full parsing:

```python
from logxy_log_parser import LogFile

# Open and validate
logfile = LogFile.open("app.log")

if logfile is None:
    print("Invalid log file")
    return

# Fast operations
print(f"Total entries: {logfile.entry_count}")
print(f"File size: {logfile.size} bytes")

# Check for content
if logfile.contains_error():
    print("Errors found!")

if logfile.contains(level="error", message="database"):
    print("Database errors found!")

# Find entries
first_error = logfile.find_first(level="error")
all_errors = logfile.find_all(level="error")
last_10 = logfile.tail(10)

# Wait for specific events
entry = logfile.wait_for_message("Application started", timeout=30)
if entry:
    print("Application is ready!")

error = logfile.wait_for_error(timeout=60)
if error:
    print(f"Error detected: {error.message}")
```

### LogFile Methods

| Method | Purpose |
|--------|---------|
| `LogFile.open(path)` | Open and validate |
| `logfile.entry_count` | Get entry count (fast, no full parse) |
| `logfile.size` | Get file size in bytes |
| `logfile.is_valid` | Check if valid LogXPy file |
| `logfile.refresh()` | Update and return new entry count |
| `logfile.contains(**criteria)` | Check if contains matching entries |
| `logfile.contains_message(text)` | Check if contains message text |
| `logfile.contains_error()` | Check if contains errors |
| `logfile.contains_level(level)` | Check if contains level |
| `logfile.find_first(**criteria)` | Find first matching entry |
| `logfile.find_last(**criteria)` | Find last matching entry |
| `logfile.find_all(**criteria)` | Find all matching entries |
| `logfile.tail(n)` | Get last N entries |
| `logfile.watch()` | Iterate new entries (generator) |
| `logfile.wait_for(**criteria)` | Wait for matching entry |
| `logfile.wait_for_message(text, timeout)` | Wait for message |
| `logfile.wait_for_error(timeout)` | Wait for error |

## LogFilter Methods

All filter methods return `LogEntries` for chaining:

```python
from logxy_log_parser import LogParser, LogFilter

parser = LogParser("app.log")
logs = parser.parse()

# Level filters
errors = LogFilter(logs).by_level("error")
warnings = LogFilter(logs).warning()
debug_and_info = LogFilter(logs).debug().info()

# Content filters
db_logs = LogFilter(logs).by_message("database")
api_logs = LogFilter(logs).by_action_type("http:*", "api:*")

# Time filters
recent = LogFilter(logs).by_time_range("2024-01-01", "2024-12-31")
yesterday = LogFilter(logs).after("2024-01-01").before("2024-01-02")

# Task filters
task = LogFilter(logs).by_task_uuid("Xa.1")
deep = LogFilter(logs).by_nesting_level(3, 99)

# Performance filters
slow = LogFilter(logs).slow_actions(5.0)
fast = LogFilter(logs).fast_actions(0.001)
by_duration = LogFilter(logs).by_duration(1.0, 60.0)

# Status filters
failed = LogFilter(logs).failed_actions()
succeeded = LogFilter(logs).succeeded_actions()
with_traceback = LogFilter(logs).with_traceback()

# Chaining
result = (LogFilter(logs)
    .by_level("error", "warning")
    .by_time_range("2024-01-01", "2024-12-31")
    .slow_actions(1.0)
    .limit(10))
```

### All Filter Methods

| Method | Purpose |
|--------|---------|
| `by_level(*levels)` | Filter by log level |
| `debug()` | DEBUG level only |
| `info()` | INFO level only |
| `warning()` | WARNING level only |
| `error()` | ERROR level only |
| `critical()` | CRITICAL level only |
| `by_message(pattern)` | Filter by message text |
| `by_action_type(*types)` | Filter by action type (wildcards) |
| `by_field(field, value)` | Filter by field value |
| `by_field_contains(field, value)` | Filter by field contains |
| `by_time_range(start, end)` | Filter by time range |
| `after(timestamp)` | Filter after timestamp |
| `before(timestamp)` | Filter before timestamp |
| `by_date(date)` | Filter by date |
| `by_task_uuid(*uuids)` | Filter by task ID (Sqid) |
| `by_nesting_level(min, max)` | Filter by depth |
| `by_duration(min, max)` | Filter by duration |
| `slow_actions(threshold)` | Slow actions only |
| `fast_actions(threshold)` | Fast actions only |
| `with_traceback()` | Entries with tracebacks |
| `failed_actions()` | Failed actions only |
| `succeeded_actions()` | Succeeded actions only |
| `started_actions()` | Started actions only |
| `filter(predicate)` | Custom filter function |
| `sort(key, reverse)` | Sort entries |
| `limit(n)` | Limit number of entries |
| `unique(key)` | Get unique entries |

## LogAnalyzer Methods

```python
from logxy_log_parser import LogParser, LogAnalyzer

parser = LogParser("app.log")
logs = parser.parse()

analyzer = LogAnalyzer(logs)

# Performance analysis
for action in analyzer.slowest_actions(10):
    print(f"{action.action_type}: {action.duration:.3f}s")

durations = analyzer.duration_by_action()
for action_type, stats in durations.items():
    print(f"{action_type}: avg={stats.mean:.3f}s, max={stats.max:.3f}s")

# Error analysis
summary = analyzer.error_summary()
print(f"Total errors: {summary.total_count}")
print(f"Most common error: {summary.most_common}")

# Task analysis
deepest = analyzer.deepest_nesting()
print(f"Deepest nesting: {deepest} levels")

orphans = analyzer.orphans()
print(f"Orphan entries: {len(orphans)}")

# Timeline
timeline = analyzer.timeline(interval="1min")
for period in timeline.intervals:
    print(f"{period.start}: {period.count} entries")

# Generate report
analyzer.generate_report("performance_report.html")
```

### All LogAnalyzer Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `slowest_actions(n)` | Get slowest actions | `list[ActionStat]` |
| `fastest_actions(n)` | Get fastest actions | `list[ActionStat]` |
| `duration_by_action()` | Duration by action type | `dict[str, DurationStats]` |
| `percentile_durations(percentile)` | Percentile durations | `dict[str, float]` |
| `task_duration_stats()` | Task duration statistics | `dict[str, DurationStats]` |
| `error_summary()` | Error analysis summary | `ErrorSummary` |
| `error_patterns()` | Find error patterns | `list[ErrorPattern]` |
| `failure_rate_by_action()` | Failure rate per action | `dict[str, float]` |
| `most_common_errors(n)` | Most common errors | `list[tuple]` |
| `deepest_nesting()` | Maximum nesting depth | `int` |
| `widest_tasks()` | Widest tasks | `list[tuple]` |
| `orphans()` | Unmatched entries | `LogEntries` |
| `timeline(interval)` | Timeline data | `Timeline` |
| `peak_periods(n)` | Busiest time periods | `list[TimePeriod]` |
| `quiet_periods(n)` | Quietest time periods | `list[TimePeriod]` |
| `generate_report(format)` | Generate report | `str` (html/text/json) |

## Indexing System

For fast lookups in large log files:

```python
from logxy_log_parser import LogIndex, IndexedLogParser

# Build index for fast lookups
index = LogIndex.build("app.log")

# Query by task UUID
positions = index.find_by_task("Xa.1")
print(f"Found {len(positions)} entries for task Xa.1")

# Query by level
errors = index.find_by_level("error")

# Query by time range
recent = index.find_by_time_range(start, end)

# Use indexed parser
parser = IndexedLogParser("app.log")
results = parser.query(task_uuid="Xa.1", level="error")

# Get specific task
task = parser.get_task("Xa.1")
print(f"Task duration: {task.duration}")

# Get all errors
errors = parser.get_errors()
```

### Index Methods

| Class/Method | Purpose |
|--------------|---------|
| `LogIndex.build(path)` | Build index |
| `index.stats` | Index statistics |
| `index.find_by_task(uuid)` | Find by task UUID |
| `index.find_by_level(level)` | Find by level |
| `index.find_by_time_range(start, end)` | Find by time range |
| `index.query(**criteria)` | Query with criteria |
| `index.get_lines(positions)` | Get log lines from positions |
| `index.save(path)` | Save index to file |
| `index.load(path)` | Load index from file |
| `index.is_stale()` | Check if index is stale |
| `IndexedLogParser(path)` | Indexed parser |
| `parser.query(**criteria)` | Query with criteria |
| `parser.get_task(task_uuid)` | Get specific task |
| `parser.get_errors()` | Get all errors |
| `parser.get_time_range(start, end)` | Get by time range |

## Time Series Analysis

```python
from logxy_log_parser import LogParser, TimeSeriesAnalyzer

parser = LogParser("app.log")
logs = parser.parse()

analyzer = TimeSeriesAnalyzer(logs)

# Bucket by interval
buckets = analyzer.bucket_by_interval(60)
for bucket in buckets:
    print(f"{bucket.start}: {bucket.count} entries, {bucket.error_rate:.1%} errors")

# Detect anomalies
for anomaly in analyzer.detect_anomalies(window_size=10, threshold=2.0):
    print(f"Anomaly at {anomaly.timestamp}: {anomaly.description}")

# Error rate trend
trend = analyzer.error_rate_trend(60)
for timestamp, rate in trend:
    print(f"{timestamp}: {rate:.1%} error rate")

# Level distribution
dist = analyzer.level_distribution(60)
print(f"Distribution: {dist}")

# Activity heatmap
heatmap = analyzer.activity_heatmap()
for hour, count in sorted(heatmap.items()):
    print(f"{hour:02d}:00 - {count} entries")

# Burst detection
bursts = analyzer.burst_detection(threshold=1.5, min_interval=5)
for burst in bursts:
    print(f"Burst from {burst.start} to {burst.end}: {burst.count} entries")
```

### Time Series Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `bucket_by_interval(seconds)` | Bucket by time interval | `list[TimeBucket]` |
| `detect_anomalies(window, threshold)` | Detect anomalies | `list[Anomaly]` |
| `error_rate_t(interval)` | Error rate over time | `list[tuple]` |
| `level_distribution(interval)` | Level distribution | `dict` |
| `activity_heatmap(hour_granularity)` | Activity heatmap | `dict` |
| `burst_detection(threshold, min_interval)` | Detect bursts | `list[Burst]` |

## Aggregation & Multi-File Analysis

```python
from logxy_log_parser import LogAggregator, MultiFileAnalyzer

files = ["app1.log", "app2.log", "app3.log"]

# Aggregate multiple files
aggregator = LogAggregator(files)
result = aggregator.aggregate()
print(f"Total entries: {len(result)}")

# Multi-file analysis
multi = MultiFileAnalyzer(files)
analysis = multi.analyze_all()
print(f"Files analyzed: {analysis.file_count}")

# Time series across files
ts = multi.time_series_analysis(interval_seconds=3600)
```

## CLI Commands

The library includes CLI tools for common operations:

### logxy-query - Query log files

```bash
# Basic query
logxy-query app.log --level error --output errors.json

# Time range filter
logxy-query app.log --start "2024-01-01" --end "2024-12-31"

# Duration filter
logxy-query app.log --min-duration 1.0 --sort duration --limit 20

# Multiple filters
logxy-query app.log --level error --action-type "db:*" --failed

# With regex action type
logxy-query app.log --action-type "db:.*" --action-type-regex

# Sort and limit
logxy-query app.log --sort timestamp --reverse --limit 100
```

### logxy-analyze - Analyze and generate reports

```bash
# Performance report
logxy-analyze app.log --slowest 20 --format html --output report.html

# Error analysis
logxy-analyze app.log --errors --format json --output errors.json

# Timeline analysis
logxy-analyze app.log --timeline --interval 1h

# Action statistics
logxy-analyze app.log --actions

# Full analysis
logxy-analyze app.log --report performance --format html
```

### logxy-view - View with colors

```bash
# View with level filter
logxy-view app.log --level error

# Follow mode (tail -f)
logxy-view app.log --follow

# Specific task
logxy-view app.log --task Xa.1

# No colors
logxy-view app.log --no-color
```

### logxy-tree - Visualize task tree

```bash
# Show tree for specific task
logxy-tree app.log --task Xa.1

# ASCII format
logxy-tree app.log --format ascii

# No colors
logxy-tree app.log --no-color
```

## Log Format Reference

### Core Fields (Every Log Entry)

| Field | Type | Description |
|-------|------|-------------|
| `ts` | float | Unix timestamp with microseconds |
| `tid` | string | Task ID (Sqid format) |
| `lvl` | array | Hierarchical level position e.g. `[1]`, `[1,1]` |
| `mt` | string | Message type: `info`, `success`, `error`, etc. |

### Action Fields (Optional)

| Field | Type | Description |
|-------|------|-------------|
| `at` | string | Action type (e.g., `UserService.authenticate`) |
| `st` | string | `started`, `succeeded`, or `failed` |
| `dur` | float | Execution time in seconds |

### Sample Log Entry

```json
{
  "ts": 1770277798.506508,
  "tid": "Xa.1",
  "lvl": [1],
  "mt": "info",
  "at": "http:request",
  "st": "started"
}
```

## Python Version

**3.12+** - Modern Python with optional pandas/rich support.

## Project Structure

```
logxy-log-parser/
├── logxy_log_parser/
│   ├── __init__.py          # Main exports
│   ├── simple.py            # Simple one-line API
│   ├── core.py              # LogParser, LogEntry
│   ├── filter.py            # LogFilter, LogEntries
│   ├── analyzer.py          # LogAnalyzer
│   ├── monitor.py           # LogFile (real-time)
│   ├── tree.py              # TaskTree, TaskNode
│   ├── index.py             # LogIndex, IndexedLogParser
│   ├── aggregation.py       # LogAggregator, TimeSeriesAnalyzer
│   ├── types.py             # Type definitions
│   ├── export.py            # Export functions
│   ├── cli.py               # CLI commands
│   ├── config.py            # Configuration management
│   └── utils.py             # Helper functions
├── tests/
│   ├── test_parser.py
│   ├── test_filter.py
│   ├── test_analyzer.py
│   └── fixtures/
│       └── sample.log
├── examples/
│   ├── basic_usage.py
│   ├── performance_analysis.py
│   └── error_analysis.py
├── pyproject.toml
└── README.md
```

## Design Principles

1. **Easy to use** - Simple, fluent API
2. **Type safe** - Full type hints
3. **Fast** - Stream processing for large files
4. **Flexible** - Multiple export formats
5. **Extensible** - Easy to add custom filters and analyzers
