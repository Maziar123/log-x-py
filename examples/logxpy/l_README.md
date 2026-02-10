# Legacy Eliot Examples

These examples demonstrate the legacy Eliot logging format that LogXPy evolved from. They are kept for reference and compatibility testing.

## Overview

LogXPy is a modern fork of Eliot with Python 3.12+ features. The examples in this folder show the original Eliot API and format.

## Examples

| File | Description |
|------|-------------|
| [asyncio_linkcheck.py](asyncio_linkcheck.py) | AsyncIO link checker with Eliot |
| [cross_process_client.py](cross_process_client.py) | Cross-process client (legacy distributed tracing) |
| [cross_process_server.py](cross_process_server.py) | Cross-process server (legacy distributed tracing) |
| [cross_thread.py](cross_thread.py) | Cross-thread logging |
| [dask_eliot.py](dask_eliot.py) | Dask integration with Eliot |
| [journald.py](journald.py) | Journald logging destination |
| [logfile.py](logfile.py) | Basic log file output |
| [linkcheck.py](linkcheck.py) | Link checker example |
| [rometrip_actions.py](rometrip_actions.py) | Rometrip example with actions |
| [stdlib.py](stdlib.py) | Standard library logging |
| [stdout.py](stdout.py) | stdout logging destination |
| [trio_say.py](trio_say.py) | Trio async framework example |

## Eliot vs LogXPy

### Legacy Eliot Format

```python
# Eliot legacy format (36-char UUIDs)
{
    "timestamp": 1234567890.0,
    "task_uuid": "59b00749-eb24-4c9d-8e9a-123456789abc",
    "task_level": [1],
    "action_type": "http:request",
    "action_status": "succeeded",
    "message_type": "info",
    "message": "Request completed"
}
```

### LogXPy Compact Format

```python
# LogXPy compact format (4-12 char Sqid)
{
    "ts": 1234567890.0,
    "tid": "Xa.1",
    "lvl": [1],
    "at": "http:request",
    "st": "succeeded",
    "mt": "info",
    "msg": "Request completed"
}
```

## Compatibility

The LogXPy parser (`logxy-log-parser`) supports both formats:

```python
from logxy_log_parser import parse_log, LogFormat

# Auto-detect format
entries = parse_log("legacy.log")  # Works with both formats

# Specify format
entries = parse_log("legacy.log", format=LogFormat.LEGACY)
entries = parse_log("modern.log", format=LogFormat.COMPACT)
```

## Migration Notes

To migrate from Eliot to LogXPy:

1. **Install LogXPy**: `pip install log-x-py`
2. **Update imports**: Replace `from eliot import ...` with `from logxpy import ...`
3. **Compact format**: Use new field names (`ts`, `tid`, `mt` instead of `timestamp`, `task_uuid`, `message_type`)
4. **Sqid IDs**: Task IDs are now shorter hierarchical IDs (4-12 chars vs 36-char UUIDs)

For migration details, see [MIGRATION.md](../../docs/MIGRATION.md).
