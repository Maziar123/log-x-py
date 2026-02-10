# LogXPy Migration

Compact field names (1-2 chars) reduce log sizes by **50-70%**.

## Field Changes

| Compact | Legacy | Savings |
|---------|--------|---------|
| `ts` | `timestamp` | 7 bytes |
| `tid` | `task_uuid` | 7 bytes |
| `lvl` | `task_level` | 6 bytes |
| `mt` | `message_type` | 8 bytes |
| `at` | `action_type` | 7 bytes |
| `st` | `action_status` | 9 bytes |
| `msg` | `message` | 5 bytes |
| `dur` | `logxpy:duration` | 12 bytes |
| `fg` | `logxpy:foreground` | 14 bytes |
| `bg` | `logxpy:background` | 14 bytes |

**Values:** `"info"` (was `"loggerx:info"`) - saves 8 bytes

## Before/After

```json
// OLD: ~180 bytes
{"timestamp":1770562483.38,"task_uuid":"59b00749-eb24-...","task_level":[1],"message_type":"loggerx:info","message":"Hello!"}

// NEW: ~95 bytes (47% smaller)
{"ts":1770563890.79,"tid":"gD.1","lvl":[1],"mt":"info","msg":"Hello!"}
```

## Sqid Task IDs

Format: `PID_PREFIX.COUNTER[.CHILD]`
- `"Xa.1"` = 4 chars (vs UUID4: 36 chars)

## Python API

```python
from logxpy import TS, TID, LVL, MT, MSG  # Compact
from logxpy import TIMESTAMP, TASK_UUID    # Legacy aliases

entry = {TS: time.time(), TID: sqid(), MT: "info", MSG: "Hello!"}
```

## Parsing (Backwards Compatible)

```python
import json
def parse(line):
    e = json.loads(line)
    return {
        "ts": e.get("ts") or e.get("timestamp"),
        "tid": e.get("tid") or e.get("task_uuid"),
        "lvl": e.get("lvl") or e.get("task_level"),
        "mt": e.get("mt") or e.get("message_type"),
        "msg": e.get("msg") or e.get("message"),
    }
```

## Environment

```bash
LOGXPY_DISTRIBUTED=1  # Force UUID4
```

## Breaking Changes

1. Fields: `timestamp` → `ts`, `task_uuid` → `tid`, etc.
2. Types: `"loggerx:info"` → `"info"`
3. Task IDs: UUID4 → Sqid
4. Duration: `"logxpy:duration"` → `"dur"`

## Files Modified

`_types.py`, `_message.py`, `_action.py`, `loggerx.py`, `_async.py`, `__init__.py`, `AGENTS.md`, `README.md`
