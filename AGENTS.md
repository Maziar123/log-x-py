# AGENTS.md

Guide for AI agents and assistants working on the log-x-py project.

## Project Overview

**log-x-py** is a zero-dependency structured logging library with beautiful tree visualization, built with Python 3.12+ features.

- **Purpose**: Modern structured logging with tree visualization
- **Python Version**: 3.12+ (uses modern features like type aliases, pattern matching, dataclass slots)
- **Dependencies**: Zero for the tree viewer
- **License**: MIT

## Development Environment

- **OS**: Arch Linux
- **Python**: 3.12+ (managed via `uv` and `venv`)
- **Package Manager**: `uv` (preferred) with fallback to `venv`

### Working with Python

Always use `uv` for Python operations:

```bash
# Run with uv
uv run python script.py

# Or activate venv first
source .venv/bin/activate
python script.py
```

## Architecture

### Core Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Tree Viewer** | `examples-log-view/view_tree.py` | Visualize logs as colored trees (499 lines) |
| **Logging Library** | `logxpy/logxpy/` | Core logging functionality |
| **CLI Viewer** | `logxpy_cli_view/` | Full-featured CLI for viewing logs |
| **Examples** | `examples-log-view/example_*.py` | 7 comprehensive examples |
| **Tutorials** | `tutorials/` | 5 detailed tutorials |

### Design Patterns

1. **Dataclasses with slots** - 40% memory reduction
2. **StrEnum** - Type-safe enums for colors/emojis
3. **Pattern matching** - Smart value routing
4. **Type aliases** - `type LogEntry = dict[str, Any]`
5. **Frozen configs** - Immutable settings

## File Structure

```
log-x-py/
├── examples-log-view/          # Main examples and tree viewer
│   ├── view_tree.py           # Core tree viewer (zero deps)
│   ├── example_01_basic.py    # Basic logging example
│   ├── example_02_actions.py  # Nested actions
│   ├── example_03_errors.py   # Error handling
│   ├── example_04_api_server.py   # HTTP simulation
│   ├── example_05_data_pipeline.py # ETL pipeline
│   ├── example_06_deep_nesting.py  # 7-level nesting
│   ├── example_07_all_data_types.py # All data types
│   ├── README.md              # Examples documentation
│   ├── VISUAL_GUIDE.md        # Side-by-side code/output
│   └── QUICK_START.md         # 5-minute guide
├── logxpy/                     # Core logging library
│   └── logxpy/
│       ├── __init__.py        # Main exports
│       ├── _action.py         # Action context management
│       ├── _message.py        # Message logging
│       ├── loggerx.py         # Main logger
│       └── [other modules]
├── logxpy_cli_view/            # CLI viewer
├── tutorials/                  # Detailed tutorials
├── README.md                   # Main documentation
├── PYTHON_312_FEATURES.md      # Modern Python features
└── PROJECT_SUMMARY.md          # Project overview
```

## Coding Conventions

### Python 3.12+ Features Used

```python
# Type aliases (PEP 695)
type LogEntry = dict[str, Any]
type TaskUUID = str

# Pattern matching (PEP 634)
match value:
    case int() | float():
        return colorize_cyan(value)
    case bool():
        return colorize_magenta(value)
    case str() if "error" in value.lower():
        return colorize_red(value)

# Walrus operator (PEP 572)
if task_uuid := entry.get("task_uuid"):
    tasks.setdefault(task_uuid, []).append(entry)

# Dataclasses with slots (PEP 681)
@dataclass(slots=True, frozen=True)
class Colors:
    enabled: bool = True

# StrEnum (PEP 663)
class Color(StrEnum):
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"

# Union syntax (PEP 604)
def process(value: str | Path) -> str:
    ...
```

### Naming Conventions

- **Modules**: `snake_case` (e.g., `view_tree.py`, `_message.py`)
- **Classes**: `PascalCase` (e.g., `Colors`, `EmojiIcon`)
- **Functions/methods**: `snake_case` (e.g., `get_icon`, `colorize`)
- **Constants**: `UPPER_SNAKE_CASE` (rarely used)
- **Private modules**: `_leading_underscore` (e.g., `_action.py`)

### Code Style

- **Type hints**: Required for all public functions
- **Docstrings**: Google style for modules/classes
- **Line length**: Not strictly enforced, aim for readability
- **Imports**: Standard library first, then local imports

## Working with the Codebase

### Running Examples

```bash
cd examples-log-view

# Generate log file
python example_01_basic.py

# View log with tree viewer
python view_tree.py example_01_basic.log

# Run all examples
./run_all.sh

# Run single example with auto-view
./run_single.sh 7
```

### Viewer Options

```bash
# Full features (colors + emoji + Unicode)
python view_tree.py file.log

# ASCII mode (plain text)
python view_tree.py file.log --ascii

# No colors (for piping/files)
python view_tree.py file.log --no-colors

# No emojis
python view_tree.py file.log --no-emojis

# Limit nesting depth
python view_tree.py file.log --depth-limit 3
```

### Testing Changes

1. Modify `view_tree.py` or logging code
2. Run example to generate log: `python example_01_basic.py`
3. View result: `python view_tree.py example_01_basic.log`
4. Compare with expected output

## Key Concepts

### Log Entry Structure

```python
{
    "task_uuid": "abc123-...",  # Groups related entries
    "timestamp": "14:30:00",     # HH:MM:SS format
    "action_type": "http:request",  # Determines emoji
    "level": "/1",               # Hierarchical level
    "status": "succeeded",       # started, succeeded, failed
    "duration_ns": 145000000,    # Nanoseconds
    # ... additional key-value pairs
}
```

### Task Level Format

```
/1              # Root level, 1st action
/2/1            # Child of 2nd action, 1st sub-action
/3/2/1          # 3 levels deep
/3/3/3/3/3/3/3  # 7 levels deep (maximum tested)
```

### Emoji Auto-Detection

Based on `action_type` keywords:
- `database`, `db:`, `query` → 💾
- `http`, `api`, `request` → 🔌
- `auth`, `login` → 🔐
- `payment`, `charge` → 💳
- `server` → 🖥️
- `pipeline`, `etl` → 🔄
- `error`, `fail` → 🔥
- Default → ⚡

### Color Coding

| Type | Color | ANSI Code |
|------|-------|-----------|
| Numbers | Cyan | `\033[36m` |
| Booleans | Magenta | `\033[35m` |
| Keys | Bright Blue | `\033[94m` |
| Error strings | Bright Red | `\033[91m` |
| Success strings | Bright Green | `\033[92m` |
| Regular strings | White | `\033[37m` |
| Timestamps | Dim Gray | `\033[90m` |
| Task UUIDs | Bright Magenta | `\033[95m` |

## Common Tasks

### Adding a New Example

1. Create `example_XX_name.py` in `examples-log-view/`
2. Import from logxpy: `from logxpy import start_action, Message, to_file`
3. Set output: `to_file(open("example_XX_name.log", "w"))`
4. Write logging code
5. Update `README.md` example table
6. Update `run_all.sh` if needed

### Adding a New Color

1. Add to `Color` StrEnum in `view_tree.py`
2. Update `_format_value()` pattern matching
3. Update color documentation in README

### Adding a New Emoji

1. Add to `EmojiIcon` StrEnum in `view_tree.py`
2. Add pattern in `get_icon()` method
3. Update emoji table in README

### Debugging Tree Rendering

1. Enable ASCII mode: `--ascii`
2. Disable colors: `--no-colors`
3. Check log file format: `cat file.log | python -m json.tool`
4. Verify `task_uuid` grouping

## Performance Notes

- **Slots**: -40% memory vs regular dataclasses
- **Pattern matching**: +10% speed vs if/elif chains
- **Frozen dataclasses**: Allow optimizations
- **Zero string concatenation**: Use f-strings only

## Documentation

- [README.md](README.md) - Main project documentation
- [PYTHON_312_FEATURES.md](PYTHON_312_FEATURES.md) - Modern Python features guide
- [examples-log-view/README.md](examples-log-view/README.md) - Examples overview
- [examples-log-view/VISUAL_GUIDE.md](examples-log-view/VISUAL_GUIDE.md) - Code and output examples
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Detailed project statistics

## Contributing

1. **Zero dependencies** - Don't add external packages to `view_tree.py`
2. **Python 3.12+ only** - Use modern features
3. **Type hints** - Required for new code
4. **Tests** - Add examples for new features
5. **Documentation** - Update relevant docs

## Project Goals

- Beautiful, readable log visualization
- Zero dependencies for tree viewer
- Modern Python 3.12+ features
- Type-safe throughout
- Fast and memory efficient
- Clear, maintainable code
