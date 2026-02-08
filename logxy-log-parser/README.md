# LogXPy Log Parser & Analyzer

A Python library for parsing, analyzing, and querying LogXPy log files with rich export formats, powerful filtering capabilities, and real-time monitoring.

## Overview

LogXPy creates structured JSON logs with hierarchical task trees. This library makes it easy to:
- **Parse** LogXPy log files (JSON Lines format)
- **Query** logs with powerful filters
- **Analyze** performance, errors, and patterns
- **Export** to multiple formats (JSON, CSV, HTML, Markdown, terminal)
- **Monitor** log files in real-time as they grow
- **Validate** and check log file contents without full parsing

## LogXPy Log Format Reference

### Core Fields (Every Log Entry)
| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | float | Unix timestamp with microseconds |
| `task_uuid` | string | Unique identifier for the transaction/action tree |
| `task_level` | array | Hierarchical level position e.g., `[1]`, `[1,1]`, `[1,1,1]` |
| `message_type` | string | Log level: `loggerx:debug`, `loggerx:info`, `loggerx:success`, `loggerx:warning`, `loggerx:error`, `loggerx:critical` |

### Action Fields (Optional)
| Field | Type | Description |
|-------|------|-------------|
| `action_type` | string | Function/class name (e.g., `UserService.authenticate`) |
| `action_status` | string | `started`, `succeeded`, or `failed` |
| `eliot:duration` / `logxpy:duration` | float | Execution time in seconds |

### Common Custom Fields
- `message` - Human-readable log message
- `exception` / `reason` - Error information
- `logxpy:traceback` - Full exception traceback
- Application-specific fields (e.g., `user_id`, `order_id`)

### Sample Log Entry
```json
{
  "timestamp": 1770277798.506508,
  "task_uuid": "311585e4-1c52-4691-95e2-65f7295abe8a",
  "task_level": [1],
  "order_id": 12345,
  "user_id": 789,
  "action_type": "__main__.OrderService.process_order",
  "action_status": "started"
}
```

---

## Installation

```bash
pip install logxy-log-parser
```

---

## Quick Start

```python
from logxy_log_parser import LogParser, LogFilter

# Parse a log file
parser = LogParser("path/to/logfile.log")

# Get all entries
logs = parser.parse()

# Filter by level
errors = LogFilter(logs).by_level("error")

# Filter by time range
recent = LogFilter(logs).by_time_range("2024-01-01", "2024-12-31")

# Export to HTML
errors.to_html("errors.html")

# Export to CSV
recent.to_csv("recent_logs.csv")
```

---

## Quick Start

### 1. Basic Parsing and Filtering
```python
from logxy_log_parser import LogParser, LogFilter

# Parse a log file
parser = LogParser("path/to/logfile.log")
logs = parser.parse()

# Filter by level
errors = LogFilter(logs).by_level("error")

# Filter by time range
recent = LogFilter(logs).by_time_range("2024-01-01", "2024-12-31")

# Export to HTML
errors.to_html("errors.html")

# Export to CSV
recent.to_csv("recent_logs.csv")
```

### 2. Real-time Monitoring with LogFile
```python
from logxy_log_parser import LogFile

# Open and validate a log file
logfile = LogFile.open("app.log")

if logfile is None:
    print("Invalid log file")
    return

# Get current entry count (fast, without full parsing)
print(f"Total entries: {logfile.entry_count}")

# Check if file contains specific content
if logfile.contains_error():
    print("Errors found!")

if logfile.contains(message="database", level="error"):
    print("Database errors found!")

# Monitor for new entries
for entry in logfile.watch():
    print(f"{entry.level}: {entry.message}")
```

### 3. Wait for Specific Events
```python
from logxy_log_parser import LogFile

logfile = LogFile("app.log")

# Wait for application to start
entry = logfile.wait_for_message("Application started", timeout=30)
if entry:
    print("Application is ready!")

# Wait for an error to occur
error = logfile.wait_for_error(timeout=60)
if error:
    print(f"Error detected: {error.message}")
```

---

## API Design

### Core Classes

#### `LogFile` - File Handle & Real-time Monitoring
```python
class LogFile:
    """Handle and monitor log files with real-time updates."""

    # Open and validate
    @classmethod
    def open(path: str | Path) -> LogFile | None

    # File state (real-time, updates as file grows)
    @property
    def entry_count(self) -> int       # Number of valid log entries
    @property
    def size(self) -> int              # File size in bytes
    @property
    def is_valid(self) -> bool         # Valid LogXPy log file

    def refresh(self) -> int           # Update and return new count

    # Search functions (fast, without full parsing)
    def contains(self, **criteria) -> bool
    def contains_message(self, text: str) -> bool
    def contains_error(self) -> bool
    def contains_level(self, level: str) -> bool

    def find_first(self, **criteria) -> LogEntry | None
    def find_last(self, **criteria) -> LogEntry | None
    def find_all(self, **criteria) -> list[LogEntry]

    def tail(self, n: int = 10) -> list[LogEntry]

    # Real-time monitoring
    def watch(self, interval: float = 0.1) -> Iterator[LogEntry]
    def follow(self, callback: Callable, interval: float = 0.1) -> None

    def wait_for(self, **criteria) -> LogEntry | None
    def wait_for_message(self, text: str, timeout: float) -> LogEntry | None
    def wait_for_error(self, timeout: float) -> LogEntry | None

    # Integration
    def get_parser(self) -> LogParser
```

#### `LogParser`
```python
class LogParser:
    """Parse LogXPy log files."""

    def __init__(self, source: str | Path | TextIO | list[dict])
    def parse(self) -> LogEntries
    def parse_stream(self) -> Iterator[LogEntry]

    # Task tree reconstruction
    def build_task_tree(self) -> TaskTree
    def get_task(self, task_uuid: str) -> Task
```

#### `LogEntries` (Collection)
```python
class LogEntries:
    """Collection of log entries with filtering and export."""

    def __len__(self) -> int
    def __iter__(self) -> Iterator[LogEntry]
    def __getitem__(self, key) -> LogEntry

    # Statistics
    def count(self) -> int
    def count_by_level(self) -> dict[str, int]
    def count_by_type(self) -> dict[str, int]
    def duration_stats(self) -> DurationStats

    # Export
    def to_json(self, file: str | Path) -> None
    def to_csv(self, file: str | Path) -> None
    def to_html(self, file: str | Path) -> None
    def to_markdown(self, file: str | Path) -> None
    def to_dataframe(self) -> pd.DataFrame

    # Display
    def pretty_print(self) -> None
    def tree_view(self) -> None
    def table_view(self) -> None
```

#### `LogFilter`
```python
class LogFilter:
    """Filter log entries by various criteria."""

    def __init__(self, entries: LogEntries)

    # Filters (chainable)
    def by_level(self, *levels: str) -> LogEntries
    def by_message(self, pattern: str, regex: bool = False) -> LogEntries
    def by_time_range(self, start: str | datetime, end: str | datetime) -> LogEntries
    def by_task_uuid(self, *uuids: str) -> LogEntries
    def by_action_type(self, *types: str) -> LogEntries
    def by_field(self, field: str, value: Any) -> LogEntries
    def by_duration(self, min: float = 0, max: float = float('inf')) -> LogEntries
    def by_nesting_level(self, min: int = 1, max: int = 99) -> LogEntries
    def with_traceback(self) -> LogEntries
    def failed_actions(self) -> LogEntries
    def slow_actions(self, threshold: float = 1.0) -> LogEntries

    # Combinations
    def and_(self, *filters: Callable) -> LogEntries
    def or_(self, *filters: Callable) -> LogEntries
    def not_(self, filter: Callable) -> LogEntries
```

#### `LogAnalyzer`
```python
class LogAnalyzer:
    """Perform advanced analysis on log entries."""

    def __init__(self, entries: LogEntries)

    # Performance analysis
    def slowest_actions(self, n: int = 10) -> list[ActionStat]
    def duration_by_action(self) -> dict[str, DurationStats]
    def time_distribution(self) -> TimeDistribution

    # Error analysis
    def error_summary(self) -> ErrorSummary
    def error_patterns(self) -> list[ErrorPattern]
    def failure_rate_by_action(self) -> dict[str, float]

    # Task analysis
    def task_duration_stats(self) -> dict[str, DurationStats]
    def deepest_nesting(self) -> int
    def orphans(self) -> LogEntries  # Logs without proper parent

    # Timeline analysis
    def timeline(self, interval: str = "1min") -> Timeline
    def peak_periods(self, n: int = 5) -> list[TimePeriod]

    # Generate report
    def generate_report(self, format: str = "html") -> str
```

#### `TaskTree`
```python
class TaskTree:
    """Hierarchical tree representation of task_uuid actions."""

    def __init__(self, root_task_uuid: str)
    def root(self) -> TaskNode
    def find_node(self, task_level: list[int]) -> TaskNode
    def to_dict(self) -> dict
    def visualize(self) -> str  # ASCII tree
```

---

## Usage Examples

### Basic Parsing and Filtering
```python
from logxy_log_parser import LogParser, LogFilter

parser = LogParser("application.log")
logs = parser.parse()

# Chain filters
result = (LogFilter(logs)
    .by_level("error", "warning")
    .by_time_range("2024-01-01", "2024-01-31")
    .by_message("database", regex=False))

result.to_html("january_db_issues.html")
```

### Performance Analysis
```python
from logxy_log_parser import LogParser, LogAnalyzer

parser = LogParser("app.log")
logs = parser.parse()

analyzer = LogAnalyzer(logs)

# Find slowest operations
for action in analyzer.slowest_actions(10):
    print(f"{action.type}: {action.duration:.3f}s")

# Duration distribution by action type
durations = analyzer.duration_by_action()
for action_type, stats in durations.items():
    print(f"{action_type}: avg={stats.mean:.3f}s, max={stats.max:.3f}s")

# Generate full performance report
analyzer.generate_report("performance_report.html")
```

### Error Analysis
```python
from logxy_log_parser import LogParser, LogFilter, LogAnalyzer

parser = LogParser("app.log")
logs = parser.parse()

# Get all errors with tracebacks
errors = LogFilter(logs).by_level("error").with_traceback()

# Analyze error patterns
analyzer = LogAnalyzer(errors)
summary = analyzer.error_summary()

print(f"Total errors: {summary.total_count}")
print(f"Unique error types: {summary.unique_types}")
print(f"Most common error: {summary.most_common}")

# Show failed actions
failed = LogFilter(logs).failed_actions()
for entry in failed:
    print(f"{entry.action_type} failed: {entry.reason}")
```

### Task Tracing
```python
from logxy_log_parser import LogParser

parser = LogParser("app.log")
task_tree = parser.build_task_tree()

# Get all logs for a specific transaction
task = parser.get_task("311585e4-1c52-4691-95e2-65f7295abe8a")

# Visualize the task hierarchy
print(task.tree_view())

# Get total task duration
print(f"Total duration: {task.duration:.3f}s")
```

### Export to DataFrame
```python
from logxy_log_parser import LogParser
import pandas as pd

parser = LogParser("app.log")
logs = parser.parse()

df = logs.to_dataframe()

# Now use pandas for analysis
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
errors_by_hour = df[df['message_type'] == 'loggerx:error'].groupby(
    df['timestamp'].dt.hour
).size()

errors_by_hour.plot(kind='bar')
```

---

## Command Line Interface (Future)

```bash
# Basic query
logxy-query app.log --level error --output errors.html

# Time range filter
logxy-query app.log --start "2024-01-01" --end "2024-01-31" --output january.json

# Performance report
logxy-analyze app.log --report performance --format html

# Task tracing
logxy-trace app.log --task-uuid 311585e4-1c52-4691-95e2-65f7295abe8a

# Slow operations
logxy-query app.log --min-duration 1.0 --sort duration --limit 20
```

---

## Dependencies

- **Required**: Python 3.12+
- **Optional**:
  - `pandas` - for DataFrame export
  - `rich` - for enhanced terminal output
  - `click` / `typer` - for CLI (future)

---

## Project Structure

```
logxy-log-parser/
├── logxy_log_parser/
│   ├── __init__.py
│   ├── core.py              # LogParser, LogEntry
│   ├── filter.py            # LogFilter
│   ├── analyzer.py          # LogAnalyzer
│   ├── export.py            # Export to various formats
│   ├── tree.py              # TaskTree, TaskNode
│   ├── types.py             # Type definitions
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

---

## Design Principles

1. **Easy to use** - Simple, fluent API
2. **Type safe** - Full type hints
3. **Fast** - Stream processing for large files
4. **Flexible** - Multiple export formats
5. **Extensible** - Easy to add custom filters and analyzers
