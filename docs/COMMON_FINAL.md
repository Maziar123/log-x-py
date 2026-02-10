# Common Module - Final Structure

## Overview

The `common/` module provides shared types, constants, and utilities across all three LogXPy packages:
- `logxpy` (logging library)
- `logxpy_cli_view` (tree viewer)
- `logxy-log-parser` (log parser)

## Structure

```
common/
├── __init__.py       # Main exports (257 lines)
├── base.py           # Base utilities (time, string, truncation, etc.)
├── cache.py          # Caching decorators (memoize, throttle, LRU)
├── dictutils.py      # Boltons dict wrappers
├── fields.py         # Field normalization and extraction
├── fmt.py            # Data type formatters
├── iterutils.py      # more-itertools wrappers
├── predicates.py     # Filter predicates (by_level, is_error, etc.)
├── sqid.py           # Sqid generation and parsing
└── types.py          # Type aliases, field constants, enums
```

## Module Details

### `types.py` - Type Constants & Aliases

Field name constants (compact format):
- `TS`, `TID`, `LVL`, `MT`, `AT`, `ST`, `DUR`, `MSG`

Field name constants (legacy format):
- `TIMESTAMP`, `TASK_UUID`, `TASK_LEVEL`, `MESSAGE_TYPE`, `ACTION_TYPE`, `ACTION_STATUS`, `DURATION_NS`, `MESSAGE`

Type aliases:
- `LogEntry`, `LogDict`, `TaskLevelTuple`, `FieldDict`, `MessageDict`, `ContextDict`

Enums:
- `Level` (DEBUG, INFO, SUCCESS, NOTE, WARNING, ERROR, CRITICAL)
- `ActionStatus` (STARTED, SUCCEEDED, FAILED)
- `LogFormat` (COMPACT, LEGACY, AUTO)
- `LevelStr`, `ActionStatusStr`

Utility functions:
- `detect_format()` - Detect compact vs legacy format
- `get_field()` - Get field value with format compatibility
- `normalize_field_name()` - Convert legacy to compact field names
- `get_level_name()`, `get_level_value()` - Level conversions

### `sqid.py` - Sqid Task IDs

Sqid is a hierarchical task ID format that's 89% smaller than UUID4.

Functions:
- `sqid()` - Generate new Sqid
- `parse_sqid()` - Parse Sqid into components
- `sqid_depth()` - Get nesting depth
- `sqid_parent()` - Get parent Sqid
- `sqid_root()` - Get root Sqid
- `child_sqid()` - Create child Sqid

Classes:
- `SqidGenerator` - Generate hierarchical Sqids
- `SqidInfo` - Parsed Sqid information
- `SqidParser` - Parse Sqid strings

### `fields.py` - Field Extraction

Functions for extracting and normalizing log entry fields:
- `get_field_value()` - Get field with fallback
- `get_timestamp()`, `parse_timestamp()`, `format_timestamp()`
- `get_task_uuid()`, `get_task_level()`
- `get_action_type()`, `get_action_status()`
- `get_message()`, `get_message_type()`
- `extract_duration()`, `parse_duration()`
- `normalize_entry()` - Convert to compact format
- `extract_task_uuids()` - Extract all UUIDs from entry

### `predicates.py` - Filter Predicates

Predicates for filtering log entries:
- `by_level()`, `is_debug()`, `is_info()`, `is_warning()`, `is_error()`, `is_critical()`
- `by_action_type()`, `by_action_type_pattern()`
- `by_status()`, `is_started()`, `is_succeeded()`, `is_failed()`
- `by_time_range()`, `after()`, `before()`
- `by_task_uuid()`, `by_nesting_level()`
- `by_message()`, `by_keyword()`
- `by_field_exists()`, `by_field()`, `by_field_contains()`
- `has_traceback()`, `is_slow()`, `is_fast()`
- `combine_and()`, `combine_or()`, `combine_not()`

### `base.py` - Base Utilities

Core utility functions:
- `now()` - Current timestamp
- `monotonic()` - Monotonic time
- `uuid()` - Generate UUID (with Sqid option)
- `truncate()` - Truncate string with ellipsis
- `strip_ansi_codes()` - Remove ANSI escape codes
- `escape_html_text()` - HTML escape
- `clean_text()` - Clean whitespace
- `pluralize()` - Pluralize words
- `get_first()` - Get first truthy value
- `get_module()` - Get module by name
- `is_non_string_iterable()` - Check if iterable (not string)
- `cachedproperty` - Cached property decorator

### `cache.py` - Caching Utilities

Caching decorators and classes:
- `memoize` - Simple memoization decorator
- `memoize_method` - Memoize instance methods
- `throttle` - Throttle function calls
- `cache_until_invalidation` - Cache with manual invalidation
- `CacheStats` - Cache statistics

### `fmt.py` - Value Formatting

- `format_value()` - Format any value for display

### `iterutils.py` - Iteration Utilities (more-itertools)

Wrappers around more-itertools library:

**Grouping:**
- `chunked`, `batched`, `ichunked`, `grouper`, `bucket`

**Filtering:**
- `filter_except`, `map_except`, `partition`, `split_at`

**Iterating:**
- `consume`, `first`, `last`, `nth`, `one`

**Lookahead:**
- `peekable`, `seekable`

**Windowing:**
- `windowed`, `sliding_window`

**Other:**
- `flatten`, `pairwise`, `unique_everseen`

### `dictutils.py` - Dict Utilities (boltons)

Wrappers around boltons.dictutils:

**Classes:**
- `OrderedMultiDict` - Dict preserving insertion order for duplicates
- `OneToOne` - Bidirectional mapping
- `ManyToMany` - Many-to-many relationship mapping
- `FrozenDict` - Immutable dictionary

**Functions:**
- `get_nested()` - Get nested dict value by key path
- `set_nested()` - Set nested dict value by key path

## Usage Examples

### Importing from common

```python
# Import field name constants
from common import TS, TID, MT, Level

# Import sqid functions
from common import parse_sqid, sqid

# Import iteration utilities
from common import chunked, first, flatten

# Import dict utilities
from common import FrozenDict, get_nested
```

### Using with log entries

```python
from common import TS, TID, MT, get_field, parse_sqid

entry = {"ts": 1234567890.0, "tid": "Xa.1", "mt": "info"}

# Get field value (works with both compact and legacy)
ts = get_field(entry, TS)  # Gets entry["ts"] or entry["timestamp"]

# Parse Sqid
info = parse_sqid(entry[TID])  # SqidInfo(...)
```

### Using iteration utilities

```python
from common import chunked, first, flatten

# Chunk list into groups
for group in chunked([1, 2, 3, 4, 5], 2):
    print(group)  # [1, 2], [3, 4], [5]

# Get first item or default
first([1, 2, 3], default=None)  # 1

# Flatten nested iterables
list(flatten([[1, 2], [3, 4]]))  # [1, 2, 3, 4]
```

### Using dict utilities

```python
from common import FrozenDict, get_nested, set_nested

# Create immutable dict
fd = FrozenDict({'a': 1, 'b': 2})

# Get nested value
d = {'a': {'b': {'c': 1}}}
get_nested(d, 'a', 'b', 'c')  # 1

# Set nested value
set_nested(d, 2, 'a', 'b', 'c')  # d is now {'a': {'b': {'c': 2}}}
```

## Dependencies

The `common/` module relies on these third-party libraries (defined in root `pyproject.toml`):
- `boltons>=24.0.0` - For `dictutils.py`
- `more-itertools>=10.0.0` - For `iterutils.py`

## Version

Current version: `0.2.0` (defined in `common/__init__.py`)
