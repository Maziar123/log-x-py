# Sample Log Outputs

This directory contains saved log outputs from the complex examples.

## Files

| File | Example | Description | Lines | Size |
|------|---------|-------------|-------|------|
| `11_ecommerce.log` | E-Commerce Order Processing | Complete order flow with payment & fulfillment | ~150+ | ~170KB |
| `12_banking.log` | Banking Fund Transfer | Fund transfer with compliance checks | ~220+ | ~240KB |
| `13_data_pipeline.log` | Data Pipeline (Async) | ETL pipeline with async operations | ~250+ | ~275KB |

## Format

All logs are in **JSON format** (one JSON object per line), containing:

```json
{
  "timestamp": 1770277592.840312,
  "task_uuid": "f9a50d27-0082-4ecc-b14f-ee59fe33b2f4",
  "task_level": [1],
  "message_type": "loggerx:info",
  "message": "🚀 STARTING ORDER PROCESSING",
  "order_id": 12345,
  "user_id": 789
}
```

## Key Fields

- **timestamp**: Unix timestamp with microseconds precision
- **task_uuid**: Unique identifier linking all logs in a transaction
- **task_level**: Array showing nesting depth (e.g., `[1]`, `[1,1]`, `[1,1,1]`)
- **message_type**: Log level (loggerx:info, loggerx:debug, etc.)
- **action_type**: Function/class name (e.g., "OrderService.process_order")
- **action_status**: "started", "succeeded", or "failed"
- **logxpy:duration**: Execution time in seconds
- Plus custom fields specific to each operation

## Viewing Logs

### View in Terminal
```bash
# Pretty print JSON
cat 11_ecommerce.log | jq '.'

# Filter by message
grep "LEVEL 7" 11_ecommerce.log

# Show only actions
grep "action_type" 12_banking.log | jq -r '.action_type'

# Count log entries
wc -l *.log
```

### View with LoggerX Tree Visualizer
```bash
# Install logxpy_cli_view (the visualizer)
cd ../../logxpy_cli_view
pip install -e .

# Visualize logs
logxpy_cli_view < ../logs/sample_outputs/11_ecommerce.log
```

### Import into Log Analysis Tools
These logs can be imported into:
- **Elasticsearch/Kibana**: Index as JSON documents
- **Splunk**: Parse JSON format
- **Grafana Loki**: Stream as JSON logs
- **CloudWatch**: Send via AWS SDK
- **DataDog**: Send via API

## Re-generating Logs

To regenerate these sample logs:

```bash
cd /mnt/N1/MZ/AMZ/Projects/Prog/a_cross/logxpy_cli_view

# E-Commerce
PYTHONPATH=./logxpy:$PYTHONPATH python logxpy/examples/11_complex_ecommerce.py > logs/sample_outputs/11_ecommerce.log 2>&1

# Banking
PYTHONPATH=./logxpy:$PYTHONPATH python logxpy/examples/12_complex_banking.py > logs/sample_outputs/12_banking.log 2>&1

# Data Pipeline
PYTHONPATH=./logxpy:$PYTHONPATH python logxpy/examples/13_complex_data_pipeline.py > logs/sample_outputs/13_data_pipeline.log 2>&1
```

## Example Queries

### Find all errors
```bash
grep '"message_type":"loggerx:error"' *.log | jq '.'
```

### Track a specific transaction
```bash
# Get task_uuid from first log
TASK_UUID=$(head -1 11_ecommerce.log | jq -r '.task_uuid')

# Show all logs for that transaction
cat 11_ecommerce.log | jq "select(.task_uuid == \"$TASK_UUID\")"
```

### Show execution times
```bash
cat 12_banking.log | jq 'select(.["logxpy:duration"] != null) | {action: .action_type, duration: .["logxpy:duration"]}'
```

### Find deepest nesting level
```bash
cat 11_ecommerce.log | jq '.task_level | length' | sort -n | tail -1
```

## Statistics

Each log file contains approximately:
- **150-250 log entries** per execution
- **7 levels of nesting** (task_level depth)
- **20-40 different action types** (functions/classes)
- **10-15 different message types**

## Notes

- All sensitive fields (passwords, tokens) are masked as `"***"`
- Timestamps are in Unix format (seconds since epoch)
- Task UUIDs are unique per execution
- Duration is measured in seconds with microsecond precision

---

**Generated**: 2026-02-05  
**Format**: JSON Lines (one JSON object per line)  
**Encoding**: UTF-8
