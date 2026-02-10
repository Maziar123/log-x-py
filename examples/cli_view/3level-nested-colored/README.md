# 3-Level Nested Actions with Colors Example

This example demonstrates **3-level nested action hierarchy** with **colored output** in LogXPy.

## Files

| File | Description |
|------|-------------|
| `xxx_3level_nested_colored.py` | Python script generating the example |
| `xxx_3level_nested_colored.log` | Generated log file (compact format) |
| `run-view.sh` | **Run and view in one command** |
| `run.sh` | Generate log only (minimalist) |
| `view.sh` | View log only (minimalist) |
| `capture.sh` | Capture screenshot of output |
| `capture.py` | Screenshot capture script |
| `oneline.html` | HTML output (one-line view) |
| `oneline.png` | Screenshot (one-line view) |
| `tree.html` | HTML output (tree view) |
| `tree.png` | Screenshot (tree view) |
| `README.md` | This documentation |

## Quick Start (One Command)

```bash
# Run and view (generates log if needed)
./run-view.sh              # One-line view (default)
./run-view.sh tree         # Tree view
./run-view.sh nocolor      # No colors
```

## Separate Commands

```bash
# Generate log only
./run.sh

# View existing log
./view.sh              # One-line view (default)
./view.sh tree         # Tree view
./view.sh nocolor      # No colors
```

## Capture Screenshot

```bash
# Capture HTML and PNG screenshot
./capture.sh              # Screenshot one-line view
./capture.sh tree         # Screenshot tree view
```

## Screenshots

### One-Line View (Default)
![One-line view](oneline.png)

### Tree View
![Tree view](tree.png)

## Hierarchy Structure

```
🚀 APPLICATION STARTUP (Yellow block - Level 1)
│
└── api:request (Cyan - Level 1)
    ├── validation:check (Green - Level 2)
    │
    ├── db:transaction (Blue - Level 2)
    │   ├── db:query (Light Blue - Level 3)
    │   ├── db:insert (Light Cyan - Level 3)
    │   └── db:update (Light Green - Level 3)
    │
    ├── payment:process (Magenta - Level 2)
    │   ├── payment:validate_card (Light Magenta - Level 3)
    │   └── payment:create_charge (Light Yellow - Level 3)
    │
    └── notification:send (Red background - Level 2)
```

## Compact Field Names Used

| Compact | Legacy | Example Value |
|---------|--------|---------------|
| `ts` | `timestamp` | `1770570902.594768` |
| `tid` | `task_uuid` | `da8601fb-5064-427e-af4f-5fec4a55da43` or `T3.1` |
| `lvl` | `task_level` | `[3,2,1]` |
| `mt` | `message_type` | `info`, `success`, `error` |
| `at` | `action_type` | `api:request`, `db:query` |
| `st` | `action_status` | `started`, `succeeded`, `failed` |
| `msg` | `message` | `"Processing order"` |
| `fg` | `logxpy:foreground` | `green`, `blue`, `magenta` |
| `bg` | `logxpy:background` | `yellow`, `red`, `green` |

## Color Scheme

| Level | Action Type | Color |
|-------|-------------|-------|
| 1 | Application/Request | Cyan |
| 2 | Validation | Green |
| 2 | Database | Blue |
| 2 | Payment | Magenta |
| 2 | Notification | Red background |
| 3 | Database Queries | Light Blue/Cyan/Green |
| 3 | Payment Steps | Light Magenta/Yellow |

## Sample Output (One-Line View)

```
da8601fb │ api:request/1 ⇒ succeeded ⧖ 0.001s │ method=POST path=/api/v1/orders
├── da8601fb │ validation:check/2/1 ⇒ succeeded ⧖ 0.000s │ schema=order_schema
├── da8601fb │ db:transaction/3/1 ⇒ succeeded ⧖ 0.000s │ isolation=read_committed
│   ├── da8601fb │ db:insert/3/3/1 ⇒ succeeded ⧖ 0.000s │ table=orders
│   ├── da8601fb │ db:query/3/2/1 ⇒ succeeded ⧖ 0.000s │ table=users
│   └── da8601fb │ db:update/3/4/1 ⇒ succeeded ⧖ 0.000s │ table=inventory
├── da8601fb │ payment:process/4/1 ⇒ succeeded ⧖ 0.000s │ amount=99.99 gateway=stripe
│   ├── da8601fb │ payment:create_charge/4/3/1 ⇒ succeeded ⧖ 0.000s
│   └── da8601fb │ payment:validate_card/4/2/1 ⇒ succeeded ⧖ 0.000s
└── da8601fb │ notification:send/5/1 ⇒ succeeded ⧖ 0.000s
```

## Python API Usage

```python
from logxpy import log, to_file, start_action
import logxpy

# Enable compact format
logxpy.COMPACT_FORMAT = True

# Set output file
to_file(open('output.log', 'w'))

# Level 1: Top-level action
with start_action(action_type="api:request", method="POST"):
    log.info("Request received")
    
    # Level 2: Nested action
    with start_action(action_type="db:query", table="users"):
        log.info("Querying database")
        
        # Level 3: Deepest nesting
        with start_action(action_type="db:fetch"):
            log.success("Rows fetched")
```
