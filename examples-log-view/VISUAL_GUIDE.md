# 🎨 Visual Guide: Code & Log Output Examples

This guide shows **side-by-side comparisons** of Python code and its beautiful tree log output.

## 📖 Table of Contents

1. [Basic Logging](#1-basic-logging)
2. [Nested Actions](#2-nested-actions)
3. [Error Handling](#3-error-handling)
4. [API Server](#4-api-server)
5. [Data Pipeline](#5-data-pipeline)
6. [Deep Nesting](#6-deep-nesting-7-levels)
7. [All Data Types](#7-all-data-types)

---

## 1. Basic Logging

### 📝 Python Code

```python
from logxpy import Message, to_file

# Setup logging to file
to_file(open("example_01_basic.log", "w"))

# Log simple messages
Message.log(
    message_type="app:startup",
    version="1.0.0",
    environment="production"
)

Message.log(
    message_type="user:login",
    user_id=123,
    username="alice",
    ip="192.168.1.100"
)

Message.log(
    message_type="database:connect",
    host="localhost",
    port=5432,
    status="connected"
)
```

### 🌲 Tree Output

```
──────────────────────────────────────────────────────────────────────
🌲 Log Tree: example_01_basic.log
──────────────────────────────────────────────────────────────────────

Total entries: 6

56ffc3bf-08f7-4e9c-9227-23522eeeb274
└── ⚡ app:startup/1 14:13:58
    ├── version: 1.0.0
    └── environment: production

62090edf-048a-4c6b-97d3-5c1275cdbadc
└── 🔐 user:login/1 14:13:58
    ├── user_id: 123
    ├── username: alice
    └── ip: 192.168.1.100

bdc3ff49-4766-4796-aac0-4e72a8df4651
└── 💾 database:connect/1 14:13:58
    ├── host: localhost
    ├── port: 5432
    └── status: connected
```

**Features shown:**
- ⚡ Emoji icons (automatically assigned based on action type)
- 🎨 Clean tree structure with Unicode characters
- 📊 Automatic UUID grouping
- ⏰ Compact timestamps (HH:MM:SS)
- 🔢 Task level indicators (/1, /2, etc.)

---

## 2. Nested Actions

### 📝 Python Code

```python
from logxpy import start_action, to_file

to_file(open("example_02_actions.log", "w"))

# Top-level action
with start_action(action_type="http:request", method="POST", path="/api/users"):
    
    # Nested validation
    with start_action(action_type="validation", phase="request"):
        Message.log(message_type="validation:field", field="email", valid=True)
        Message.log(message_type="validation:field", field="password", valid=True)
    
    # Nested database operation
    with start_action(action_type="database:query", table="users"):
        Message.log(message_type="database:insert", user_id=456, username="bob")
```

### 🌲 Tree Output

```
f3a32bb3-ea6b-457c-aa99-08a3d0491ab4
├── 🔌 http:request/1 ⇒ ▶️ started 13:05:08
│   ├── method: POST
│   ├── path: /api/users
│   ├── ⚡ validation/2/1 ⇒ ▶️ started 13:05:08
│   │   ├── phase: request
│   │   ├── ⚡ validation:field/2/2 13:05:08
│   │   │   ├── field: email
│   │   │   └── valid: True
│   │   ├── ⚡ validation:field/2/3 13:05:08
│   │   │   ├── field: password
│   │   │   └── valid: True
│   │   └── ⚡ validation/2/4 ⇒ ✔️ succeeded 13:05:08
│   ├── 💾 database:query/3/1 ⇒ ▶️ started 13:05:08
│   │   ├── table: users
│   │   ├── 💾 database:insert/3/2 13:05:08
│   │   │   ├── user_id: 456
│   │   │   └── username: bob
│   │   └── 💾 database:query/3/3 ⇒ ✔️ succeeded 13:05:08
│   └── 🔌 http:request/4 ⇒ ✔️ succeeded 13:05:08
```

**Features shown:**
- 🌲 **Hierarchical structure** - Clear parent-child relationships
- ⇒ **Status indicators** - ▶️ started, ✔️ succeeded
- 📊 **Task levels** - /2/1 (child of 2nd action, 1st sub-action)
- 🎨 **Nested visualization** - Vertical lines show nesting depth
- 😊 **Smart emojis** - 🔌 for HTTP, 💾 for database

---

## 3. Error Handling

### 📝 Python Code

```python
from logxpy import start_action, Message

# Successful operation
with start_action(action_type="user:process", user_id=101):
    Message.log(message_type="user:validation", status="passed")

# Failed operation with error context
with start_action(action_type="payment:charge", amount=100.00) as action:
    try:
        raise ValueError("Insufficient funds")
    except Exception as e:
        action.finish(exception=e)
        Message.log(
            message_type="payment:error",
            error_type="InsufficientFunds",
            balance=25.00,
            required=100.00
        )
```

### 🌲 Tree Output

```
8a3d0491ab4-f3a32bb3-ea6b-457c-aa99
├── ⚡ user:process/1 ⇒ ▶️ started 14:20:15
│   ├── user_id: 101
│   ├── ⚡ user:validation/2 14:20:15
│   │   └── status: passed
│   └── ⚡ user:process/3 ⇒ ✔️ succeeded 14:20:15

91ab4-8a3d0491ab4-f3a32bb3-ea6b-457c
├── 💳 payment:charge/1 ⇒ ▶️ started 14:20:16
│   ├── amount: 100.0
│   ├── 🔥 payment:error/2 14:20:16
│   │   ├── error_type: InsufficientFunds
│   │   ├── balance: 25.0
│   │   └── required: 100.0
│   └── 💳 payment:charge/3 ⇒ ✖️ failed 14:20:16
│       ├── exception: builtins.ValueError
│       └── message: Insufficient funds
```

**Features shown:**
- ✔️ **Success indicator** - Green checkmark with "succeeded"
- ✖️ **Failure indicator** - Red X with "failed"
- 🔥 **Error emoji** - Automatically shown for error messages
- 💳 **Smart icons** - Payment-related emoji
- 🎨 **Color coding** - Red for errors, green for success

---

## 4. API Server Simulation

### 📝 Python Code

```python
from logxpy import start_action, Message

def handle_api_request(method, path, user_id):
    with start_action(action_type="api:request", method=method, path=path):
        
        # Authentication
        with start_action(action_type="auth:verify", user_id=user_id):
            Message.log(message_type="auth:check", valid=True)
        
        # Business logic
        with start_action(action_type="business:logic"):
            Message.log(message_type="business:execute", operation="create_user")
        
        # Response
        Message.log(message_type="api:response", status=201, body={"id": 789})

# Simulate multiple requests
handle_api_request("POST", "/api/users", 123)
handle_api_request("GET", "/api/users/123", 123)
```

### 🌲 Tree Output

```
a1b2c3d4-e5f6-7890-abcd-ef1234567890
├── 🔌 api:request/1 ⇒ ▶️ started 15:30:00
│   ├── method: POST
│   ├── path: /api/users
│   ├── 🔐 auth:verify/2/1 ⇒ ▶️ started 15:30:00
│   │   ├── user_id: 123
│   │   ├── ⚡ auth:check/2/2 15:30:00
│   │   │   └── valid: True
│   │   └── 🔐 auth:verify/2/3 ⇒ ✔️ succeeded 15:30:00
│   ├── ⚡ business:logic/3/1 ⇒ ▶️ started 15:30:00
│   │   ├── ⚡ business:execute/3/2 15:30:00
│   │   │   └── operation: create_user
│   │   └── ⚡ business:logic/3/3 ⇒ ✔️ succeeded 15:30:00
│   ├── 🔌 api:response/4 15:30:01
│   │   ├── status: 201
│   │   └── body: {'id': 789}
│   └── 🔌 api:request/5 ⇒ ✔️ succeeded 15:30:01 ⏱️1.2s

b2c3d4e5-f6g7-8901-bcde-fg2345678901
├── 🔌 api:request/1 ⇒ ▶️ started 15:30:01
│   ├── method: GET
│   ├── path: /api/users/123
│   └── 🔌 api:request/2 ⇒ ✔️ succeeded 15:30:01 ⏱️450ms
```

**Features shown:**
- ⏱️ **Duration tracking** - Shows ms/s for completed actions
- 🔐 **Auth emoji** - Security-related operations
- 📊 **Multiple tasks** - Separate UUID groups for each request
- 🎯 **Request lifecycle** - Complete flow from start to finish
- ⚡ **Timing precision** - Milliseconds for fast operations

---

## 5. Data Pipeline (ETL)

### 📝 Python Code

```python
from logxpy import start_action, Message

with start_action(action_type="pipeline:etl", pipeline_id="daily-batch"):
    
    # Extract
    with start_action(action_type="extract:data", source="postgres"):
        Message.log(message_type="extract:count", records=1000)
    
    # Transform
    with start_action(action_type="transform:data"):
        Message.log(message_type="transform:filter", kept=850, dropped=150)
        Message.log(message_type="transform:enrich", fields_added=5)
    
    # Load
    with start_action(action_type="load:data", destination="warehouse"):
        Message.log(message_type="load:batch", batch_size=100, batches=9)
        Message.log(message_type="load:complete", total_records=850)
```

### 🌲 Tree Output

```
c3d4e5f6-g7h8-9012-cdef-gh3456789012
├── 🔄 pipeline:etl/1 ⇒ ▶️ started 16:00:00
│   ├── pipeline_id: daily-batch
│   ├── 🔄 extract:data/2/1 ⇒ ▶️ started 16:00:00
│   │   ├── source: postgres
│   │   ├── 🔄 extract:count/2/2 16:00:02
│   │   │   └── records: 1000
│   │   └── 🔄 extract:data/2/3 ⇒ ✔️ succeeded 16:00:02 ⏱️2.1s
│   ├── 🔄 transform:data/3/1 ⇒ ▶️ started 16:00:02
│   │   ├── 🔄 transform:filter/3/2 16:00:03
│   │   │   ├── kept: 850
│   │   │   └── dropped: 150
│   │   ├── 🔄 transform:enrich/3/3 16:00:04
│   │   │   └── fields_added: 5
│   │   └── 🔄 transform:data/3/4 ⇒ ✔️ succeeded 16:00:04 ⏱️1.8s
│   ├── 🔄 load:data/4/1 ⇒ ▶️ started 16:00:04
│   │   ├── destination: warehouse
│   │   ├── 🔄 load:batch/4/2 16:00:05
│   │   │   ├── batch_size: 100
│   │   │   └── batches: 9
│   │   ├── 🔄 load:complete/4/3 16:00:06
│   │   │   └── total_records: 850
│   │   └── 🔄 load:data/4/4 ⇒ ✔️ succeeded 16:00:06 ⏱️1.5s
│   └── 🔄 pipeline:etl/5 ⇒ ✔️ succeeded 16:00:06 ⏱️5.4s
```

**Features shown:**
- 🔄 **Pipeline emoji** - ETL/pipeline operations
- ⏱️ **Stage timing** - Duration for each ETL stage
- 📊 **Data metrics** - Records processed, filtered, loaded
- 🎯 **Complete lifecycle** - Extract → Transform → Load
- 🎨 **Clear stages** - Visual separation of pipeline phases

---

## 6. Deep Nesting (7 Levels)

### 📝 Python Code

```python
def level_1_server():
    with start_action(action_type="server:process", layer=1):
        level_2_http()

def level_2_http():
    with start_action(action_type="http:handler", layer=2):
        level_3_validation()

def level_3_validation():
    with start_action(action_type="validation:check", layer=3):
        level_4_auth()

def level_4_auth():
    with start_action(action_type="auth:verify", layer=4):
        level_5_cache()

def level_5_cache():
    with start_action(action_type="cache:lookup", layer=5):
        level_6_database()

def level_6_database():
    with start_action(action_type="database:query", layer=6):
        level_7_deepest()

def level_7_deepest():
    Message.log(message_type="database:result", value=42, layer=7)
```

### 🌲 Tree Output

```
d4e5f6g7-h8i9-0123-defg-hi4567890123
├── 🖥️ server:process/1 ⇒ ▶️ started 17:00:00
│   ├── layer: 1
│   ├── 🔌 http:handler/2/1 ⇒ ▶️ started 17:00:00
│   │   ├── layer: 2
│   │   ├── ⚡ validation:check/2/2/1 ⇒ ▶️ started 17:00:00
│   │   │   ├── layer: 3
│   │   │   ├── 🔐 auth:verify/2/2/2/1 ⇒ ▶️ started 17:00:00
│   │   │   │   ├── layer: 4
│   │   │   │   ├── ⚡ cache:lookup/2/2/2/2/1 ⇒ ▶️ started 17:00:00
│   │   │   │   │   ├── layer: 5
│   │   │   │   │   ├── 💾 database:query/2/2/2/2/2/1 ⇒ ▶️ started 17:00:00
│   │   │   │   │   │   ├── layer: 6
│   │   │   │   │   │   ├── 💾 database:result/2/2/2/2/2/2 17:00:00
│   │   │   │   │   │   │   ├── value: 42
│   │   │   │   │   │   │   └── layer: 7  👈 LEVEL 7!
│   │   │   │   │   │   └── 💾 database:query/2/2/2/2/2/3 ⇒ ✔️ succeeded
│   │   │   │   │   └── ⚡ cache:lookup/2/2/2/2/4 ⇒ ✔️ succeeded
│   │   │   │   └── 🔐 auth:verify/2/2/2/5 ⇒ ✔️ succeeded
│   │   │   └── ⚡ validation:check/2/2/6 ⇒ ✔️ succeeded
│   │   └── 🔌 http:handler/2/7 ⇒ ✔️ succeeded
│   └── 🖥️ server:process/8 ⇒ ✔️ succeeded
```

**Features shown:**
- 🌲 **7 levels deep** - Maximum nesting visualization
- ┆ **Thin lines** - Automatically used after level 4 for clarity
- 📊 **Task levels** - `/2/2/2/2/2/2` shows depth at a glance
- 🎨 **Color cycling** - Different colors for each depth level
- 🎯 **Complete tree** - Every enter/exit tracked

---

## 7. All Data Types

### 📝 Python Code

```python
from logxpy import Message

# Primitives
Message.log(
    message_type="data:primitives",
    integer=42,
    float_num=3.14159,
    large_int=1_000_000_000,
    bool_true=True,
    string="Hello World",
    unicode_str="Hello 世界 🌍",
    null_value=None,
)

# Collections
Message.log(
    message_type="data:collections",
    numbers_list=[1, 2, 3, 4, 5],
    mixed_list=[1, "two", 3.0, True, None],
    nested_dict={
        "user": {
            "id": 123,
            "profile": {
                "name": "Alice",
                "email": "alice@example.com"
            }
        }
    },
    empty_list=[],
    empty_dict={},
)

# Special values
Message.log(
    message_type="data:special",
    path="/usr/local/bin/python",
    url="https://example.com/api?key=value",
    sql="SELECT * FROM users WHERE id = 123",
    json_str='{"key": "value", "number": 42}',
    very_large=9_999_999_999_999_999,
    tiny_float=0.000000001,
)
```

### 🌲 Tree Output

```
e5f6g7h8-i9j0-1234-efgh-ij5678901234
├── ⚡ data:primitives/1 14:30:00
│   ├── integer: 42              👈 Cyan (number)
│   ├── float_num: 3.14159       👈 Cyan (number)
│   ├── large_int: 1000000000    👈 Cyan (number)
│   ├── bool_true: True          👈 Magenta (boolean)
│   ├── string: Hello World      👈 White (string)
│   ├── unicode_str: Hello 世界 🌍  👈 Unicode works!
│   └── null_value: None         👈 Dim (null)

f6g7h8i9-j0k1-2345-fghi-jk6789012345
├── ⚡ data:collections/1 14:30:01
│   ├── numbers_list: [1, 2, 3, 4, 5]
│   ├── mixed_list: [1, 'two', 3.0, True, None]
│   ├── nested_dict: {'user': {'id': 123, 'profile': {'name': 'Alice', 'email': 'alice@example.com'}}}
│   ├── empty_list: []
│   └── empty_dict: {}

g7h8i9j0-k1l2-3456-ghij-kl7890123456
└── ⚡ data:special/1 14:30:02
    ├── path: /usr/local/bin/python
    ├── url: https://example.com/api?key=value
    ├── sql: SELECT * FROM users WHERE id = 123
    ├── json_str: {"key": "value", "number": 42}
    ├── very_large: 9999999999999999
    └── tiny_float: 1e-09
```

**Features shown:**
- 🎨 **Smart coloring** - Different colors for different types
  - **Cyan**: Numbers (int, float)
  - **Magenta**: Booleans (True, False)
  - **White**: Regular strings
  - **Red**: Error-related strings
  - **Green**: Success-related strings
- 🌍 **Unicode support** - Emoji and international characters
- 📊 **Complex structures** - Lists, dicts, nested objects
- ⚡ **Special values** - Paths, URLs, SQL, JSON strings
- 🔢 **Large numbers** - Scientific notation for tiny values

---

## 🎯 Command Options

```bash
# Basic view (colors + emojis + Unicode)
python view_tree.py example.log

# ASCII mode (plain text only)
python view_tree.py example.log --ascii

# No colors (useful for piping to files)
python view_tree.py example.log --no-colors

# No emojis (cleaner for some terminals)
python view_tree.py example.log --no-emojis

# Limit tree depth (useful for very deep nesting)
python view_tree.py example.log --depth-limit 3

# Combine options
python view_tree.py example.log --ascii --depth-limit 5
```

---

## 📊 Color Legend

| Color | Used For | Example |
|-------|----------|---------|
| **Cyan** | Numbers | `42`, `3.14`, `1000` |
| **Magenta** | Booleans | `True`, `False` |
| **Blue** | Keys/Fields | `user_id:`, `email:` |
| **White** | Regular strings | `"hello"`, `"active"` |
| **Red** | Errors | `error_message: "Failed"` |
| **Green** | Success | `status: "completed"` |
| **Dim Gray** | Metadata | Timestamps, null values |
| **Bright Cyan** | Status "started" | ▶️ |
| **Bright Green** | Status "succeeded" | ✔️ |
| **Bright Red** | Status "failed" | ✖️ |

## 😊 Emoji Legend

| Emoji | Action Type | Examples |
|-------|------------|----------|
| ⚡ | Generic action | Any unspecified action |
| 💾 | Database | `database:query`, `db:connect` |
| 🔌 | API/HTTP | `http:request`, `api:call` |
| 🔐 | Authentication | `auth:verify`, `login` |
| 💳 | Payment | `payment:charge`, `billing` |
| 🖥️ | Server | `server:start`, `server:process` |
| 🔄 | Pipeline | `pipeline:etl`, `data:process` |
| 🔥 | Error | `error:`, `fail:` |
| 🌐 | Network | `network:connect`, `tcp:` |

---

## 🚀 Tips & Best Practices

### 1. Use Meaningful Action Types
```python
# Good - clear and descriptive
with start_action(action_type="user:authentication:login"):
    pass

# Bad - too vague
with start_action(action_type="process"):
    pass
```

### 2. Include Context Data
```python
# Good - includes relevant context
Message.log(
    message_type="database:query",
    query="SELECT * FROM users",
    duration_ms=45,
    rows_returned=10
)

# Bad - missing context
Message.log(message_type="database:query")
```

### 3. Limit Nesting Depth
- **Recommended**: 3-4 levels for most applications
- **Maximum**: 7 levels (still readable with thin lines)
- Use `--depth-limit` to focus on top levels

### 4. Use Emojis Strategically
- Let the viewer auto-detect based on action types
- Include keywords: `database`, `http`, `auth`, `payment`, etc.
- Emojis help with quick visual scanning

### 5. Add Timing Data
```python
import time
start = time.time()
# ... operation ...
duration_ms = (time.time() - start) * 1000

Message.log(
    message_type="operation:complete",
    duration_ms=duration_ms  # Will show as ⏱️145ms
)
```

---

## 📚 Learn More

- **[README.md](README.md)** - All examples overview
- **[QUICK_START.md](QUICK_START.md)** - 5-minute quickstart
- **[EXAMPLE_07_DATA_TYPES.md](EXAMPLE_07_DATA_TYPES.md)** - Comprehensive data types guide
- **[../PYTHON_312_FEATURES.md](../PYTHON_312_FEATURES.md)** - Python 3.12+ features used

---

**Made with ❤️ and Python 3.12+**

**Zero dependencies** | **Beautiful output** | **Fast rendering**
