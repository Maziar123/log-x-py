# Libraries Integration Guide

> How logxpy and logxy-log-parser use boltons and Python 3.12+ features
> Python ≥3.12 · boltons ≥24.0.0 · Updated Feb 2026

---

## Overview

The log-x-py project leverages **boltons** — a pure-Python utility library — combined with **Python 3.12+ features** to provide cleaner, more efficient implementations across both components:

| Component | Python Version | boltons Usage |
|-----------|---------------|---------------|
| **logxpy** | ≥3.12.0 | cacheutils, dictutils, iterutils, strutils, funcutils |
| **logxy-log-parser** | ≥3.12.0 | dictutils, iterutils |

---

## Component 1: logxpy (Logging Library)

### Location
- [`logxpy/`](../logxpy/)
- Core: [`logxpy/logxpy/_cache.py`](../logxpy/logxpy/_cache.py), [`_base.py`](../logxpy/logxpy/_base.py), [`_message.py`](../logxpy/logxpy/_message.py), [`_action.py`](../logxpy/logxpy/_action.py)

### boltons Integrations

| Module | boltons Feature | Purpose |
|--------|----------------|---------|
| `_cache.py` | `cachedproperty` | Per-instance cached properties |
| `_base.py` | `first`, `is_iterable` | Advanced iteration helpers |
| `_base.py` | `strip_ansi`, `cardinalize`, `asciify` | String processing |
| `_message.py` | `OMD`, `subdict` | OrderedMultiDict for fields |
| `_action.py` | `wraps` | Better function wrapping |

### Python 3.12+ Features

| Feature | PEP | Location | Purpose |
|---------|-----|----------|---------|
| Type aliases | 695 | [`_types.py`](../logxpy/logxpy/_types.py) | `type LogEntry = dict[str, Any]` |
| StrEnum | 663 | [`_types.py`](../logxpy/logxpy/_types.py), [`_action.py`](../logxpy/logxpy/_action.py) | Type-safe string enums |
| Pattern matching | 634 | [`_base.py`](../logxpy/logxpy/_base.py), [`_action.py`](../logxpy/logxpy/_action.py) | Clean value routing |
| Dataclass slots | 681 | [`_types.py`](../logxpy/logxpy/_types.py) | ~40% memory reduction |

### Example Usage

```python
from logxpy._cache import memoize, memoize_method, CacheStats
from logxpy._base import truncate, strip_ansi_codes, pluralize
from logxpy._message import merge_messages, extract_fields
from logxpy._action import ActionStatus, TaskLevel

# Memoization with boltons cacheutils
@memoize(size=128)
def expensive_computation(x: int) -> int:
    return x * x

# StrEnum for type-safe status values
status: str = ActionStatus.STARTED  # "started"
if status == ActionStatus.FAILED:
    print("Action failed!")

# Pattern matching for clean logic
match action.status:
    case ActionStatus.STARTED:
        return "▶ Started"
    case ActionStatus.SUCCEEDED:
        return "✓ Succeeded"
    case ActionStatus.FAILED:
        return "✗ Failed"

# Efficient field operations with boltons dictutils
merged = merge_messages(msg1, msg2, msg3)
subset = extract_fields(message, 'task_uuid', 'timestamp')
```

---

## Component 2: logxy-log-parser (Log Parser)

### Location
- [`logxy-log-parser/`](../logxy-log-parser/)
- Core: [`logxy_log_parser/utils.py`](../logxy-log-parser/logxy_log_parser/utils.py)

### boltons Integrations

| Function | boltons Feature | Purpose |
|----------|----------------|---------|
| `subdict()` | `dictutils.subdict` | Extract subset of dictionary keys |
| `merge_fields()` | `dictutils` (via update) | Merge multiple dictionaries |
| Re-exports | `iterutils.bucketize` | Group values by key function |
| Re-exports | `iterutils.chunked` | Break iterable into chunks |
| Re-exports | `iterutils.first` | Get first matching item |
| Re-exports | `iterutils.is_iterable` | Check if iterable (not string) |
| Re-exports | `iterutils.split` | Split iterable on separator |
| Re-exports | `iterutils.unique` | Unique values preserving order |
| Re-exports | `iterutils.pairwise` | Sliding window of size 2 |
| Re-exports | `iterutils.windowed` | Sliding window of any size |
| Re-exports | `iterutils.flatten` | Collapse one level of nesting |

### Example Usage

```python
from logxy_log_parser.utils import (
    subdict, bucketize, chunked, first,
    unique, pairwise, windowed, flatten, split
)

# Extract specific fields from log entries
subset = subdict(entry, {'task_uuid', 'timestamp', 'level'})

# Group log entries by level
by_level = bucketize(entries, key=lambda e: e.get('level'))

# Process in chunks
for batch in chunked(million_entries, 1000):
    db.insert_many(batch)

# Get first error entry
error = first(entries, key=lambda e: e.get('level') == 'error')

# Sliding window analysis
for triplet in windowed(prices, 3):
    moving_avg = sum(triplet) / 3
```

---

## Performance Benefits

### Memory Efficiency
- **Dataclass slots (PEP 681)**: ~40% memory reduction
- **OMD (OrderedMultiDict)**: Efficient field merging without copies

### Speed Improvements
- **Pattern matching (PEP 634)**: ~10% faster than if/elif chains
- **boltons cacheutils**: Zero-overhead memoization
- **boltons iterutils**: Optimized C-like loops in pure Python

### Code Quality
- **Type aliases (PEP 695)**: Cleaner type hints
- **StrEnum (PEP 663)**: Type-safe string values
- **boltons functions**: Fewer bugs, better readability

---

## Quick Reference

### logxpy Public API

```python
# Caching and memoization
from logxpy._cache import memoize, memoize_method, throttle, CacheStats

# String and text utilities
from logxpy._base import (
    truncate, strip_ansi_codes, escape_html_text,
    pluralize, clean_text, get_first, is_non_string_iterable
)

# Message operations
from logxpy._message import merge_messages, extract_fields
```

### logxy-log-parser Public API

```python
from logxy_log_parser.utils import (
    # Parsing
    parse_timestamp, format_timestamp, parse_duration,
    level_from_message_type, extract_task_uuid,

    # Dictionary operations
    merge_fields, subdict,

    # Iteration (boltons re-exports)
    bucketize, chunked, first, is_iterable, split,
    unique, pairwise, windowed, flatten
)
```

---

## See Also

- [boltons Complete Reference](boltons-ref.md) — Full boltons API documentation
- [more-itertools Reference](more-itertools-ref.md) — For advanced iteration needs
- [boltons in logxpy](boltons-in-logxpy.md) — Detailed logxpy integration guide
- [Python 3.12 Release Notes](https://docs.python.org/3.12/whatsnew.html)
