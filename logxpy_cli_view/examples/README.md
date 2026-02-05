# EliotTree2 Examples

Collection of examples demonstrating logxpy-tree2 features, including new export, statistics, filtering, and pattern extraction capabilities.

## 📁 Directory Structure

```
examples/
├── example-01-simple-task/       # Basic rendering + export + stats
├── example-02-nested-tasks/      # Nested tasks + task level analysis
├── example-03-errors/            # Error handling + error analysis
├── example-04-web-service/       # HTTP logs + pattern extraction
├── example-05-data-pipeline/     # ETL pipeline + time series
├── example-06-filtering/         # All 16 filter functions
├── example-07-color-themes/      # ThemeMode enum + themes
├── example-08-metrics/           # Comprehensive metrics + analytics
├── example-09-generating/        # Log generation + export
├── python_samples/               # Additional Python API examples
└── README.md
```

## 🚀 Quick Start

### Using CLI

```bash
# View any log file
logxpy-tree2 examples/example-01-simple-task/simple_task.log

# Show statistics
logxpy-tree2 stats examples/example-03-errors/with_errors.log

# Export to HTML
logxpy-tree2 export -f html -o report.html examples/example-04-web-service/web_service.log

# Watch logs in real-time
logxpy-tree2 tail -f examples/example-01-simple-task/simple_task.log

# Live dashboard
logxpy-tree2 tail --dashboard examples/example-01-simple-task/simple_task.log
```

### Using Python

```bash
# Run any example
cd examples/example-01-simple-task
python main.py

cd examples/example-06-filtering
python main.py
```

## 📖 Examples Overview

### 01 - Simple Task
**Basic rendering with export and statistics**
- Tree rendering
- Statistics calculation
- Export to JSON, CSV, HTML
- **New**: `calculate_statistics()`, `export_tasks()`

### 02 - Nested Tasks
**Hierarchical tasks with level analysis**
- Parent-child relationships
- Task depth analysis
- Filter by task level
- **New**: `filter_by_task_level()`, task depth distribution

### 03 - Errors
**Error handling and analysis**
- Error highlighting
- Error statistics
- Filter by status
- **New**: `filter_by_action_status()`, `filter_by_keyword()`

### 04 - Web Service
**HTTP request logging with pattern extraction**
- Request lifecycle
- URL/IP extraction
- Log classification
- **New**: `extract_urls()`, `extract_ips()`, `create_common_classifier()`

### 05 - Data Pipeline
**ETL pipeline with time series**
- Multi-stage processing
- Time series analysis
- Export to all formats
- **New**: `create_time_series()`, duration stats

### 06 - Filtering
**All 16 filter functions demonstrated**
- Status, action type, duration filters
- Keyword search
- Field existence
- Combined filters (AND, OR, NOT)
- **New**: All filter functions and combinators

### 07 - Color Themes
**ThemeMode enum and theme options**
- Dark/Light/Auto themes
- ASCII mode
- No color mode
- **New**: `ThemeMode` enum

### 08 - Metrics
**Comprehensive analytics**
- Duration statistics
- Error analysis
- Time series
- Top N slowest tasks
- **New**: `print_statistics()`, `create_time_series()`

### 09 - Generating
**Log generation with modern features**
- Programmatic log creation
- Statistics on generated logs
- Export to HTML
- **New**: Full integration with all features

## 🆕 New Features Demonstrated

### Export Formats
```bash
# Export to JSON
logxpy-tree2 export -f json -o out.json logfile.log

# Export to CSV
logxpy-tree2 export -f csv -o out.csv logfile.log

# Export to HTML (interactive table)
logxpy-tree2 export -f html -o out.html logfile.log

# Export to logfmt
logxpy-tree2 export -f logfmt -o out.logfmt logfile.log
```

### Statistics Command
```bash
# Show statistics
logxpy-tree2 stats logfile.log

# Export statistics to JSON
logxpy-tree2 stats -o stats.json logfile.log
```

### Advanced Filtering
```bash
# Filter by status
logxpy-tree2 --status failed logfile.log

# Filter by duration
logxpy-tree2 --min-duration 5.0 logfile.log

# Filter by regex pattern
logxpy-tree2 --action-type "http:.*" --action-type-regex logfile.log

# Filter by keyword
logxpy-tree2 --keyword timeout logfile.log

# Combined filters
logxpy-tree2 --status failed --min-duration 1.0 logfile.log
```

### Live Tail
```bash
# Follow mode
logxpy-tree2 tail -f logfile.log

# Live dashboard
logxpy-tree2 tail --dashboard logfile.log

# Aggregated statistics
logxpy-tree2 tail --aggregate --interval 10 logfile.log
```

## 🐍 Python API Examples

### Basic Rendering
```python
from logxpy_cli_view import render_tasks, tasks_from_iterable

with open('logfile.log') as f:
    logs = [line.strip() for line in f]

tasks = tasks_from_iterable(logs)
render_tasks(tasks)
```

### Statistics
```python
from logxpy_cli_view import calculate_statistics, print_statistics
import json

with open('logfile.log') as f:
    logs = [json.loads(line) for line in f]

stats = calculate_statistics(logs)
print_statistics(stats)
print(f"Success rate: {stats.success_rate:.1f}%")
```

### Export
```python
from logxpy_cli_view import export_tasks

tasks = tasks_from_iterable(logs)

# Export to HTML
export_tasks(tasks, "report.html", format="html", title="My Report")

# Export to CSV
export_tasks(tasks, "data.csv", format="csv")
```

### Filtering
```python
from logxpy_cli_view import (
    filter_by_action_status,
    filter_by_duration,
    combine_filters_and,
)

# Simple filter
failed = filter(filter_by_action_status('failed'), logs)

# Combined filters
slow_failed = combine_filters_and(
    filter_by_action_status('failed'),
    filter_by_duration(min_seconds=5.0),
)
filtered = list(filter(slow_failed, logs))
```

### Pattern Extraction
```python
from logxpy_cli_view import extract_urls, extract_ips, create_common_classifier

# Extract URLs
urls = extract_urls(json.dumps(logs))

# Extract IPs
ips = extract_ips(json.dumps(logs))

# Classify logs
classifier = create_common_classifier()
for log in logs:
    categories = classifier.classify(json.dumps(log))
    print(categories)  # ['http_request', 'database']
```

### Live Tail
```python
from logxpy_cli_view import tail_logs, LiveDashboard

# Simple tail
tail_logs("app.log", follow=True)

# Dashboard
dashboard = LiveDashboard("app.log", refresh_rate=1.0)
dashboard.run()
```

## 🎯 Advanced Examples

See `python_samples/` for additional examples:
- `new_features_demo.py` - Comprehensive demo of all new features
- `advanced_filtering.py` - All 16 filter functions
- `log_analysis.py` - Statistical analysis patterns

## 📊 Feature Comparison

| Feature | CLI | Python API |
|---------|-----|------------|
| Tree Rendering | ✅ | ✅ |
| Statistics | `stats` | `calculate_statistics()` |
| Export | `export` | `export_tasks()` |
| Live Tail | `tail` | `tail_logs()` |
| Dashboard | `tail --dashboard` | `LiveDashboard()` |
| Filtering | `--status`, `--keyword`, etc | Filter functions |
| Pattern Extraction | - | `extract_urls()`, etc |

## 🔗 Additional Resources

- [Main Documentation](../README.md)
- [Refactoring Guide](../REFACTORING.md)
- [Features Guide](../FEATURES.md)
