# logxpy-cli-view

[![Python versions](https://img.shields.io/pypi/pyversions/logxpy-cli-view.svg)](https://pypi.org/project/logxpy-cli-view/)

Render [LogXPy](https://github.com/Maziar123/log-x-py) logs as an ASCII tree.

Forked from [eliottree](https://github.com/jonathanj/eliottree) by Jonathan Jacobs.
Modernized with new features and integrated with the LogXPy ecosystem.

## Example

Given this LogXPy log output:

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
pip install logxpy-cli-view
```

## Usage

### Basic usage

```bash
# Render a log file
logxpy-view app.log

# Pipe from another command
tail -f app.log | logxpy-view

# Filter by task UUID
logxpy-view -u f3a32bb3-ea6b-457c-aa99-08a3d0491ab4 app.log
```

### Filtering

```bash
# Filter by date range
logxpy-view --start 2024-01-01T00:00:00 --end 2024-01-02T00:00:00 app.log

# Filter using JMESPath query
logxpy-view --select "action_type == \`app:soap:client:request\`" app.log

# Multiple filters (AND logic)
logxpy-view --select "action_status == \`failed\`" --select "error == \`true\`" app.log
```

### Output options

```bash
# Use ASCII characters instead of Unicode
logxpy-view --ascii app.log

# Disable colors
logxpy-view --color never app.log

# Limit field length
logxpy-view --field-limit 50 app.log

# Use local timezone instead of UTC
logxpy-view --local-timezone app.log
```

### Configuration file

Create `~/.config/logxpy-cli-view/config.json`:

```json
{
  "color": "auto",
  "field_limit": 100,
  "theme": "dark"
}
```

## 🎨 Color Rendering from LogXPy

`logxpy-cli-view` supports rendering foreground/background colors from LogXPy log entries:

```python
from logxpy import log

# Set colors that will be rendered by the CLI viewer
log.set_foreground("cyan")
log.info("This renders with cyan text")

log.set_background("yellow").set_foreground("black")
log.error("Black text on yellow background")

# One-shot colored message
log.colored(
    "╔════════════════════════════════════╗\n"
    "║  ⚠️  IMPORTANT HIGHLIGHTED BLOCK  ║\n"
    "╚════════════════════════════════════╝",
    foreground="black",
    background="yellow"
)

log.reset_foreground().reset_background()
```

When viewed with `logxpy-view`, entries with `logxpy:foreground` and `logxpy:background` fields will render with those colors.

## Python API

```python
from logxpy_cli_view import render_tasks, tasks_from_iterable
import json

# Parse LogXPy log messages
tasks = tasks_from_iterable([
    json.loads(line)
    for line in open("app.log")
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
git clone https://github.com/Maziar123/log-x-py.git
cd log-x-py/logxpy_cli_view

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
