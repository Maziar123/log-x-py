# LogXPy Log Parser - Folder Structure

## Project Directory Layout

```
logxy_log_parser/
│
├── __init__.py                    # Thin shim → src/
├── src/                           # Main package directory
│   ├── __init__.py                # Public API exports
│   ├── simple.py                  # One-line API functions
│   ├── core.py                    # LogEntry, LogParser
│   ├── monitor.py                 # LogFile for real-time monitoring
│   ├── filter.py                  # LogFilter, LogEntries
│   ├── analyzer.py                # LogAnalyzer, statistics
│   ├── export.py                  # Export to JSON/CSV/HTML/MD/DataFrame
│   ├── tree.py                    # TaskTree, TaskNode
│   ├── types.py                   # Type definitions (Level, ActionStatus)
│   └── utils.py                   # Helper functions
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # pytest fixtures
│   ├── test_core.py               # Parser tests
│   ├── test_monitor.py            # LogFile tests
│   ├── test_filter.py             # Filter tests
│   ├── test_analyzer.py           # Analyzer tests
│   ├── test_export.py             # Export tests
│   ├── test_tree.py               # Tree tests
│   └── fixtures/                  # Test data
│       ├── sample.log             # Sample LogXPy log (all levels)
│       ├── errors.log             # Sample with errors
│       └── complex.log            # Complex nested log
│
├── examples/                      # Usage examples
│   ├── basic_usage.py             # Getting started
│   ├── monitoring.py              # LogFile and real-time monitoring
│   ├── filtering.py               # Filter examples
│   ├── performance.py             # Performance analysis
│   ├── error_analysis.py          # Error tracking
│   └── task_tracing.py            # Task tree examples
│
├── docs/                          # Additional documentation
│   ├── api.md                     # API reference
│   └── examples.md                # More examples
│
├── pyproject.toml                 # Package configuration
├── README.md                      # User documentation
├── IMPLEMENTATION_PLAN.md         # Implementation plan
└── FOLDER_STRUCTURE.md            # This file
```

## File Descriptions

### Core Package (`logxy_log_parser/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Public API exports, version info, optional dependency handling |
| `types.py` | Type aliases, enums (Level, ActionStatus) |
| `core.py` | `LogEntry` dataclass, `LogParser` class |
| `filter.py` | `LogFilter` builder, `LogEntries` collection |
| `analyzer.py` | `LogAnalyzer`, stats classes (`DurationStats`, `ErrorSummary`) |
| `export.py` | All exporter classes (JSON, CSV, HTML, Markdown, DataFrame) |
| `tree.py` | `TaskNode`, `TaskTree` for hierarchical task representation |
| `utils.py` | Helper functions (timestamp formatting, duration parsing) |

### Tests (`tests/`)

| File | Purpose |
|------|---------|
| `conftest.py` | pytest fixtures for sample logs |
| `test_core.py` | Test log parsing, LogEntry properties |
| `test_filter.py` | Test all filter methods, chaining |
| `test_analyzer.py` | Test analysis functions, statistics |
| `test_export.py` | Test export to all formats |
| `test_tree.py` | Test task tree building, visualization |
| `fixtures/` | Sample log files for testing |

### Examples (`examples/`)

Each file demonstrates specific functionality:

- `basic_usage.py` - Parsing, basic filtering, export
- `filtering.py` - All filter types, chaining
- `performance.py` - Duration analysis, slowest actions
- `error_analysis.py` - Error summary, patterns, failed actions
- `task_tracing.py` - Task tree, execution paths

## Module Dependencies

```
__init__.py
    ├── types.py
    ├── core.py
    │   └── types.py
    ├── filter.py
    │   └── core.py
    ├── analyzer.py
    │   ├── core.py
    │   └── filter.py
    ├── export.py
    │   ├── core.py
    │   └── filter.py
    └── tree.py
        └── core.py
```
