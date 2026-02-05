# logxpy-tree2

[![CI](https://github.com/jonathanj/eliottree/workflows/CI/badge.svg)](https://github.com/jonathanj/eliottree/actions)
[![codecov](https://codecov.io/gh/jonathanj/eliottree/branch/main/graph/badge.svg)](https://codecov.io/gh/jonathanj/eliottree)
[![PyPI version](https://badge.fury.io/py/logxpy-tree.svg)](https://pypi.org/project/logxpy-tree/)
[![Python versions](https://img.shields.io/pypi/pyversions/logxpy-tree.svg)](https://pypi.org/project/logxpy-tree/)

Render [Eliot](https://github.com/scatterhq/logxpy) logs as an ASCII tree.

## Example

Given this Eliot log output:

```json
{"dump": "/home/user/dump_files/20150303/1425356936.28_Client_req.xml", "timestamp": 1425356936.278875, "uri": "http://example.org/soap", "action_status": "started", "task_uuid": "f3a32bb3-ea6b-457c-aa99-08a3d0491ab4", "action_type": "app:soap:client:request", "soapAction": "a_soap_action", "task_level": [1]}
{"timestamp": 1425356937.516579, "task_uuid": "f3a32bb3-ea6b-457c-aa99-08a3d0491ab4", "action_type": "app:soap:client:success", "action_status": "started", "task_level": [2, 1]}
{"task_uuid": "f3a32bb3-ea6b-457c-aa99-08a3d0491ab4", "action_type": "app:soap:client:success", "dump": "/home/user/dump_files/20150303/1425356937.52_Client_res.xml", "timestamp": 1425356937.517077, "action_status": "succeeded", "task_level": [2, 2]}
{"status": 200, "task_uuid": "f3a32bb3-ea6b-457c-aa99-08a3d0491ab4", "task_level": [3], "action_type": "app:soap:client:request", "timestamp": 1425356937.517161, "action_status": "succeeded"}
```

`logxpy-tree` produces:

```text
f3a32bb3-ea6b-457c-aa99-08a3d0491ab4
└── app:soap:client:request/1 ⇒ started 2015-03-03 04:28:56 ⧖ 1.238s
    ├── dump: /home/user/dump_files/20150303/1425356936.28_Client_req.xml
    ├── soapAction: a_soap_action
    ├── uri: http://example.org/soap
    ├── app:soap:client:success/2/1 ⇒ started 2015-03-03 04:28:57 ⧖ 0.000s
    │   └── app:soap:client:success/2/2 ⇒ succeeded 2015-03-03 04:28:57
    │       └── dump: /home/user/dump_files/20150303/1425356937.52_Client_res.xml
    └── app:soap:client:request/3 ⇒ succeeded 2015-03-03 04:28:57
        └── status: 200
```

## Installation

```bash
pip install logxpy-tree2
```

## Usage

### Basic usage

```bash
# Render a log file
logxpy-tree2 logxpy.log

# Pipe from another command
tail -f logxpy.log | logxpy-tree2

# Filter by task UUID
logxpy-tree2 -u f3a32bb3-ea6b-457c-aa99-08a3d0491ab4 logxpy.log
```

### Filtering

```bash
# Filter by date range
logxpy-tree2 --start 2024-01-01T00:00:00 --end 2024-01-02T00:00:00 logxpy.log

# Filter using JMESPath query
logxpy-tree2 --select "action_type == \`app:soap:client:request\`" logxpy.log

# Multiple filters (AND logic)
logxpy-tree --select "action_status == \`failed\`" --select "error == \`true\`" logxpy.log
```

### Output options

```bash
# Use ASCII characters instead of Unicode
logxpy-tree2 --ascii logxpy.log

# Disable colors
logxpy-tree2 --color never logxpy.log

# Limit field length
logxpy-tree2 --field-limit 50 logxpy.log

# Use local timezone instead of UTC
logxpy-tree2 --local-timezone logxpy.log
```

### Configuration file

Create `~/.config/logxpy-tree2/config.json`:

```json
{
  "color": "auto",
  "field_limit": 100,
  "theme": "dark"
}
```

## Python API

```python
from logxpy_cli_view import render_tasks, tasks_from_iterable
import json

# Parse Eliot log messages
tasks = tasks_from_iterable([
    json.loads(line)
    for line in open("logxpy.log")
])

# Render to stdout
render_tasks(
    write=print,
    tasks=tasks,
    human_readable=True,
    colorize_tree=True,
)
```

## Development

```bash
# Clone the repository
git clone https://github.com/jonathanj/eliottree.git
cd eliottree

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src

# Run type checker
mypy src/logxpy_cli_view
```

## Requirements

- Python 3.9+

## License

MIT License - see [LICENSE](LICENSE) file.
