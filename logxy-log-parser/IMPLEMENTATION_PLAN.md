# LogXPy Log Parser - Implementation Plan

## Overview

This document outlines the implementation plan for the logxy-log-parser library, a Python library for parsing, analyzing, and querying LogXPy log files.

## Project Status

**Current Status**: Feature Complete, Production Ready

The logxy-log-parser library is fully implemented with all planned features:
- ✅ Core parsing functionality
- ✅ Filtering system
- ✅ Analysis capabilities
- ✅ Export to multiple formats
- ✅ Real-time monitoring
- ✅ Task tree reconstruction
- ✅ Simple one-line API

## Project Overview

Create a Python library `logxy-log-parser` for parsing, analyzing, and querying LogXPy log files with rich export formats (JSON, CSV, HTML, Markdown, terminal).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Application                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    logxy-log-parser API                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Parser  │  │  Filter  │  │ Analyzer │  │  Export  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LogXPy Log File                             │
│                    (JSON Lines Format)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Breakdown

### 1. Core Module (`core.py`)

**Classes:**
- `LogEntry` - Single log entry dataclass
- `LogParser` - Parse log files into `LogEntries`
- `LogFile` - Live log file monitoring and verification

**Key Methods:**
```python
class LogEntry:
    """Immutable log entry with typed accessors."""
    timestamp: float
    task_uuid: str
    task_level: tuple[int, ...]
    message_type: str
    message: str | None
    action_type: str | None
    action_status: str | None
    duration: float | None
    fields: dict[str, Any]

    @property
    def level(self) -> str: ...
    @property
    def depth(self) -> int: ...
    @property
    def is_error(self) -> bool: ...
    @property
    def is_action(self) -> bool: ...

class LogParser:
    """Parse LogXPy JSON log files."""

    def __init__(self, source: str | Path | TextIO | list[dict]):
        """Initialize with file path, file object, or raw data."""

    def parse(self) -> LogEntries:
        """Parse entire file into LogEntries collection."""

    def parse_stream(self) -> Iterator[LogEntry]:
        """Stream parse for large files (memory efficient)."""

class LogFile:
    """Handle and monitor a log file with real-time updates."""

    def __init__(self, path: str | Path):
        """Open and validate a log file. Raises LogFileError if invalid."""

    @classmethod
    def open(cls, path: str | Path) -> LogFile | None:
        """
        Open a log file, return None if file doesn't exist or is invalid.
        Safe alternative to constructor that doesn't raise exceptions.
        """

    @property
    def path(self) -> Path:
        """Get the file path."""

    @property
    def is_valid(self) -> bool:
        """Check if file is a valid LogXPy log file."""

    @property
    def size(self) -> int:
        """Get current file size in bytes."""

    @property
    def line_count(self) -> int:
        """Get current number of lines in the file."""

    @property
    def entry_count(self) -> int:
        """Get current number of valid log entries (real-time, updates as file grows)."""

    def refresh(self) -> int:
        """Refresh the file state and return new entry count. Call this to update entry_count for growing files."""

    def contains(self, **criteria) -> bool:
        """
        Check if log file contains entries matching criteria.

        Examples:
            contains(message="error")
            contains(level="error")
            contains(action_type="database.query")
            contains(message__contains="database")
            contains(user_id=123)
        """

    def contains_message(self, text: str, regex: bool = False) -> bool:
        """Check if file contains a specific message text."""

    def contains_error(self) -> bool:
        """Check if file contains any error level logs."""

    def find_first(self, **criteria) -> LogEntry | None:
        """Find first entry matching criteria."""

    def find_last(self, **criteria) -> LogEntry | None:
        """Find last entry matching criteria."""

    def tail(self, n: int = 10) -> list[LogEntry]:
        """Get last n entries from the file."""

    def follow(self, callback: Callable[[LogEntry], None], interval: float = 0.1):
        """
        Monitor file for new entries and call callback for each new log.
        Blocks until interrupted or file is closed.
        """

    def watch(self, interval: float = 0.1) -> Iterator[LogEntry]:
        """
        Yield new entries as they are written to the file.
        Use as: for entry in logfile.watch(): print(entry)
        """

    def get_parser(self) -> LogParser:
        """Get a LogParser for this file."""
```

---

### 2. Filter Module (`filter.py`)

**Classes:**
- `LogFilter` - Chainable filtering API
- `LogEntries` - Collection of log entries with filtering methods

**Key Methods:**
```python
class LogFilter:
    """Chainable filter builder."""
    def __init__(self, entries: LogEntries | list[LogEntry])

    # Level filters
    def by_level(self, *levels: str) -> LogEntries
    def debug(self) -> LogEntries
    def info(self) -> LogEntries
    def warning(self) -> LogEntries
    def error(self) -> LogEntries
    def critical(self) -> LogEntries

    # Content filters
    def by_message(self, pattern: str, regex: bool = False) -> LogEntries
    def by_action_type(self, *types: str) -> LogEntries
    def by_field(self, field: str, value: Any) -> LogEntries
    def by_field_contains(self, field: str, value: Any) -> LogEntries

    # Time filters
    def by_time_range(self, start: str | datetime, end: str | datetime) -> LogEntries
    def by_date(self, date: str) -> LogEntries
    def after(self, timestamp: str | datetime) -> LogEntries
    def before(self, timestamp: str | datetime) -> LogEntries

    # Task filters
    def by_task_uuid(self, *uuids: str) -> LogEntries
    def by_nesting_level(self, min: int = 1, max: int = 99) -> LogEntries

    # Performance filters
    def by_duration(self, min: float = 0, max: float = inf) -> LogEntries
    def slow_actions(self, threshold: float = 1.0) -> LogEntries
    def fast_actions(self, threshold: float = 0.001) -> LogEntries

    # Status filters
    def with_traceback(self) -> LogEntries
    def failed_actions(self) -> LogEntries
    def succeeded_actions(self) -> LogEntries
    def started_actions(self) -> LogEntries

class LogEntries:
    """Collection of log entries."""
    def __len__(self) -> int
    def __iter__(self) -> Iterator[LogEntry]
    def __getitem__(self, index: int) -> LogEntry

    # Filtering (delegates to LogFilter)
    def filter(self, predicate: Callable[[LogEntry], bool]) -> LogEntries
    def sort(self, key: str, reverse: bool = False) -> LogEntries
    def limit(self, n: int) -> LogEntries
    def unique(self, key: str | None = None) -> LogEntries

    # Aggregation
    def count_by_level(self) -> dict[str, int]
    def count_by_type(self) -> dict[str, int]
    def group_by(self, key: str) -> dict[str, LogEntries]

    # Export (delegates to export module)
    def to_json(self, file: str | Path) -> None
    def to_csv(self, file: str | Path) -> None
    def to_html(self, file: str | Path) -> None
    def to_markdown(self, file: str | Path) -> None
    def to_dataframe(self) -> pd.DataFrame
```

---

### 3. Analyzer Module (`analyzer.py`)

**Classes:**
- `LogAnalyzer` - Statistical and pattern analysis
- `DurationStats` - Duration statistics
- `ErrorSummary` - Error analysis summary
- `ActionStat` - Individual action statistic

**Key Methods:**
```python
class LogAnalyzer:
    """Advanced log analysis."""
    def __init__(self, entries: LogEntries)

    # Performance
    def slowest_actions(self, n: int = 10) -> list[ActionStat]
    def fastest_actions(self, n: int = 10) -> list[ActionStat]
    def duration_by_action(self) -> dict[str, DurationStats]
    def percentile_durations(self, percentile: float = 95) -> list[ActionStat]

    # Errors
    def error_summary(self) -> ErrorSummary
    def error_patterns(self) -> list[ErrorPattern]
    def failure_rate_by_action(self) -> dict[str, float]
    def most_common_errors(self, n: int = 10) -> list[tuple[str, int]]

    # Task analysis
    def task_duration_stats(self) -> dict[str, DurationStats]
    def deepest_nesting(self) -> int
    def widest_tasks(self) -> list[tuple[str, int]]  # (task_uuid, child_count)
    def orphans(self) -> LogEntries

    # Timeline
    def timeline(self, interval: str = "1min") -> Timeline
    def peak_periods(self, n: int = 5) -> list[TimePeriod]
    def quiet_periods(self, n: int = 5) -> list[TimePeriod]

    # Report generation
    def generate_report(self, format: str = "html") -> str

@dataclass
class DurationStats:
    count: int
    total: float
    mean: float
    median: float
    min: float
    max: float
    std: float
    p25: float
    p75: float
    p95: float
    p99: float

@dataclass
class ErrorSummary:
    total_count: int
    unique_types: int
    most_common: tuple[str, int]
    by_level: dict[str, int]
    by_action: dict[str, int]

@dataclass
class ActionStat:
    action_type: str
    count: int
    total_duration: float
    mean_duration: float
    min_duration: float
    max_duration: float
```

---

### 4. Export Module (`export.py`)

**Classes:**
- `JsonExporter`
- `CsvExporter`
- `HtmlExporter`
- `MarkdownExporter`
- `DataFrameExporter`

**Key Methods:**
```python
class JsonExporter:
    def export(self, entries: LogEntries, file: str | Path, pretty: bool = True) -> None

class CsvExporter:
    def export(self, entries: LogEntries, file: str | Path, flatten: bool = True) -> None

class HtmlExporter:
    def export(self, entries: LogEntries, file: str | Path,
               template: str | None = None) -> None
    def export_report(self, analysis: LogAnalysis, file: str | Path) -> None

class MarkdownExporter:
    def export(self, entries: LogEntries, file: str | Path) -> None
    def export_table(self, entries: LogEntries, file: str | Path) -> None

class DataFrameExporter:
    def export(self, entries: LogEntries) -> pd.DataFrame
```

---

### 5. Tree Module (`tree.py`)

**Classes:**
- `TaskTree` - Hierarchical task representation
- `TaskNode` - Single node in task tree

**Key Methods:**
```python
class TaskNode:
    """Node in task tree."""
    task_uuid: str
    task_level: tuple[int, ...]
    action_type: str | None
    status: str | None
    start_time: float | None
    end_time: float | None
    duration: float | None
    children: list[TaskNode]
    messages: list[LogEntry]

    @property
    def depth(self) -> int
    @property
    def is_complete(self) -> bool
    @property
    def total_duration(self) -> float

class TaskTree:
    """Hierarchical tree of actions for a task_uuid."""
    def __init__(self, root: TaskNode)

    @classmethod
    def from_entries(cls, entries: list[LogEntry], task_uuid: str) -> TaskTree

    def root(self) -> TaskNode
    def find_node(self, task_level: tuple[int, ...]) -> TaskNode | None
    def to_dict(self) -> dict
    def visualize(self, format: str = "ascii") -> str
    def get_execution_path(self) -> list[str]
```

---

### 6. Types Module (`types.py`)

**Type Definitions:**
```python
from __future__ import annotations
from typing import TypeAlias
from datetime import datetime

# Core types
LogDict: TypeAlias = dict[str, Any]
TaskLevel: TypeAlias = tuple[int, ...]

# Log level enum (matches LogXPy)
class Level(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    NOTE = "note"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# Action status enum
class ActionStatus(str, Enum):
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

# Message type patterns
MESSAGE_TYPE_PREFIX = "loggerx:"
```

---

### 7. Utils Module (`utils.py`)

**Helper Functions:**
```python
def parse_timestamp(ts: float) -> datetime: ...
def format_timestamp(ts: float, fmt: str = "%Y-%m-%d %H:%M:%S") -> str: ...
def parse_duration(seconds: float) -> str:  # "1h 23m 45.123s"
def level_from_message_type(message_type: str) -> Level: ...
def extract_task_uuid(entries: list[LogEntry]) -> set[str]: ...
def merge_fields(*dicts: dict) -> dict: ...
```

---

### 8. Monitor Module (`monitor.py`)

**Classes:**
- `LogFile` - Handle and monitor log files with real-time updates
- `LogFileError` - Exception for invalid log files

**Key Methods:**
```python
class LogFile:
    """Handle and monitor a log file with real-time updates."""

    def __init__(self, path: str | Path):
        """Open and validate a log file. Raises LogFileError if invalid."""

    @classmethod
    def open(cls, path: str | Path) -> LogFile | None:
        """Safe open - returns None if invalid instead of raising."""

    # File state
    @property
    def path(self) -> Path: ...
    @property
    def is_valid(self) -> bool: ...
    @property
    def size(self) -> int: ...  # File size in bytes
    @property
    def line_count(self) -> int: ...
    @property
    def entry_count(self) -> int: ...  # Real-time count of valid log entries

    def refresh(self) -> int:
        """Update file state and return new entry count."""

    # Search functions
    def contains(self, **criteria) -> bool:
        """
        Check if log contains entries matching criteria.

        Supports:
        - contains(message="error")           # exact match
        - contains(message__contains="db")    # substring
        - contains(level="error")             # log level
        - contains(action_type="db.query")    # action type
        - contains(user_id=123)               # custom field
        - contains(timestamp__gt=1738332000)  # comparisons: gt, lt, gte, lte
        """

    def contains_message(self, text: str, regex: bool = False) -> bool:
        """Check if file contains specific message text."""

    def contains_error(self) -> bool:
        """Quick check if file has any errors."""

    def contains_level(self, level: str) -> bool:
        """Check if file has specific log level."""

    def find_first(self, **criteria) -> LogEntry | None:
        """Find first entry matching criteria."""

    def find_last(self, **criteria) -> LogEntry | None:
        """Find last entry matching criteria."""

    def find_all(self, **criteria) -> list[LogEntry]:
        """Find all entries matching criteria."""

    def tail(self, n: int = 10) -> list[LogEntry]:
        """Get last n entries from file."""

    # Real-time monitoring
    def follow(self, callback: Callable[[LogEntry], None], interval: float = 0.1):
        """
        Monitor file for new entries. Callback receives each new log.
        Blocks until interrupted.

        Example:
            logfile.follow(lambda entry: print(entry.message))
        """

    def watch(self, interval: float = 0.1) -> Iterator[LogEntry]:
        """
        Yield new entries as they appear.

        Example:
            for entry in logfile.watch():
                if entry.level == "error":
                    print(f"ERROR: {entry.message}")
        """

    def wait_for(self, **criteria) -> LogEntry | None:
        """
        Wait for an entry matching criteria to appear.
        Returns the entry when found, or None if timeout.
        """

    def wait_for_message(self, text: str, timeout: float = 30.0) -> LogEntry | None:
        """Wait for a specific message to appear."""

    def wait_for_error(self, timeout: float = 30.0) -> LogEntry | None:
        """Wait for an error to appear."""

    # Integration
    def get_parser(self) -> LogParser:
        """Get a LogParser for this file."""

    def to_entries(self) -> LogEntries:
        """Load all entries as LogEntries collection."""
```

---

## File Structure

```
logxy-log-parser/
├── logxy_log_parser/
│   ├── __init__.py           # Public API exports
│   ├── core.py               # LogEntry, LogParser
│   ├── monitor.py            # LogFile (NEW - real-time monitoring)
│   ├── filter.py             # LogFilter, LogEntries
│   ├── analyzer.py           # LogAnalyzer, statistics
│   ├── export.py             # All exporters
│   ├── tree.py               # TaskTree, TaskNode
│   ├── types.py              # Type definitions
│   └── utils.py              # Helper functions
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # pytest fixtures
│   ├── test_core.py          # Parser tests
│   ├── test_monitor.py       # LogFile tests (NEW)
│   ├── test_filter.py        # Filter tests
│   ├── test_analyzer.py      # Analyzer tests
│   ├── test_export.py        # Export tests
│   ├── test_tree.py          # Tree tests
│   └── fixtures/
│       ├── sample.log        # Sample LogXPy log file
│       ├── errors.log        # Sample with errors
│       └── complex.log       # Complex nested log
│
├── examples/
│   ├── basic_usage.py        # Getting started
│   ├── monitoring.py         # LogFile and real-time monitoring (NEW)
│   ├── filtering.py          # Filter examples
│   ├── performance.py        # Performance analysis
│   ├── error_analysis.py     # Error tracking
│   └── task_tracing.py       # Task tree examples
│
├── docs/
│   ├── api.md                # API reference
│   └── examples.md           # More examples
│
├── pyproject.toml            # Package config
├── README.md                 # User documentation
└── IMPLEMENTATION_PLAN.md    # This file
```

---

## LogFile Usage Examples

### Example 1: Open and Validate Log File
```python
from logxy_log_parser import LogFile

# Safe open - returns None if file doesn't exist or is invalid
logfile = LogFile.open("app.log")

if logfile is None:
    print("File not found or invalid")
    return

print(f"File: {logfile.path}")
print(f"Valid LogXPy log: {logfile.is_valid}")
print(f"Size: {logfile.size} bytes")
print(f"Entries: {logfile.entry_count}")
```

### Example 2: Real-time Entry Count
```python
from logxy_log_parser import LogFile
import time

logfile = LogFile("app.log")

# Get current count
print(f"Current entries: {logfile.entry_count}")

# Simulate waiting for logs to be written
time.sleep(5)

# Refresh to get updated count
new_count = logfile.refresh()
print(f"Updated entries: {new_count}")
```

### Example 3: Check if Log Contains Specific Content
```python
from logxy_log_parser import LogFile

logfile = LogFile("app.log")

# Check for errors
if logfile.contains_error():
    print("Log file contains errors!")

# Check for specific message
if logfile.contains_message("database connection"):
    print("Database connection issue found")

# Check for specific log level
if logfile.contains_level("critical"):
    print("Critical issues present!")

# Check with custom criteria
if logfile.contains(action_type="payment.process"):
    print("Payment processing logs found")

if logfile.contains(user_id=12345):
    print("User 12345 activity found")

# Substring search
if logfile.contains(message__contains="timeout"):
    print("Timeout messages found")

# Comparison searches
if logfile.contains(timestamp__gt=1738332000):
    print("Logs after timestamp found")
```

### Example 4: Find Specific Entries
```python
from logxy_log_parser import LogFile

logfile = LogFile("app.log")

# Find first error
first_error = logfile.find_first(level="error")
if first_error:
    print(f"First error: {first_error.message}")

# Find last entry for specific user
last_user = logfile.find_last(user_id=12345)
if last_user:
    print(f"Last activity: {last_user.message}")

# Find all database query entries
db_entries = logfile.find_all(action_type="database.query")
print(f"Found {len(db_entries)} database queries")

# Get last 10 entries (tail)
recent = logfile.tail(10)
for entry in recent:
    print(f"{entry.timestamp}: {entry.message}")
```

### Example 5: Real-time Monitoring (Follow)
```python
from logxy_log_parser import LogFile

logfile = LogFile("app.log")

# Define callback for new entries
def on_new_log(entry):
    if entry.level == "error":
        print(f"🔴 ERROR: {entry.message}")
    elif entry.level == "warning":
        print(f"🟡 WARNING: {entry.message}")
    else:
        print(f"📌 {entry.message}")

# Monitor file - blocks until Ctrl+C
try:
    logfile.follow(on_new_log, interval=0.5)
except KeyboardInterrupt:
    print("\nStopped monitoring")
```

### Example 6: Real-time Monitoring (Watch/Iterator)
```python
from logxy_log_parser import LogFile

logfile = LogFile("app.log")

# Use as iterator - more Pythonic
print("Monitoring for errors...")
try:
    for entry in logfile.watch(interval=0.5):
        if entry.level == "error":
            print(f"[{entry.timestamp}] {entry.message}")

            # Can break on condition
            if "critical" in entry.message.lower():
                print("Critical error found, stopping!")
                break
except KeyboardInterrupt:
    print("\nStopped monitoring")
```

### Example 7: Wait for Specific Events
```python
from logxy_log_parser import LogFile

logfile = LogFile("app.log")

# Wait for specific message
entry = logfile.wait_for_message("Application started", timeout=30.0)
if entry:
    print("Application has started!")
else:
    print("Timeout waiting for start message")

# Wait for any error
error_entry = logfile.wait_for_error(timeout=60.0)
if error_entry:
    print(f"Error detected: {error_entry.message}")

# Wait for specific criteria
entry = logfile.wait_for(
    action_type="payment.process",
    action_status="succeeded",
    timeout=120.0
)
if entry:
    print("Payment completed successfully!")
```

### Example 8: Integration with Parser
```python
from logxy_log_parser import LogFile, LogFilter

# Use LogFile to validate and monitor
logfile = LogFile("app.log")

if not logfile.is_valid:
    print("Invalid log file")
    return

# Get full parser for analysis
parser = logfile.get_parser()
logs = parser.parse()

# Use all filtering capabilities
errors = LogFilter(logs).by_level("error")
print(f"Found {len(errors)} errors")

# Export filtered results
errors.to_html("errors.html")
```

### Example 9: Monitoring Dashboard
```python
from logxy_log_parser import LogFile
from datetime import datetime

def print_dashboard(logfile: LogFile):
    """Print a simple monitoring dashboard."""
    logfile.refresh()

    print(f"\n{'='*60}")
    print(f"Log Monitor: {logfile.path}")
    print(f"{'='*60}")
    print(f"Total Entries: {logfile.entry_count:,}")
    print(f"File Size: {logfile.size / 1024:.1f} KB")
    print(f"Has Errors: {logfile.contains_error()}")
    print(f"Last Entry: {logfile.tail(1)[0].message if logfile.entry_count > 0 else 'None'}")
    print(f"{'='*60}\n")

logfile = LogFile("app.log")

# Update dashboard every 5 seconds
import time
try:
    while True:
        print_dashboard(logfile)
        time.sleep(5)
except KeyboardInterrupt:
    print("Monitoring stopped")
```

---

## Implementation Phases

### Phase 1: Core Foundation (Week 1)
- [ ] Create project structure
- [ ] Implement `types.py` - type definitions
- [ ] Implement `LogEntry` dataclass
- [ ] Implement `LogParser.parse()` for basic JSON parsing
- [ ] Implement `LogFile` for file handling and real-time monitoring **(NEW)**
- [ ] Basic tests for parsing

### Phase 2: Collection & Filtering (Week 1-2)
- [ ] Implement `LogEntries` collection
- [ ] Implement `LogFilter` class
- [ ] Implement all filter methods (by_level, by_message, etc.)
- [ ] Implement chainable filters
- [ ] Filter tests

### Phase 3: Export (Week 2)
- [ ] JSON exporter
- [ ] CSV exporter
- [ ] HTML exporter (with template)
- [ ] Markdown exporter
- [ ] DataFrame exporter (optional)
- [ ] Export tests

### Phase 4: Analysis (Week 3)
- [ ] Implement `LogAnalyzer`
- [ ] Performance analysis methods
- [ ] Error analysis methods
- [ ] Task analysis methods
- [ ] Timeline analysis
- [ ] Analyzer tests

### Phase 5: Task Tree (Week 3-4)
- [ ] Implement `TaskNode`
- [ ] Implement `TaskTree` builder
- [ ] Tree visualization
- [ ] Tree tests

### Phase 6: Polish & Documentation (Week 4)
- [ ] Complete examples
- [ ] API documentation
- [ ] Performance optimization (streaming)
- [ ] Integration with LogXPy

---

## Key Design Decisions

### 1. Immutable LogEntry
- LogEntry is a frozen dataclass (immutable)
- Thread-safe for parallel processing
- Easy hashing for deduplication

### 2. Lazy Evaluation
- Filters return new `LogEntries` views (not copies)
- Actual filtering happens on iteration
- Enables efficient chaining

### 3. Streaming Support
- `parse_stream()` for large files
- Generator-based processing
- Memory-efficient for multi-GB logs

### 4. Optional Pandas
- DataFrame export is opt-in
- Falls back gracefully if pandas not installed
- Core library has minimal dependencies

### 5. Type Safety
- Full type hints throughout
- Mypy strict mode compatible
- Runtime validation where appropriate

---

## Testing Strategy

### Unit Tests
- Each module has corresponding test file
- Test edge cases (empty logs, malformed JSON, etc.)
- Property-based testing for filters

### Integration Tests
- Test with real LogXPy log files
- Test filter chains
- Test export/import round trips

### Fixtures
- `sample.log` - Basic logs (all levels)
- `errors.log` - Contains errors and failures
- `complex.log` - Deep nesting, many entries

---

## Dependencies

### Required
```
python = "^3.12"
```

### Optional/Dev
```
pandas = { version = "^2.0", optional = true }
rich = { version = "^13.0", optional = true }
pytest = "^7.0"
pytest-cov = "^4.0"
mypy = "^1.0"
ruff = "^0.1"
```

---

## Future Enhancements

### CLI Tool (Phase 2)
```bash
logxy-query app.log --level error --output errors.html
logxy-analyze app.log --report performance
```

### Real-time Monitoring
- Tail log files and display updates
- WebSocket support for web dashboards

### Cloud Integration
- Direct S3/GCS log reading
- Integration with log aggregators

### Machine Learning
- Anomaly detection
- Predictive error analysis
