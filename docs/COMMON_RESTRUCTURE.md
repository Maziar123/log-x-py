# Common Folder Restructure Plan

This document outlines the plan to reorganize the `common/` folder for better sharing between the three packages.

## Current State Analysis

### common/ modules
| Module | Purpose | Used By |
|--------|---------|----------|
| `base.py` | uuid, now, truncate, strip_ansi, etc. | None yet (planned for all) |
| `cache.py` | memoize, throttle, LRU cache | None yet |
| `fields.py` | Field normalization, get_field_value | parser only |
| `fmt.py` | format_value | None yet |
| `predicates.py` | Filter predicates (by_level, etc.) | None yet |
| `sqid.py` | Sqid generation/parsing | parser only |
| `types.py` | Type constants (TS, TID, MT, etc.) | parser only |

### Package-specific utils
| Package | Utils File | Key Functions |
|---------|------------|---------------|
| `logxpy/src/` | None (scattered in individual files) | - |
| `logxpy_cli_view/src/` | `_util.py` | Color, format helpers |
| `logxy-log-parser/src/` | `utils.py` | Timestamp, duration, boltons wrappers |

## Problems

1. **`common/` is not actually shared** - only parser uses it currently
2. **Duplicate utilities** - Each package has its own utils with similar functionality
3. **`common/fields.py`** - Has log-entry specific logic, should be in parser or shared
4. **No boltons/more-itertools wrappers** - These are mentioned in docs but not organized

## Proposed Structure

### Option 1: Minimal Common (Current approach, just organize better)

```
common/
├── __init__.py              # Re-exports
├── types.py                 # Type constants (TS, TID, MT, etc.)
├── sqid.py                  # Sqid generation/parsing
├── iter.py                  # Common iteration utilities (more-itertools wrappers)
├── dict.py                  # Common dict utilities (boltons wrappers)
└── cache.py                 # Caching utilities
```

### Option 2: Moderate Common (Share more, keep package-specific utils)

```
common/
├── __init__.py
├── core/                    # Core shared types
│   ├── types.py
│   └── sqid.py
├── utils/                   # Shared utilities
│   ├── cache.py
│   ├── iter.py              # more-itertools wrappers
│   └── dict.py              # boltons wrappers
└── compat/                  # Compatibility layer
    └── fields.py            # Field normalization (used by parser)
```

### Option 3: Full Common (Maximize sharing, risks over-coupling)

```
common/
├── __init__.py
├── types.py
├── sqid.py
├── fields.py                # Field extraction (used by parser, could be by others)
├── predicates.py            # Filter predicates (used by parser)
├── utils/
│   ├── base.py              # Base utilities (time, string, etc.)
│   ├── cache.py             # Caching
│   ├── fmt.py               # Formatting
│   ├── iter.py              # Iteration (more-itertools wrappers)
│   └── dict.py              # Dict (boltons wrappers)
└── subfolders/               # Package-specific shared code
    ├── logxpy/              # logxpy-specific shared code
    ├── cli_view/            # viewer-specific shared code
    └── parser/              # parser-specific shared code
```

## Recommendation: Option 2 (Moderate Common)

This approach:
1. Keeps truly shared code in `common/`
2. Moves package-specific code back to packages
3. Organizes utilities by category
4. Makes boltons/more-itertools accessible via wrappers

## Migration Steps

### Phase 1: Create new common/ structure

```bash
# Create subfolders
mkdir -p common/core
mkdir -p common/utils

# Move core types
mv common/types.py common/core/
mv common/sqid.py common/core/

# Create shared utils
# - Move cache.py to utils/
mv common/cache.py common/utils/

# Create iter.py (more-itertools wrappers)
cat > common/utils/iter.py << 'EOF'
"""Shared iteration utilities using more-itertools."""

from more_itertools import chunked, pairwise, unique_everseen, windowed

__all__ = [
    "chunked", "pairwise", "unique_everseen", "windowed",
]
EOF

# Create dict.py (boltons wrappers)
cat > common/utils/dict.py << 'EOF'
"""Shared dict utilities using boltons."""

import boltons.dictutils as du

__all__ = [
    # Add boltons utilities as needed
]
EOF
```

### Phase 2: Move package-specific code back

```bash
# Move parser-specific fields/predicates to parser/src/
mv common/fields.py logxy-log-parser/src/
mv common/predicates.py logxy-log-parser/src/

# Move fmt.py to parser (or keep in common if useful for others)
# mv common/fmt.py logxy-log-parser/src/

# Move base.py utilities to appropriate locations
# - time functions -> common/utils/base.py or keep in common/base.py
# - string functions -> common/utils/base.py or keep in common/base.py
```

### Phase 3: Update imports

```python
# In parser:
from common.core.types import TS, TID, MT
from common.core.sqid import SqidGenerator
from common.utils.cache import memoize

# Or (simpler):
from common import TS, TID, MT, SqidGenerator, memoize
```

## Dependencies: boltons & more-itertools

The `common/` module should provide convenient wrappers for:

### boltons (v24.0.0+)

Key modules to wrap:
- **cacheutils**: `LRU`, `LRI`, `@cached`, `cachedproperty`
- **dictutils**: `OrderedMultiDict`, `OneToOne`, `ManyToMany`
- **iterutils**: `remap`, `research`, `chunked`, `bucketize`

### more-itertools (v10.0.0+)

Key functions to re-export:
- **Grouping**: `chunked`, `batched`, `ichunked`, `grouper`, `bucket`
- **Lookahead**: `peekable`, `seekable`
- **Iterating**: `consume`, `nth`, `first`, `last`, `one`
- **Filtering**: `filter_except`, `map_except`, `split_at`, `partition`
- **Windowing**: `windowed`, `sliding_window`

## File Organization

```
common/
├── __init__.py              # Main re-exports
├── core/
│   ├── __init__.py
│   ├── types.py             # Type constants (TS, TID, MT, etc.)
│   └── sqid.py             # Sqid generation/parsing
├── utils/
│   ├── __init__.py
│   ├── base.py              # Base utilities (moved from common/base.py)
│   ├── cache.py             # Caching (moved from common/cache.py)
│   ├── iter.py              # more-itertools wrappers
│   ├── dict.py              # boltons wrappers
│   └── fmt.py               # Formatting utilities (if truly shared)
└── compat/                  # Optional compatibility layer
    └── __init__.py
```

## Next Steps

1. Review current `common/` files to identify what's truly shared
2. Create new folder structure
3. Move package-specific code back to packages
4. Update all imports
5. Update documentation
