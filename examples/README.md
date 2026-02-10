# LogXPy Examples

Collection of examples demonstrating LogXPy features across all three packages:
- **logxpy** - Structured logging library
- **logxpy_cli_view** - Colored tree viewer for logs
- **logxy-log-parser** - Log parsing, analysis, and monitoring

## Directory Structure

```
examples/
├── README.md              # This file - main index
├── cli_view/              # CLI viewer examples
├── logxpy/                # Logging library examples
└── parser/                # Log parser examples
```

---

## CLI Viewer Examples (`cli_view/`)

**Command**: `logxpy-view`

### Numbered Examples (Recommended Learning Path)

| # | Example | Description |
|---|---------|-------------|
| 01 | [example-01-simple-task](cli_view/example-01-simple-task/) | Basic rendering + export + statistics |
| 02 | [example-02-nested-tasks](cli_view/example-02-nested-tasks/) | Nested tasks + task level analysis |
| 03 | [example-03-errors](cli_view/example-03-errors/) | Error handling + error analysis |
| 04 | [example-04-web-service](cli_view/example-04-web-service/) | HTTP logs + pattern extraction |
| 05 | [example-05-data-pipeline](cli_view/example-05-data-pipeline/) | ETL pipeline + time series |
| 06 | [example-06-filtering](cli_view/example-06-filtering/) | All 16 filter functions |
| 07 | [example-07-color-themes](cli_view/example-07-color-themes/) | ThemeMode enum + themes |
| 08 | [example-08-metrics](cli_view/example-08-metrics/) | Comprehensive metrics + analytics |
| 09 | [example-09-generating](cli_view/example-09-generating/) | Log generation + export |
| 10 | [example-10-deep-functions](cli_view/example-10-deep-functions/) | Deep function call tracking |
| 11 | [example-11-async-tasks](cli_view/example-11-async-tasks/) | Async task monitoring |

### Descriptive Examples (Advanced Topics)

| Example | Description |
|---------|-------------|
| [3level-nested-colored](cli_view/3level-nested-colored/) | Deep nesting with color visualization |
| [colored_tests](cli_view/colored_tests/) | Color rendering tests |
| [compact-color-demo](cli_view/compact-color-demo/) | Compact format color demo |
| [complete-example-01](cli_view/complete-example-01/) | Comprehensive reference (9 examples) |
| [comp-with-parser](cli_view/comp-with-parser/) | Integration with log parser |

---

## LogXPy Examples (`logxpy/`)

**Module**: `from logxpy import ...`

### Core Examples (01-10)

| # | File | Description |
|---|------|-------------|
| 01 | [01_simple_logging.py](logxpy/01_simple_logging.py) | Basic message logging |
| 02 | [02_decorators.py](logxpy/02_decorators.py) | Logging decorators |
| 03 | [03_context_scopes.py](logxpy/03_context_scopes.py) | Context management |
| 04 | [04_async_tasks.py](logxpy/04_async_tasks.py) | Async logging |
| 05 | [05_error_handling.py](logxpy/05_error_handling.py) | Exception handling |
| 06 | [06_data_types.py](logxpy/06_data_types.py) | Data type logging |
| 07 | [07_generators_iterators.py](logxpy/07_generators_iterators.py) | Generator logging |
| 08 | [08_tracing_opentelemetry.py](logxpy/08_tracing_opentelemetry.py) | OpenTelemetry integration |
| 09 | [09_configuration.py](logxpy/09_configuration.py) | Configuration options |
| 10 | [10_advanced_patterns.py](logxpy/10_advanced_patterns.py) | Advanced usage patterns |

### Real-World Examples (11-13)

| # | File | Description |
|---|------|-------------|
| 11 | [11_complex_ecommerce.py](logxpy/11_complex_ecommerce.py) | E-commerce system |
| 12 | [12_complex_banking.py](logxpy/12_complex_banking.py) | Banking system |
| 13 | [13_complex_data_pipeline.py](logxpy/13_complex_data_pipeline.py) | Data pipeline |

### Special Files

| File | Description |
|------|-------------|
| [xx_Color_Methods1.py](logxpy/xx_Color_Methods1.py) | Color method reference |
| [legacy/](logxpy/legacy/) | Legacy Eliot examples (12 files) |

---

## Parser Examples (`parser/`)

**Module**: `from logxy_log_parser import ...`

### Core Examples (01-09)

| # | File | Description |
|---|------|-------------|
| 01 | [01_basic.py](parser/01_basic.py) | Basic log parsing |
| 02 | [02_filtering.py](parser/02_filtering.py) | Log filtering |
| 03 | [03_analysis.py](parser/03_analysis.py) | Log analysis |

### Advanced Examples (10-16)

| # | File | Description |
|---|------|-------------|
| 10 | [10_check_presence.py](parser/10_check_presence.py) | Presence checking |
| 11 | [11_indexing_system.py](parser/11_indexing_system.py) | Fast indexing |
| 12 | [12_time_series_analysis.py](parser/12_time_series_analysis.py) | Time series analysis |
| 13 | [13_export_data.py](parser/13_export_data.py) | Data export formats |
| 14 | [14_realtime_monitoring.py](parser/14_realtime_monitoring.py) | Real-time monitoring |
| 15 | [15_aggregation.py](parser/15_aggregation.py) | Multi-file aggregation |
| 16 | [16_complete_reference.py](parser/16_complete_reference.py) | Complete API reference |

### Descriptive Examples

| File | Description |
|------|-------------|
| [basic_usage.py](parser/basic_usage.py) | Basic usage patterns |
| [error_analysis.py](parser/error_analysis.py) | Error analysis |
| [example_parser_usage.py](parser/example_parser_usage.py) | Parser usage |
| [filtering.py](parser/filtering.py) | More filtering |
| [monitoring.py](parser/monitoring.py) | Monitoring patterns |
| [performance.py](parser/performance.py) | Performance analysis |
| [task_tracing.py](parser/task_tracing.py) | Task tracing |

---

## Quick Start

### CLI Viewer

```bash
# View logs as a colored tree
logxpy-view examples/cli_view/example-01-simple-task/simple_task.log

# Show statistics
logxpy-view stats examples/cli_view/example-03-errors/with_errors.log

# Export to HTML
logxpy-view export -f html -o report.html examples/cli_view/example-04-web-service/web_service.log
```

### LogXPy Library

```bash
# Run examples
python examples/logxpy/01_simple_logging.py
python examples/logxpy/02_decorators.py
```

### Parser Library

```bash
# Run examples
python examples/parser/01_basic.py
python examples/parser/02_filtering.py
```

---

## Learning Path

### Beginner
1. `logxpy/01_simple_logging.py` - Basic logging
2. `cli_view/example-01-simple-task/` - View logs as trees
3. `parser/01_basic.py` - Parse log files

### Intermediate
1. `logxpy/03_context_scopes.py` - Context management
2. `cli_view/example-02-nested-tasks/` - Nested task visualization
3. `parser/02_filtering.py` - Advanced filtering

### Advanced
1. `logxpy/10_advanced_patterns.py` - Advanced patterns
2. `cli_view/complete-example-01/` - Comprehensive reference
3. `parser/16_complete_reference.py` - Full API reference

---

## See Also

- [Main Documentation](../docs/)
- [Common Module](../docs/COMMON_FINAL.md)
- [Python 3.12+ Features](../docs/PYTHON_312_FEATURES.md)
- [Migration Guide](../docs/MIGRATION.md)
