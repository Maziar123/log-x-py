# ⚡ Compact Color Demo

Ultra-compact demo showing **deep function nesting tree** with:
- **ONE yellow block** (Application Start)
- **ONE cyan block** (Critical Section)
- **@logged decorator** (3 decorated functions)
- **log.stack_trace()** (error handling)
- **4 levels deep** nesting

## Key Features

| Feature | Implementation | Count |
|---------|---------------|-------|
| **@logged decorator** | `process_item()`, `validate_email()`, `calculate_total()` | 3 functions |
| **log.stack_trace()** | Inside error handler | 1 call |
| **Yellow block** | `set_background("yellow")` | 1 block |
| **Cyan block** | `set_background("cyan")` | 1 block |
| **Max depth** | Nested `start_action()` calls | 4 levels |

## Decorator Usage

```python
from logxpy.decorators import logged

@logged(level="INFO", capture_args=True, capture_result=True)
def process_item(item_id: int, name: str) -> dict:
    log.info("Processing", item_id=item_id)
    return {"id": item_id, "status": "processed"}

# Auto-logs: entry, args, exit, result
result = process_item(101, "Widget")
```

## Stack Trace Usage

```python
try:
    risky_operation()
except ValueError:
    log.error("Failed")
    log.stack_trace(limit=5)  # Shows stack trace
```

## Files

| File | Lines | Purpose |
|------|-------|---------|
| `compact_color_demo.py` | ~120 | Deep nesting + @logged + stack_trace() |
| `compact_parser.py` | ~75 | Parse showing function tree |
| `run_compact.sh` | ~40 | Run pipeline |
| `minimal_color_demo.py` | ~70 | Symlink to complete-example-01 (alt demo) |

## Quick Start

```bash
./run_compact.sh
```

## Output Example

```
✓ 74 entries

Function Tree (4 levels deep):
------------------------------------------------------------
🟡 [ 1] ═══════════════════════        ← YELLOW BLOCK
   [ 2] app:main → started
    ├── [ 3] system:init → started
   [ 4]   System Info                  ← Category inside tree
   [ 5]   Memory Status                ← Category inside tree
   ...
    ├── [23] decorator:demo → started
   [24] Testing @logged decorator
    ├── [25] __main__.process_item → started  ← @logged
        ├── [27] __main__.process_item → succeeded
    ├── [28] __main__.validate_email → started  ← @logged
    ├── [30] __main__.calculate_total → started  ← @logged
    ...
🟦 [35] ═══════════════════════        ← CYAN BLOCK
       ├── [36] payment:charge → started
    ...
    ├── [60] error:test → started
   [61] Testing error + stack_trace()
        ├── [62] risky:op → started
   [66]   Stack Trace                   ← stack_trace()
    ...

Categories: {'Actions': 42, 'System Info': 1, 'Memory': 1, 
  'Checkpoints': 2, 'Stack Traces': 2, 'Errors': 1}
Decorators: @logged (3 functions) | stack_trace() included
```

## Tree Structure

```
🟡 YELLOW BLOCK (App Start)
└── app:main
    ├── system:init
    │   ├── System Info          # Category
    │   └── Memory Status        # Category
    ├── db:connect
    │   └── db:pool              # Level 3
    ├── api:server
    │   └── api:routes
    │       └── api:middleware   # Level 4
    ├── decorator:demo
    │   ├── process_item()       # @logged
    │   ├── validate_email()     # @logged
    │   └── calculate_total()    # @logged
    ├── app:critical
    │   🟦 CYAN BLOCK
    │   └── payment:charge
    │       ├── payment:validate # Level 4
    │       └── payment:fraud    # Level 4
    ├── data:batch
    │   └── data:transform
    │       └── data:validate    # Level 4
    ├── error:test
    │   └── risky:op
    │       └── Stack Trace      # stack_trace()
    └── app:cleanup
```

## Screenshot Note

> 📸 Run `./run_compact.sh` and screenshot the tree view with ANSI colors
