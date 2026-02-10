# Deep Refactor: Final Project Tree

This document describes the step-by-step plan to refactor 3 subprojects into a single unified project.

---

## Quick Summary: Final Structure

```
log-x-py/                              # ROOT (/mnt/N1/MZ/AMZ/Projects/Prog/a_cross/log-x-py)
│
├── pyproject.toml                     # SINGLE config for ALL packages
├── uv.lock                            # Single lock file
│
├── common/                            # SHARED CODE (can have subfolders if needed)
├── tests/                             # SHARED TESTS
├── examples/                          # SHARED EXAMPLES
├── benchmarks/                        # SHARED BENCHMARKS
├── docs/                              # SHARED DOCS
├── tutorials/                         # SHARED TUTORIALS
│
├── logxpy/src/*.py                    # Package code (*.py files directly in src/)
├── logxpy_cli_view/src/*.py           # Package code (*.py files directly in src/)
└── logxy-log-parser/src/*.py          # Package code (*.py files directly in src/)
```

**Key Points:**
- Project root: `/mnt/N1/MZ/AMZ/Projects/Prog/a_cross/log-x-py`
- Single `pyproject.toml` and `uv.lock` at root
- `common/` at root (can have subfolders if needed)
- `tests/`, `examples/`, `benchmarks/`, `docs/`, `tutorials/` at root
- Each subproject has `src/` folder with `*.py` files directly inside

---

## Current State (3 Subprojects)

```
log-x-py/                              # ROOT
├── pyproject.toml                     # Root config (empty packages=[])
├── uv.lock                            # Root lock file
├── README.md
├── AGENTS.md
│
├── logxpy/                            # Subproject 1 - WRONG STRUCTURE
│   ├── setup.py                       # Legacy setuptools
│   ├── common/                        # <-- PROBLEM: Should be root shared code!
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── cache.py
│   │   ├── fields.py
│   │   ├── fmt.py
│   │   ├── predicates.py
│   │   ├── sqid.py
│   │   └── types.py
│   ├── logxpy/                        # <-- PROBLEM: Nested package!
│   │   ├── __init__.py
│   │   ├── _action.py
│   │   ├── _async.py
│   │   ├── _base.py
│   │   ├── _cache.py
│   │   ├── category.py
│   │   ├── cli.py
│   │   ├── _compat.py
│   │   ├── _config.py
│   │   ├── dask.py
│   │   ├── data_types.py
│   │   ├── decorators.py
│   │   ├── _dest.py
│   │   ├── _errors.py
│   │   ├── file_stream.py
│   │   ├── filter.py
│   │   ├── _fmt.py
│   │   ├── _generators.py
│   │   ├── journald.py
│   │   ├── json.py
│   │   ├── loggerx.py
│   │   ├── logwriter.py
│   │   ├── _mask.py
│   │   ├── _message.py
│   │   ├── _output.py
│   │   ├── parse.py
│   │   ├── _pool.py
│   │   ├── prettyprint.py
│   │   ├── serializers.py
│   │   ├── _sqid.py
│   │   ├── stdlib.py
│   │   ├── system_info.py
│   │   ├── tai64n.py
│   │   ├── testing.py
│   │   ├── _traceback.py
│   │   ├── twisted.py
│   │   ├── _types.py
│   │   ├── _util.py
│   │   ├── _validation.py
│   │   ├── _version.py
│   │   └── tests/                     # <-- PROBLEM: Tests INSIDE package!
│   ├── tests/                         # External tests (some files)
│   ├── examples/                      # 14+ example files
│   ├── benchmarks/                    # 3 files
│   └── docs/                          # Empty/small
│
├── logxpy_cli_view/                   # Subproject 2
│   ├── pyproject.toml                 # Separate config
│   ├── uv.lock                        # Separate lock file
│   ├── src/logxpy_cli_view/           # Already has src/ but nested package
│   │   ├── __init__.py
│   │   ├── _cli.py
│   │   ├── _color.py
│   │   ├── _compat.py
│   │   ├── _errors.py
│   │   ├── _export.py
│   │   ├── filter.py
│   │   ├── format.py
│   │   ├── _parse.py
│   │   ├── _patterns.py
│   │   ├── _render.py
│   │   ├── _stats.py
│   │   ├── _tail.py
│   │   ├── _theme.py
│   │   ├── tree.py
│   │   ├── tree_format/
│   │   │   ├── __init__.py
│   │   │   └── _text.py
│   │   └── _util.py
│   ├── tests/                         # 8 test files
│   ├── examples/                      # 11 example folders
│   └── doc/                           # Documentation
│
├── logxy-log-parser/                  # Subproject 3
│   ├── pyproject.toml                 # Separate config
│   ├── uv.lock                        # Separate lock file
│   ├── logxy_log_parser/              # <-- PROBLEM: No src/ folder
│   │   ├── __init__.py
│   │   ├── aggregation.py
│   │   ├── analyzer.py
│   │   ├── cli.py
│   │   ├── config.py
│   │   ├── core.py
│   │   ├── export.py
│   │   ├── filter.py
│   │   ├── index.py
│   │   ├── monitor.py
│   │   ├── simple.py
│   │   ├── sqid.py                    # <-- DUPLICATE of common/sqid.py
│   │   ├── tree.py
│   │   ├── types.py                   # <-- DUPLICATE of common/types.py
│   │   └── utils.py
│   ├── tests/                         # 7 test files
│   └── examples/                      # 16+ example files
│
├── DOC/                               # Reference documentation (KEEP)
│   ├── boltons-ref.md
│   └── more-itertools-ref.md
│
├── docs/                              # Root docs (KEEP)
├── examples-log-view/                 # Additional examples (KEEP)
└── tutorials/                         # Tutorials (KEEP)
```

---

## Problems to Fix

| # | Problem | Fix |
|---|---------|-----|
| 1 | `logxpy/common/` is in wrong location (under logxpy/) | Move to root `common/` |
| 2 | `logxpy/logxpy/` is nested (package inside package) | Move files to `logxpy/src/` |
| 3 | `logxpy_cli_view/src/logxpy_cli_view/` has nested package | Move files to `logxpy_cli_view/src/` |
| 4 | `logxy-log-parser` has no `src/` folder | Create `logxy-log-parser/src/` |
| 5 | `sqid.py` and `types.py` duplicated in parser | Remove, use `common/` |
| 6 | 3 separate `pyproject.toml` files | Merge into single root file |
| 7 | Tests, examples, benchmarks scattered | Merge into root folders |
| 8 | 3 separate `uv.lock` files | Single lock file in root |

---

## Target State (After Refactor)

```
log-x-py/                              # SINGLE UNIFIED PROJECT
├── pyproject.toml                     # SINGLE config for all packages
├── uv.lock                            # Single lock file
├── README.md
├── LICENSE
├── AGENTS.md
│
├── common/                           # SHARED CODE - ROOT LEVEL
│   ├── __init__.py
│   ├── base.py                        # uuid, now, truncate, strip_ansi, etc.
│   ├── cache.py                       # memoize, memoize_method, throttle, etc.
│   ├── fields.py                      # get_field_value, normalize_entry, etc.
│   ├── fmt.py                         # format_value
│   ├── predicates.py                  # by_level, by_action_type, etc.
│   ├── sqid.py                        # Sqid generation (used by all 3)
│   ├── types.py                       # TS, TID, MT, AT, ST, DUR, MSG constants
│   └── validation.py                  # Schema validation
│
├── tests/                            # SHARED TESTS - ROOT LEVEL
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_logxpy/
│   ├── test_cli_view/
│   └── test_parser/
│
├── examples/                         # SHARED EXAMPLES - ROOT LEVEL
│   ├── README.md
│   ├── logxpy/
│   ├── cli_view/
│   └── parser/
│
├── benchmarks/                       # SHARED BENCHMARKS - ROOT LEVEL
│   ├── logxpy/
│   ├── cli_view/
│   └── parser/
│
├── docs/                             # SHARED DOCS - ROOT LEVEL
├── tutorials/                        # SHARED TUTORIALS - ROOT LEVEL
│
├── logxpy/                           # Subproject 1: ONLY src/ folder
│   └── src/                          # *.py files DIRECTLY here (no subfolder)
│       ├── __init__.py
│       ├── _action.py
│       ├── _async.py
│       ├── _base.py
│       ├── _cache.py
│       ├── category.py
│       ├── cli.py
│       ├── _compat.py
│       ├── _config.py
│       ├── dask.py
│       ├── data_types.py
│       ├── decorators.py
│       ├── _dest.py
│       ├── _errors.py
│       ├── file_stream.py
│       ├── filter.py
│       ├── _fmt.py
│       ├── _generators.py
│       ├── journald.py
│       ├── json.py
│       ├── loggerx.py
│       ├── logwriter.py
│       ├── _mask.py
│       ├── _message.py
│       ├── _output.py
│       ├── parse.py
│       ├── _pool.py
│       ├── prettyprint.py
│       ├── serializers.py
│       ├── _sqid.py
│       ├── stdlib.py
│       ├── system_info.py
│       ├── tai64n.py
│       ├── testing.py
│       ├── _traceback.py
│       ├── twisted.py
│       ├── _types.py
│       ├── _util.py
│       ├── _validation.py
│       └── _version.py
│
├── logxpy_cli_view/                  # Subproject 2: ONLY src/ folder
│   └── src/                          # *.py files DIRECTLY here (no subfolder)
│       ├── __init__.py
│       ├── _cli.py
│       ├── _color.py
│       ├── _compat.py
│       ├── _errors.py
│       ├── _export.py
│       ├── filter.py
│       ├── format.py
│       ├── _parse.py
│       ├── _patterns.py
│       ├── _render.py
│       ├── _stats.py
│       ├── _tail.py
│       ├── _theme.py
│       ├── tree.py
│       └── tree_format/
│           ├── __init__.py
│           └── _text.py
│
└── logxy-log-parser/                 # Subproject 3: ONLY src/ folder
    └── src/                          # *.py files DIRECTLY here (no subfolder)
        ├── __init__.py
        ├── aggregation.py
        ├── analyzer.py
        ├── cli.py
        ├── config.py
        ├── core.py
        ├── export.py
        ├── filter.py
        ├── index.py
        ├── monitor.py
        ├── simple.py
        ├── tree.py
        └── utils.py
        # sqid.py REMOVED - uses common/
        # types.py REMOVED - uses common/
```

---

# Phase 1: Move common/ to Root + Create src/ folders

**Goal**: Fix the `common/` location and create unified `src/` structure in each subproject

## Step 1.1: Move common/ to root

```bash
# common/ is already SHARED code - move to root
mv logxpy/common common
```

**Before:**
```
logxpy/
└── common/           # Wrong location - under subproject
    ├── base.py
    ├── cache.py
    └── ...
```

**After:**
```
common/                # Root level - shared by all packages
├── base.py
├── cache.py
├── fields.py
├── fmt.py
├── predicates.py
├── sqid.py
├── types.py
└── validation.py
```

## Step 1.2: Create src/ for logxpy and move package files

```bash
# Create src/ in logxpy
mkdir -p logxpy/src

# Move ALL *.py files from nested package to src/
mv logxpy/logxpy/*.py logxpy/src/

# Move tree_format subfolder if exists
mv logxpy/logxpy/tree_format logxpy/src/ 2>/dev/null || true

# Remove old nested package folder
rm -rf logxpy/logxpy
```

**Before:**
```
logxpy/
├── setup.py
├── common/              # Moved in Step 1.1
└── logxpy/              # Nested package - WRONG!
    ├── __init__.py
    └── ... (37 more .py files)
```

**After:**
```
logxpy/
└── src/                # All *.py files directly here
    ├── __init__.py
    ├── _action.py
    └── ... (37 more .py files)
```

## Step 1.3: Move files from logxpy_cli_view/src/ nested package

```bash
# Move ALL *.py files from nested package to src/
mv logxpy_cli_view/src/logxpy_cli_view/*.py logxpy_cli_view/src/

# Move tree_format subfolder
mv logxpy_cli_view/src/logxpy_cli_view/tree_format logxpy_cli_view/src/ 2>/dev/null || true

# Remove old nested package folder
rm -rf logxpy_cli_view/src/logxpy_cli_view
```

**Before:**
```
logxpy_cli_view/
└── src/
    └── logxpy_cli_view/    # Nested package - WRONG!
        ├── __init__.py
        └── ... (15 more .py files)
```

**After:**
```
logxpy_cli_view/
└── src/                    # All *.py files directly here
    ├── __init__.py
    ├── _cli.py
    └── ... (15 more .py files)
```

## Step 1.4: Create src/ for logxy-log-parser

```bash
# Create src/ in logxy-log-parser
mkdir -p logxy-log-parser/src

# Move ALL *.py files to src/
mv logxy-log-parser/logxy_log_parser/*.py logxy-log-parser/src/

# Remove duplicate files (use common/ instead)
rm logxy-log-parser/src/sqid.py
rm logxy-log-parser/src/types.py

# Remove old package folder
rm -rf logxy-log-parser/logxy_log_parser
```

**Before:**
```
logxy-log-parser/
└── logxy_log_parser/    # No src/ folder
    ├── __init__.py
    ├── sqid.py          # Duplicate - will remove
    ├── types.py         # Duplicate - will remove
    └── ... (12 more .py files)
```

**After:**
```
logxy-log-parser/
└── src/                # All *.py files directly here
    ├── __init__.py
    ├── aggregation.py
    └── ... (12 more .py files)
```

## Step 1.5: Verify layout

```bash
# Verify all three subprojects have src/ with *.py files
ls logxpy/src/*.py           # Should show ~40 .py files
ls logxpy_cli_view/src/*.py   # Should show ~17 .py files
ls logxy-log-parser/src/*.py  # Should show ~13 .py files

# Verify common/ is at root
ls common/                    # Should show: base.py, cache.py, fields.py, etc.
```

---

# Phase 2: Move Tests from Packages to Root

**Goal**: Remove tests from inside packages, merge into root `tests/`

## Step 2.1: Move logxpy tests (INSIDE package - CRITICAL FIX)

```bash
mkdir -p tests/test_logxpy

# Tests are INSIDE the package - but we already moved files in Phase 1
# Tests might be at old location or already moved - check both
if [ -d "logxpy/src/tests" ]; then
    mv logxpy/src/tests/* tests/test_logxpy/
    rmdir logxpy/src/tests
elif [ -d "logxpy/logxpy/tests" ]; then
    mv logxpy/logxpy/tests/* tests/test_logxpy/
    rmdir logxpy/logxpy/tests
fi
```

**Before (WRONG):**
```
logxpy/src/logxpy/ or logxpy/logxpy/
├── __init__.py
├── _action.py
├── tests/              # <-- INSIDE PACKAGE!
│   ├── test_action.py
│   └── ...
```

**After (CORRECT):**
```
logxpy/src/
├── __init__.py
├── _action.py
└── ...                # No tests/ folder

tests/test_logxpy/
├── test_action.py
└── ...
```

## Step 2.2: Move cli_view tests

```bash
mkdir -p tests/test_cli_view
mv logxpy_cli_view/tests/* tests/test_cli_view/
```

## Step 2.3: Move parser tests

```bash
mkdir -p tests/test_parser
mv logxy-log-parser/tests/* tests/test_parser/
```

## Step 2.4: Create shared conftest.py

```bash
cat > tests/conftest.py << 'EOF'
"""Shared pytest fixtures for all log-x-py tests."""
import pytest
from common import TS, TID, MT, MSG, LVL, AT, ST

@pytest.fixture
def sample_log_entry():
    """A sample log entry for testing."""
    return {
        TS: 1234567890.0,
        TID: "Xa.1",
        LVL: [1],
        MT: "info",
        MSG: "test message"
    }

@pytest.fixture
def sample_action_entry():
    """A sample action entry for testing."""
    return {
        TS: 1234567890.0,
        TID: "Xa.1",
        LVL: [1],
        MT: "started",
        AT: "test_action",
        ST: "started",
        MSG: "Starting action"
    }
EOF
```

---

# Phase 3: Merge Examples, Benchmarks, Docs

## Step 3.1: Merge examples/

```bash
mkdir -p examples/logxpy examples/cli_view examples/parser

# Move logxpy examples
mv logxpy/examples/* examples/logxpy/ 2>/dev/null || true

# Move cli_view examples
mv logxpy_cli_view/examples/* examples/cli_view/ 2>/dev/null || true

# Move parser examples
mv logxy-log-parser/examples/* examples/parser/ 2>/dev/null || true

# Create unified README
cat > examples/README.md << 'EOF'
# LogXPy Examples

## logxpy/ - Core logging library examples
Basic logging, decorators, async, context scopes, data types, etc.

## cli_view/ - Tree viewer examples
Visualizing logs as trees, filtering, color themes, metrics.

## parser/ - Log parser examples
Parsing logs, filtering, analysis, indexing, monitoring.
EOF
```

## Step 3.2: Merge benchmarks/

```bash
mkdir -p benchmarks/logxpy benchmarks/cli_view benchmarks/parser

# Move logxpy benchmarks
mv logxpy/benchmarks/* benchmarks/logxpy/ 2>/dev/null || true

# Move others if they exist
mv logxpy_cli_view/benchmarks/* benchmarks/cli_view/ 2>/dev/null || true
mv logxy-log-parser/benchmarks/* benchmarks/parser/ 2>/dev/null || true
```

## Step 3.3: Merge docs/

```bash
# Merge all documentation
mv logxpy_cli_view/doc/* docs/ 2>/dev/null || true
mv logxy-log-parser/*.md docs/ 2>/dev/null || true
```

---

# Phase 4: Unified pyproject.toml

## Step 4.1: Merge all 3 pyproject.toml into root

```bash
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "log-x-py"
version = "0.1.0"
description = "Structured logging ecosystem with tree visualization and log parsing"
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
authors = [
    { name = "LogXPy Contributors" }
]
keywords = ["logging", "logxpy", "tree-view", "log-parser", "structured-logging"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Logging",
]

# Core dependencies (shared by all packages)
dependencies = [
    "boltons>=24.0.0",      # Core utilities (cacheutils, dictutils, iterutils, etc.)
    "more-itertools>=10.0.0",  # 160+ functions extending itertools
]

[tool.hatch.build.targets.wheel]
packages = [
    "logxpy/src",
    "logxpy_cli_view/src",
    "logxy-log-parser/src",
    "common",
]

[project.optional-dependencies]
# Core logxpy dependencies
logxpy = [
    "zope.interface>=5.0",
    "pyrsistent>=0.11.8",
    "orjson; implementation_name=='cpython'",
]

# CLI viewer dependencies
cli-view = [
    "jmespath>=1.0.0",
    "iso8601>=2.0.0",
    "colored>=2.0.0",
    "toolz>=0.12.0",
    "win-unicode-console>=0.5;platform_system=='Windows'",
]

# Parser dependencies
parser = [
    "pandas>=2.0",
    "rich>=13.0",
    "click>=8.0",
    "jinja2>=3.0",
]

# Development dependencies
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "mypy>=1.8",
    "ruff>=0.1",
]

# Everything
all = [
    "log-x-py[logxpy,cli-view,parser,dev]",
]

[project.scripts]
# CLI viewer commands
logxpy-view = "logxpy_cli_view._cli:main"
logxpy-cli-view = "logxpy_cli_view._cli:main"

# Parser commands
logxy = "logxy_log_parser.cli:main"
logxy-query = "logxy_log_parser.cli:main"
logxy-analyze = "logxy_log_parser.cli:main"
logxy-view = "logxy_log_parser.cli:main"
logxy-tree = "logxy_log_parser.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = "."
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--tb=short",
]

[tool.mypy]
python_version = "3.12"
mypy_path = "logxpy/src:logxpy_cli_view/src:logxy-log-parser/src:common"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
show_error_codes = true

[[tool.mypy.overrides]]
module = ["logxpy.*", "logxpy_cli_view.*", "logxy_log_parser.*"]
ignore_missing_imports = true

[tool.ruff]
target-version = "py312"
line-length = 120
src = ["logxpy/src", "logxpy_cli_view/src", "logxy-log-parser/src", "common", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "F",      # Pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "W",      # pycodestyle warnings
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "TID",    # flake8-tidy-imports
    "Q",      # flake8-quotes
    "FLY",    # flynt
    "PERF",   # perflint
    "RUF",    # Ruff-specific rules
]
ignore = [
    "E501",   # Line too long (handled by formatter)
]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.isort]
known-first-party = ["logxpy", "logxpy_cli_view", "logxy_log_parser", "common"]
EOF
```

---

# Phase 5: Update Imports + Cleanup

## Step 5.1: Update imports for common/

Find and replace in ALL source files:

```python
# OLD (wrong):
from logxpy.common import TS, TID, MT
from logxpy.common.base import now, uuid

# NEW (correct):
from common import TS, TID, MT, now, uuid
# or:
from common.base import now, uuid
from common.types import TS, TID, MT
```

For parser (remove duplicate imports):
```python
# OLD:
from .sqid import SqidGenerator
from .types import LogEntry

# NEW:
from common.sqid import SqidGenerator
from common.types import LogEntry
```

## Step 5.2: Remove old folders and configs

```bash
# After verifying everything works, remove old configs
rm -f logxpy/setup.py              # Legacy setup.py
rm -f logxpy/pyproject.toml        # Old config (if exists)
rm -f logxpy_cli_view/pyproject.toml  # Old config
rm -f logxy-log-parser/pyproject.toml  # Old config
rm -f logxpy_cli_view/uv.lock      # Old lock file
rm -f logxy-log-parser/uv.lock     # Old lock file

# Remove empty folders if any
rmdir logxpy/tests 2>/dev/null || true
rmdir logxpy/examples 2>/dev/null || true
rmdir logxpy/benchmarks 2>/dev/null || true
rmdir logxpy/docs 2>/dev/null || true
rmdir logxpy_cli_view/tests 2>/dev/null || true
rmdir logxpy_cli_view/examples 2>/dev/null || true
rmdir logxpy_cli_view/doc 2>/dev/null || true
rmdir logxy-log-parser/tests 2>/dev/null || true
rmdir logxy-log-parser/examples 2>/dev/null || true
```

## Step 5.3: Verify everything

```bash
# Check layout - each subproject has src/ with *.py files
ls logxpy/src/*.py                   # Should show ~40 .py files
ls logxpy_cli_view/src/*.py          # Should show ~17 .py files
ls logxy-log-parser/src/*.py         # Should show ~13 .py files

# Check common/ at root
ls common/                            # Should show: base.py, cache.py, etc.

# Check merged folders at root
ls tests/                             # Should show: test_logxpy/, test_cli_view/, test_parser/
ls examples/                          # Should show: logxpy/, cli_view/, parser/
ls benchmarks/                        # Should show: logxpy/, (others)
ls docs/                              # Should show merged docs

# Verify single pyproject.toml
ls pyproject.toml                     # Should exist at root
ls logxpy/pyproject.toml 2>/dev/null  # Should NOT exist
ls logxpy_cli_view/pyproject.toml 2>/dev/null  # Should NOT exist
ls logxy-log-parser/pyproject.toml 2>/dev/null # Should NOT exist

# Verify single lock file
ls uv.lock                            # Should exist (root only)

# Test imports
python -c "from common import TS, TID, MT; print('common: OK')"
python -c "from logxpy.src import Message; print('logxpy: OK')"
python -c "from logxpy_cli_view.src import render_tasks; print('logxpy_cli_view: OK')"
python -c "from logxy_log_parser.src import parse_log; print('logxy_log_parser: OK')"

# Run tests
pytest tests/ -v

# Regenerate lock file
uv lock
```

---

# Summary of Changes

| Phase | Action | Files Changed |
|-------|--------|---------------|
| 1 | Move common/ to root, create src/ in each subproject | ~70 source files |
| 2 | Move tests from packages to root | 46 test files |
| 3 | Merge examples, benchmarks, docs | ~40 files |
| 4 | Unified pyproject.toml | 1 file |
| 5 | Update imports, cleanup | ~100 import statements |

---

# File Movement Summary

### From → To

| Source | Destination | Notes |
|--------|-------------|-------|
| `logxpy/common/` | `common/` | Shared code to root |
| `logxpy/logxpy/*.py` | `logxpy/src/*.py` | Flatten to src/ |
| `logxpy/logxpy/tests/` | `tests/test_logxpy/` | Tests out of package |
| `logxpy_cli_view/src/logxpy_cli_view/*.py` | `logxpy_cli_view/src/*.py` | Flatten to src/ |
| `logxy-log-parser/logxy_log_parser/*.py` | `logxy-log-parser/src/*.py` | Flatten to src/ |
| `logxy-log-parser/src/sqid.py` | *(deleted)* | Use common/ |
| `logxy-log-parser/src/types.py` | *(deleted)* | Use common/ |
| `logxpy/examples/` | `examples/logxpy/` | Merge to root |
| `logxpy_cli_view/examples/` | `examples/cli_view/` | Merge to root |
| `logxy-log-parser/examples/` | `examples/parser/` | Merge to root |
| `logxpy/benchmarks/` | `benchmarks/logxpy/` | Merge to root |
| `logxpy_cli_view/tests/` | `tests/test_cli_view/` | Merge to root |
| `logxy-log-parser/tests/` | `tests/test_parser/` | Merge to root |

---

# Import Migration Guide

## Files that need import updates:

### In logxpy/src/:
- All files importing from `logxpy.common`
- Update: `from logxpy.common import X` → `from common import X`

### In logxpy_cli_view/src/:
- Check for any imports from logxpy
- Update if needed

### In logxy-log-parser/src/:
- Remove: `from .sqid import` → `from common.sqid import`
- Remove: `from .types import` → `from common.types import`

### In tests/:
- Update all test imports to use new package locations

---

# Common Module Organization

The `common/` module provides shared utilities:

```
common/
├── __init__.py          # Re-exports common symbols
├── base.py              # uuid, now, truncate, strip_ansi
├── cache.py             # memoize, throttle, LRU cache
├── fields.py            # Field access, normalization
├── fmt.py               # Value formatting
├── predicates.py        # Filtering predicates
├── sqid.py              # Sqid ID generation
├── types.py             # Type constants (TS, TID, MT, etc.)
└── validation.py        # Schema validation
```

**Re-exports in `__init__.py`:**
```python
from common.types import *
from common.base import uuid, now, truncate
from common.sqid import SqidGenerator, sqid
from common.fields import get_field_value
from common.predicates import by_level, by_action_type
```

---

# Final Installation

```bash
# Install everything
uv pip install -e .

# Install specific components
uv pip install -e ".[logxpy]"
uv pip install -e ".[cli-view]"
uv pip install -e ".[parser]"

# Development
uv pip install -e ".[all]"
```

---

# Quick Reference Commands

```bash
# After refactor, verify structure:
find logxpy/src -name "*.py" | wc -l           # Should be ~40 files
find logxpy_cli_view/src -name "*.py" | wc -l  # Should be ~17 files
find logxy-log-parser/src -name "*.py" | wc -l # Should be ~13 files
find common -name "*.py" | wc -l               # Should be ~8 files
find tests -name "test_*.py" | wc -l           # Should be ~46 files
find examples -type f | wc -l                  # Should be ~40 files

# Verify single pyproject.toml
ls pyproject.toml                              # Should exist
ls logxpy/pyproject.toml 2>/dev/null           # Should NOT exist
ls logxpy_cli_view/pyproject.toml 2>/dev/null  # Should NOT exist
ls logxy-log-parser/pyproject.toml 2>/dev/null # Should NOT exist

# Verify single lock file
ls uv.lock                                     # Should exist (root only)

# Verify each subproject has src/ with *.py files
ls logxpy/src/__init__.py                      # Should exist
ls logxpy_cli_view/src/__init__.py             # Should exist
ls logxy-log-parser/src/__init__.py            # Should exist
```

---

# Dependencies: boltons & more-itertools

The `common/` module uses these included dependencies:

## boltons (v24.0.0+)

Pure Python utility library with 250+ functions across 26 modules.

Key modules used:
- **cacheutils**: `LRU`, `LRI`, `@cached`, `cachedproperty`
- **dictutils**: `OrderedMultiDict`, `OneToOne`, `ManyToMany`
- **iterutils**: `remap`, `research`, `chunked`, `bucketize`
- **funcutils**: `wraps`, `FunctionBuilder`
- **ioutils**: `SpooledBytesIO`, `MultiFileReader`
- **mathutils**: `clamp`, `ceil`, `floor`, `Bits`
- **queueutils**: `HeapPriorityQueue`, `PriorityQueue`
- **setutils**: `IndexedSet`, `complement`

Reference: [DOC/boltons-ref.md](docs/boltons-ref.md)

## more-itertools (v10.0.0+)

160+ functions extending itertools.

Key functions used:
- **Grouping**: `chunked`, `batched`, `ichunked`, `grouper`, `bucket`
- **Lookahead**: `peekable`, `seekable`
- **Iterating**: `consume`, `nth`, `first`, `last`, `one`
- **Filtering**: `filter_except`, `map_except`, `split_at`, `partition`
- **Windowing**: `windowed`, `sliding_window`
- **Math**: `convolve`, `sum_of_squares`, `matmul`

Reference: [DOC/more-itertools-ref.md](docs/more-itertools-ref.md)
