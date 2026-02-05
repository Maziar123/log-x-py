# New Filtering Features

This document describes the new advanced filtering features added to logxpy_cli_view.

## New Filter Functions

### 1. filter_by_action_status(status)
Filter tasks by their action status.

```python
from logxpy_cli_view import filter_by_action_status

# Only failed tasks
filter_fn = filter_by_action_status('failed')

# Only succeeded tasks
filter_fn = filter_by_action_status('succeeded')
```

### 2. filter_by_action_type(pattern, regex=False)
Filter tasks by action type. Supports exact match or regex pattern.

```python
from logxpy_cli_view import filter_by_action_type

# Exact match
filter_fn = filter_by_action_type('app:http:request')

# Regex match
filter_fn = filter_by_action_type(r'app:http:.*', regex=True)
```

### 3. filter_by_duration(min_seconds=None, max_seconds=None)
Filter tasks by their duration.

```python
from logxpy_cli_view import filter_by_duration

# Slow tasks (> 5 seconds)
filter_fn = filter_by_duration(min_seconds=5.0)

# Fast tasks (< 100ms)
filter_fn = filter_by_duration(max_seconds=0.1)

# Tasks within a range
filter_fn = filter_by_duration(min_seconds=1.0, max_seconds=10.0)
```

### 4. filter_by_relative_time(lookback)
Filter tasks within a relative time window from now.

```python
from datetime import timedelta
from logxpy_cli_view import filter_by_relative_time

# Last 5 minutes
filter_fn = filter_by_relative_time(timedelta(minutes=5))

# Last hour
filter_fn = filter_by_relative_time(timedelta(hours=1))
```

### 5. filter_by_field_exists(field_path)
Filter tasks that have a specific field (supports nested paths).

```python
from logxpy_cli_view import filter_by_field_exists

# Tasks with error field
filter_fn = filter_by_field_exists('error')

# Tasks with nested metadata
filter_fn = filter_by_field_exists('metadata.request_id')
```

### 6. filter_by_keyword(keyword, case_sensitive=False)
Search for a keyword in any field (deep search through nested dicts).

```python
from logxpy_cli_view import filter_by_keyword

# Case-insensitive search
filter_fn = filter_by_keyword('timeout')

# Case-sensitive search
filter_fn = filter_by_keyword('ERROR', case_sensitive=True)
```

### 7. filter_by_task_level(min_level=None, max_level=None)
Filter tasks by their depth level in the task tree.

```python
from logxpy_cli_view import filter_by_task_level

# Top-level tasks only
filter_fn = filter_by_task_level(max_level=1)

# Nested tasks (level 2 or deeper)
filter_fn = filter_by_task_level(min_level=2)
```

### 8. filter_sample(every_n)
Sample every Nth task for statistical analysis.

```python
from logxpy_cli_view import filter_sample

# Sample 10% of tasks
filter_fn = filter_sample(10)
```

### 9. combine_filters_not(filter_fn)
Negate a filter (logical NOT).

```python
from logxpy_cli_view import combine_filters_not, filter_by_action_status

# All non-failed tasks
filter_fn = combine_filters_not(filter_by_action_status('failed'))
```

## CLI Usage

All new filters are available as command-line arguments:

```bash
# Filter by status
logxpy-tree2 --status failed logfile.json

# Filter by action type (exact)
logxpy-tree2 --action-type "app:http:request" logfile.json

# Filter by action type (regex)
logxpy-tree2 --action-type "http:.*" --action-type-regex logfile.json

# Filter by duration
logxpy-tree2 --min-duration 5.0 logfile.json
logxpy-tree2 --max-duration 0.1 logfile.json

# Filter by field existence
logxpy-tree2 --has-field error logfile.json
logxpy-tree2 --has-field metadata.user_id logfile.json

# Filter by keyword
logxpy-tree2 --keyword timeout logfile.json

# Filter by task level
logxpy-tree2 --max-level 1 logfile.json  # Top-level only
logxpy-tree2 --min-level 2 logfile.json  # Nested only

# Combined filters
logxpy-tree2 --status failed --min-duration 1.0 logfile.json
```

## Examples

### Find All Failed HTTP Requests

```python
from logxpy_cli_view import combine_filters_and, filter_by_action_status, filter_by_action_type

filter_fn = combine_filters_and(
    filter_by_action_status('failed'),
    filter_by_action_type(r'http:.*', regex=True),
)
```

### Find Slow Database Queries

```python
from logxpy_cli_view import combine_filters_and, filter_by_action_type, filter_by_duration

filter_fn = combine_filters_and(
    filter_by_action_type(r'database:.*', regex=True),
    filter_by_duration(min_seconds=1.0),
)
```

### Find Errors in Last Hour

```python
from datetime import timedelta
from logxpy_cli_view import combine_filters_and, filter_by_action_status, filter_by_relative_time

filter_fn = combine_filters_and(
    filter_by_action_status('failed'),
    filter_by_relative_time(timedelta(hours=1)),
)
```

### Search for Specific Error Types

```python
from logxpy_cli_view import combine_filters_and, filter_by_action_status, filter_by_keyword

filter_fn = combine_filters_and(
    filter_by_action_status('failed'),
    filter_by_keyword('ConnectionError'),
)
```

## Performance Notes

- `filter_by_jmespath` uses `@cache` for compiled expressions
- `filter_by_keyword` performs deep search (may be slower on large logs)
- Multiple filters are combined with AND logic by default
- Use `combine_filters_or()` for OR logic

## New Example Files

- `examples/python_samples/advanced_filtering.py` - Comprehensive filtering examples
- `examples/python_samples/log_analysis.py` - Log analysis and aggregation

Both examples include sample data generation for easy testing.
