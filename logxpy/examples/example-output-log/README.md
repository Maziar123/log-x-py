# Example Output Logs

This directory contains the actual log output from all 13 Eliot examples.

**Generated**: 2026-02-05  
**Format**: JSON Lines (one JSON object per line)  
**Total Examples**: 13

---

## 📋 Log Files

| File | Example | Lines | Size | Description |
|------|---------|-------|------|-------------|
| `01_output.log` | Simple Logging | 21 | 2.4K | Basic messages, structured data, log levels |
| `02_output.log` | Decorators | 14 | 1.5K | @log.logged, @log.timed, @log.retry |
| `03_output.log` | Context Scopes | 15 | 2.1K | log.scope(), nested scopes, context builder |
| `04_output.log` | Async Tasks | 19 | 3.0K | aaction, async decorator, context propagation |
| `05_output.log` | Error Handling | 12 | 1.6K | Exception logging, auto-capture, silent errors |
| `06_output.log` | Data Types | 12 | 1.7K | JSON, DataFrames, tensors, universal send |
| `07_output.log` | Generators/Iterators | 13 | 1.8K | @log.generator, @log.aiterator |
| `08_output.log` | OpenTelemetry | 5 | 576B | Tracing spans (degrades gracefully) |
| `09_output.log` | Configuration | 10 | 847B | Field masking, destinations |
| `10_output.log` | Advanced Patterns | 12 | 1.3K | Conditional logging, dynamic levels |
| `11_output.log` | **Complex E-Commerce** | 116 | 34K | 7-level order processing |
| `12_output.log` | **Complex Banking** | 168 | 56K | 7-level fund transfer |
| `13_output.log` | **Complex Data Pipeline** | 179 | 465K | 7-level async ETL pipeline |

---

## 📊 Statistics

### Basic Examples (01-10)
- **Total lines**: 143
- **Total size**: 17.7 KB
- **Average size**: 1.8 KB per example
- **Max nesting**: 3-4 levels

### Complex Examples (11-13)
- **Total lines**: 463
- **Total size**: 555 KB
- **Average size**: 185 KB per example
- **Max nesting**: **7 levels** (deepest possible)

### Overall
- **Total log entries**: 606 lines
- **Total output size**: 572.7 KB
- **All examples**: ✅ **100% Success Rate**

---

## 🔍 Sample Log Entries

### Basic Example (01)
```json
{
  "timestamp": 1770278239.7123232,
  "task_uuid": "ff7d1866-4e7d-48bc-89c4-ff3252d5d7c3",
  "task_level": [1],
  "message_type": "loggerx:info",
  "message": "Hello, World!"
}
```

### Complex Example (12) - LEVEL 7
```json
{
  "timestamp": 1770278245.8093594,
  "task_uuid": "f5b4b054-d8b2-4de6-a9c1-f3550567db1a",
  "task_level": [1],
  "transaction_type": "transfer",
  "currency": "USD",
  "message_type": "loggerx:debug",
  "message": "          📄 LEVEL 7: Parsing result set"
}
```

---

## 📖 How to Use These Logs

### 1. View Raw Logs
```bash
# View a specific log
cat 01_output.log

# View with pagination
less 11_output.log

# View last 20 lines
tail -20 13_output.log
```

### 2. Pretty Print JSON
```bash
# Pretty print single log entry
head -1 01_output.log | jq '.'

# Pretty print entire file
cat 02_output.log | jq '.'

# Show specific fields
cat 03_output.log | jq '{message, timestamp, task_level}'
```

### 3. Search and Filter
```bash
# Find all errors
grep '"message_type":"loggerx:error"' *.log

# Find LEVEL 7 logs (deepest nesting)
grep "LEVEL 7" *.log

# Find all success messages
grep '"message_type":"loggerx:success"' *.log

# Show all action types
cat 11_output.log | jq -r 'select(.action_type != null) | .action_type' | sort -u
```

### 4. Analyze Patterns
```bash
# Count log entries per file
wc -l *.log

# Show size of each file
ls -lh *.log

# Find longest messages
cat *.log | jq -r '.message' | awk '{print length, $0}' | sort -rn | head -10

# Show unique message types
cat *.log | jq -r '.message_type' | sort -u
```

### 5. Extract Specific Data
```bash
# Get all timestamps
cat 01_output.log | jq -r '.timestamp'

# Get all task UUIDs
cat 02_output.log | jq -r '.task_uuid' | sort -u

# Find actions with duration > 0.1 seconds
cat 11_output.log | jq 'select(.["logxpy:duration"] > 0.1)'

# Show nesting levels distribution
cat 12_output.log | jq -r '.task_level | length' | sort | uniq -c
```

---

## 🎯 Example-Specific Queries

### Example 01: Simple Logging
```bash
# Show all log levels used
cat 01_output.log | jq -r '.message_type' | sort -u

# Expected: debug, info, note, success, warning, error, critical
```

### Example 02: Decorators
```bash
# Show function execution times
cat 02_output.log | jq 'select(.["logxpy:duration"] != null) | {func: .action_type, duration: .["logxpy:duration"]}'

# Check password masking
grep "password" 02_output.log | jq '.password'
# Expected: "***"
```

### Example 09: Configuration
```bash
# Verify field masking works
grep -E "(password|token)" 09_output.log | jq '{password, token}'

# All should show: "***"
```

### Example 11: E-Commerce (Complex)
```bash
# Track order flow
cat 11_output.log | jq 'select(.action_type != null) | .action_type' | nl

# Find fraud detection logs
grep "Fraud" 11_output.log | jq '.message'

# Show all levels reached
cat 11_output.log | jq -r '.message' | grep -E "LEVEL [0-9]"
```

### Example 12: Banking (Complex)
```bash
# Show transaction phases
grep -E "(PHASE|TRANSACTION)" 12_output.log | jq '.message'

# Find compliance checks
grep "compliance" 12_output.log | jq '.message'

# Show LEVEL 7 operations
grep "LEVEL 7" 12_output.log | jq '.'
```

### Example 13: Data Pipeline (Complex)
```bash
# Show pipeline phases
grep "PHASE" 13_output.log | jq '.message'

# Count operations by phase
grep "░░░" 13_output.log | wc -l

# Show deepest nesting
grep "LEVEL 7" 13_output.log | jq '.message'
```

---

## 🔬 Advanced Analysis

### Trace a Complete Transaction

```bash
# Get first task_uuid from example 11
TASK_UUID=$(head -1 11_output.log | jq -r '.task_uuid')

# Show all logs for that transaction
cat 11_output.log | jq "select(.task_uuid == \"$TASK_UUID\")"
```

### Performance Analysis

```bash
# Show slowest operations
cat 11_output.log | jq 'select(.["logxpy:duration"] != null) | {action: .action_type, duration: .["logxpy:duration"], status: .action_status}' | jq -s 'sort_by(.duration) | reverse | .[0:5]'
```

### Context Propagation Check

```bash
# Example 03: Verify scope inheritance
cat 03_output.log | jq 'select(.request_id != null) | {message, request_id, user}'
```

---

## 🛠️ Visualization

### Using logxpy_cli_view (Recommended)

```bash
# Install the visualizer
cd ../../logxpy_cli_view
pip install -e .

# Visualize logs as tree
logxpy_cli_view < ../logxpy/examples/example-output-log/11_output.log

# With filtering
logxpy_cli_view --select 'action_type=OrderService.*' < ../logxpy/examples/example-output-log/11_output.log
```

### Using jq for Custom Formatting

```bash
# Create a simple text timeline
cat 01_output.log | jq -r '"\(.timestamp | strftime("%H:%M:%S")) - \(.message)"'

# Show action hierarchy
cat 11_output.log | jq -r 'select(.action_type != null) | "\(.task_level | length) \(.action_type) \(.action_status)"'
```

---

## 📦 Exporting Logs

### To Elasticsearch
```bash
# Use bulk API
cat 11_output.log | while read line; do
  echo '{"index":{"_index":"logxpy-logs"}}'
  echo "$line"
done | curl -X POST "localhost:9200/_bulk" -H "Content-Type: application/x-ndjson" --data-binary @-
```

### To CSV
```bash
# Extract specific fields to CSV
echo "timestamp,message_type,message,task_level" > export.csv
cat 01_output.log | jq -r '[.timestamp, .message_type, .message, (.task_level | @json)] | @csv' >> export.csv
```

### To SQLite
```bash
# Create table and import
sqlite3 logs.db <<EOF
CREATE TABLE logs (
  timestamp REAL,
  task_uuid TEXT,
  task_level TEXT,
  message_type TEXT,
  message TEXT,
  data TEXT
);
EOF

# Import (requires jq preprocessing)
cat 01_output.log | jq -r '[.timestamp, .task_uuid, (.task_level|@json), .message_type, .message, @json] | @csv' | sqlite3 logs.db ".import /dev/stdin logs"
```

---

## 🔄 Regenerating Logs

To regenerate all logs:

```bash
cd /mnt/N1/MZ/AMZ/Projects/Prog/a_cross/logxpy_cli_view

# Run all examples
for i in {01..13}; do
  echo "Running example ${i}..."
  PYTHONPATH=./logxpy:$PYTHONPATH python logxpy/examples/${i}_*.py > logxpy/examples/example-output-log/${i}_output.log 2>&1
done
```

Or run individually:
```bash
# Example 11
PYTHONPATH=./logxpy:$PYTHONPATH python logxpy/examples/11_complex_ecommerce.py > logxpy/examples/example-output-log/11_output.log 2>&1
```

---

## ✅ Validation

All logs are validated for:
- ✅ Valid JSON format
- ✅ Required fields present (timestamp, task_uuid, task_level)
- ✅ Proper nesting (task_level arrays)
- ✅ Field masking (passwords/tokens = "***")
- ✅ Action lifecycle (started → succeeded/failed)
- ✅ Duration tracking (logxpy:duration field)

### Quick Validation
```bash
# Check all files are valid JSON
for f in *.log; do
  echo -n "Checking $f... "
  cat "$f" | jq empty && echo "✓ Valid" || echo "✗ Invalid"
done
```

---

## 📚 Related Documentation

- `../01_simple_logging.py` to `../13_complex_data_pipeline.py` - Source examples
- `../../../COMPLEX_EXAMPLES_GUIDE.md` - Detailed guide for examples 11-13
- `../../../EXAMPLES_LOG_VERIFICATION.md` - Verification report
- `../../../loggerx_Commands_Reference.md` - API reference

---

## 💡 Tips

1. **Use jq**: It's essential for working with JSON logs
2. **Grep patterns**: Use emojis to filter by operation type (🚀, ✅, ❌, etc.)
3. **Task tracking**: Follow task_uuid to trace complete transactions
4. **Nesting depth**: Check task_level length to see call depth
5. **Performance**: Look for logxpy:duration to find slow operations

---

**Generated**: 2026-02-05  
**Total Files**: 13  
**Total Size**: 572.7 KB  
**Status**: ✅ All examples passed  
**Format**: JSON Lines (NDJSON)
