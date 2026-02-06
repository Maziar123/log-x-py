# loggerx Python Types Guide & Tree Structure Logging

> Map Python types to optimal loggerx methods + CodeSite-style tree tracing patterns

---

## Python Type → loggerx Method Reference

### Primitive Types

| Python Type | loggerx Method | Example Output |
|-------------|----------------|----------------|
| `str` | `log.info()`, `log()`, `log.send()` | Plain text or `"msg": "text"` |
| `int` | `log.send(key, value)` | `"count": 42` |
| `float` | `log.send(key, value)` | `"price": 99.99` |
| `bool` | `log.send(key, value)` | `"active": true` |
| `None` | `log.send(key, value)` | `"result": null` |
| `bytes` | `log.hex_dump()`, `log.send()` | Hex preview + length |
| `bytearray` | `log.hex_dump()` | Hex preview |

```python
# Primitives - direct key-value
log.info("Status", count=42, active=True, price=99.99)

# Bytes - hex dump for binary
raw_data = b"\x00\x01\x02\x03" * 100
log.hex_dump("Binary data", raw_data)  # Shows hex + ASCII
```

---

### Collections

| Python Type | loggerx Method | Smart Behavior |
|-------------|----------------|----------------|
| `list` | `log.send()`, `log.list()` | Shows len + sample (first/last 5) |
| `tuple` | `log.send()`, `log.list()` | Same as list |
| `set` | `log.send()`, `log.set()` | Shows len + sample, notes unordered |
| `frozenset` | `log.send()`, `log.set()` | Same as set |
| `dict` | `log.send()`, `log.dict()` | Keys + sample values |
| `collections.Counter` | `log.counter()` | Top N most common |
| `collections.deque` | `log.send()` | Shows maxlen + content sample |
| `collections.defaultdict` | `log.send()` | As dict with default factory noted |
| `collections.OrderedDict` | `log.send()` | As dict with order noted |

```python
# Lists - auto-sampling for large collections
users = [{"id": i, "name": f"User{i}"} for i in range(10000)]
log.send("Users", users)
# Output: {"type": "list", "len": 10000, "sample": [...], "schema": {"id": "int", "name": "str"}}

# Dicts - nested support
config = {
    "database": {"host": "localhost", "port": 5432},
    "cache": {"ttl": 3600, "enabled": True}
}
log.send("Config", config)  # Pretty nested structure

# Sets - special handling for uniqueness
tags = {"python", "logging", "devops", "python"}  # 3 unique
log.set("Tags", tags)  # Output: {"type": "set", "len": 3, "sample": ["python", "logging", "devops"]}
```

---

### Object Types

| Python Type | loggerx Method | Behavior |
|-------------|----------------|----------|
| `class instance` | `log.send()`, `log.obj()` | Auto-extract `__dict__`, properties |
| `dataclass` | `log.send()`, `log.dataclass()` | All fields + types |
| `namedtuple` | `log.send()` | Fields + values |
| `Enum` | `log.send()`, `log.enum()` | Name + value |
| `re.Pattern` | `log.send()` | Pattern string + flags |
| `slice` | `log.send()` | start:stop:step |
| `range` | `log.send()` | start, stop, step, len |

```python
from dataclasses import dataclass
from enum import Enum, auto

class Status(Enum):
    PENDING = auto()
    ACTIVE = auto()
    INACTIVE = auto()

@dataclass
class User:
    id: int
    name: str
    email: str
    status: Status = Status.PENDING

user = User(1, "Alice", "alice@example.com", Status.ACTIVE)
log.send("User", user)
# Output:
# {
#   "type": "User",
#   "id": 1,
#   "name": "Alice",
#   "email": "alice@example.com",
#   "status": {"name": "ACTIVE", "value": 2}
# }

log.enum("Status", Status.ACTIVE)  # Output: "ACTIVE" (2)
```

---

### Date/Time Types

| Python Type | loggerx Method | Format |
|-------------|----------------|--------|
| `datetime.datetime` | `log.send()`, `log.datetime()` | ISO 8601 with timezone |
| `datetime.date` | `log.send()`, `log.date()` | YYYY-MM-DD |
| `datetime.time` | `log.send()`, `log.time()` | HH:MM:SS.micros |
| `datetime.timedelta` | `log.send()`, `log.duration()` | Human readable (e.g., "2h 30m") |
| `time.struct_time` | `log.send()` | ISO format |

```python
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
log.datetime("Current time", now)  # 2024-01-15T14:30:00+00:00

duration = timedelta(hours=2, minutes=30, seconds=15)
log.duration("Elapsed", duration)  # "2h 30m 15s"
```

---

### Data Science Types

| Python Type | loggerx Method | Output |
|-------------|----------------|--------|
| `pandas.DataFrame` | `log.df()`, `log.send()` | shape, dtypes, memory, head(5) |
| `pandas.Series` | `log.series()`, `log.send()` | dtype, len, head(5), stats |
| `numpy.ndarray` | `log.tensor()`, `log.send()` | shape, dtype, stats (min/max/mean/std) |
| `numpy.generic` (scalar) | `log.send()` | Value + dtype |
| `torch.Tensor` | `log.tensor()` | shape, dtype, device, stats |
| `tensorflow.Tensor` | `log.tensor()` | shape, dtype, device |
| `jax.Array` | `log.tensor()` | shape, dtype, device |
| `scipy.sparse.*` | `log.sparse()` | Shape, nnz (non-zero), density |
| `xarray.DataArray` | `log.xarray()` | dims, coords, shape, dtype |
| `xarray.Dataset` | `log.xarray()` | Variables, dims, coords |

```python
import pandas as pd
import numpy as np
import torch

# DataFrame
df = pd.DataFrame({
    "id": range(1000),
    "value": np.random.randn(1000),
    "category": np.random.choice(["A", "B", "C"], 1000)
})
log.df("Sales data", df)
# Output:
# Shape: (1000, 3) | Memory: 23.5 KB
# Columns:
#   id          int64
#   value       float64
#   category    object
# Preview (first 5 rows):
#    id     value category
# 0   0 -0.234567        A
# ...

# NumPy array
arr = np.random.rand(100, 100, 3)
log.tensor("Image array", arr)
# Output:
# Shape: (100, 100, 3) | Dtype: float64 | Size: 234KB
# Stats: min=0.0001, max=0.9999, mean=0.5000, std=0.2887

# PyTorch tensor (with GPU support)
tensor = torch.randn(3, 224, 224, device="cuda:0")
log.tensor("Model input", tensor)
# Output:
# Shape: [3, 224, 224] | Dtype: float32 | Device: cuda:0
# Stats: min=-3.21, max=3.45, mean=0.01, std=1.00
```

---

### Image/Media Types

| Python Type | loggerx Method | Output |
|-------------|----------------|--------|
| `PIL.Image.Image` | `log.img()`, `log.send()` | Thumbnail, format, size, mode |
| `numpy.ndarray` (image) | `log.img()` | If 2D/3D array, treats as image |
| `matplotlib.figure.Figure` | `log.plot()`, `log.send()` | Rendered figure |
| `plotly.graph_objects.Figure` | `log.plot()` | Interactive or static render |
| `bytes` (image) | `log.img()` | Auto-detect format, show thumbnail |
| `io.BytesIO` (image) | `log.img()` | Same as bytes |
| `av.AudioFrame` | `log.audio()` | Waveform visualization |
| `av.VideoFrame` | `log.video_frame()` | Frame thumbnail |
| `pydub.AudioSegment` | `log.audio()` | Waveform + duration |

```python
from PIL import Image
import matplotlib.pyplot as plt

# PIL Image
img = Image.open("screenshot.png")
log.img("Screenshot", img, max_size=(512, 512))
# Shows: Format=PNG, Size=(1920, 1080), Mode=RGBA + thumbnail

# Matplotlib plot
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
ax.set_title("Growth curve")
log.plot("Growth analysis", fig)
# Embeds rendered figure in log viewer

# Audio
from pydub import AudioSegment
audio = AudioSegment.from_mp3("sample.mp3")
log.audio("User recording", audio)
# Shows: Duration=30s, Channels=2, Sample rate=44100 + waveform
```

---

### Network/Web Types

| Python Type | loggerx Method | Output |
|-------------|----------------|--------|
| `requests.Response` | `log.response()`, `log.send()` | Status, headers, content preview |
| `httpx.Response` | `log.response()` | Same as requests |
| `aiohttp.ClientResponse` | `log.response()` | Status, headers |
| `urllib3.HTTPResponse` | `log.response()` | Status, headers |
| `http.client.HTTPResponse` | `log.send()` | Status, headers |
| `fastapi.Request` | `log.request()` | Method, URL, headers, body preview |
| `starlette.requests.Request` | `log.request()` | Same as FastAPI |
| `flask.Request` | `log.request()` | Method, URL, form data |
| `pydantic.BaseModel` | `log.send()`, `log.model()` | JSON schema + values |
| `pydantic.ValidationError` | `log.validation_error()` | Errors list |

```python
import requests
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

# HTTP Response
response = requests.get("https://api.example.com/users")
log.response("API call", response)
# Output:
# Status: 200 OK | Time: 245ms
# Headers: {"content-type": "application/json", ...}
# Body preview: [{"id": 1, "name": "Alice"}, ...]

# Pydantic model
user = User(id=1, name="Alice")
log.model("Validated user", user)
# Output:
# {"id": 1, "name": "Alice"}
# Schema: {"id": {"type": "integer"}, "name": {"type": "string"}}
```

---

### File/Path Types

| Python Type | loggerx Method | Output |
|-------------|----------------|--------|
| `pathlib.Path` | `log.path()`, `log.send()` | Absolute path, size, exists, permissions |
| `pathlib.PurePath` | `log.send()` | Path string, parts |
| `os.DirEntry` | `log.send()` | Name, path, is_file, is_dir |
| `io.FileIO` | `log.send()` | Name, mode, closed status |
| `io.BytesIO` | `log.send()` | Buffer length, position |
| `io.StringIO` | `log.send()` | Buffer length, content preview |
| `tempfile.*` | `log.send()` | Path, delete status |
| `mmap.mmap` | `log.send()` | Size, offset, access mode |

```python
from pathlib import Path

config_path = Path("/etc/app/config.yaml")
log.path("Config file", config_path)
# Output:
# Path: /etc/app/config.yaml
# Exists: True
# Size: 4.2 KB
# Modified: 2024-01-15T10:30:00
# Permissions: -rw-r--r--
```

---

### Exception Types

| Python Type | loggerx Method | Output |
|-------------|----------------|--------|
| `BaseException` | `log.send()`, `log.exception()` | Type, message, traceback |
| `Exception` | `log.send()`, `log.exception()` | Same as above |
| `ExceptionGroup` (Py3.11+) | `log.exception_group()` | All nested exceptions |
| `warnings.WarningMessage` | `log.warning()` | Category, message, filename, lineno |
| `traceback.TracebackException` | `log.send()` | Formatted traceback |

```python
# Simple exception
try:
    1 / 0
except ZeroDivisionError as e:
    log.exception("Division failed", e)

# Exception group (Python 3.11+)
async def process_batch(items):
    try:
        async with asyncio.TaskGroup() as tg:
            for item in items:
                tg.create_task(process(item))
    except* ValueError as eg:
        log.exception_group("Validation errors", eg)
        # Shows all ValueErrors from the group
```

---

### Async Types

| Python Type | loggerx Method | Output |
|-------------|----------------|--------|
| `asyncio.Task` | `log.send()` | Name, done, cancelled, exception? |
| `asyncio.Future` | `log.send()` | Done, cancelled, result/exception |
| `asyncio.Queue` | `log.send()` | Maxsize, qsize, empty, full |
| `asyncio.Event` | `log.send()` | Set status |
| `asyncio.Lock` | `log.send()` | Locked status, waiters |
| `asyncio.Semaphore` | `log.send()` | Value, locked |
| `aiohttp.ClientSession` | `log.send()` | Headers, cookies, timeout |

---

### SQL/Database Types

| Python Type | loggerx Method | Output |
|-------------|----------------|--------|
| `sqlalchemy.Query` | `log.query()` | SQL string, parameters |
| `sqlalchemy.engine.Result` | `log.result()` | Row count, column names |
| `sqlite3.Cursor` | `log.send()` | Lastrowid, rowcount |
| `psycopg2.extensions.cursor` | `log.send()` | Query, status |
| `pymongo.cursor.Cursor` | `log.send()` | Query filter, count |
| `redis.Redis` | `log.send()` | Connection info |

```python
from sqlalchemy import select

stmt = select(User).where(User.active == True).limit(10)
log.query("Active users", stmt)
# Output:
# SELECT users.id, users.name, users.active
# FROM users
# WHERE users.active = true
# LIMIT 10
```

---

## Tree Structure Logging (CodeSite-Style)

Modern implementation of CodeSite's visual tree/grouping features.

### Method Entry/Exit Tracing

```python
import loggerx as log

# Visual tree with indentation
@log.tree  # Or @log.logged with tree=True
async def process_order(order_id: int):
    validate_order(order_id)
    payment = await charge_payment(order_id)
    await send_confirmation(payment)

# Output in tree view:
# ▶ process_order(order_id=123) [START]
#   ▶ validate_order(order_id=123) [START]
#   ◀ validate_order [OK] [15ms]
#   ▶ charge_payment(order_id=123) [START]
#   ◀ charge_payment [OK] [245ms]
#   ▶ send_confirmation(payment_id="pi_123") [START]
#   ◀ send_confirmation [OK] [89ms]
# ◀ process_order [OK] [349ms]
```

### Checkpoint Markers

```python
@log.tree
def data_pipeline():
    raw = extract_data()
    log.checkpoint("Extracted", rows=len(raw))
    
    cleaned = transform(raw)
    log.checkpoint("Transformed", rows=len(cleaned))
    
    load(cleaned)
    log.checkpoint("Loaded")

# Output:
# ▶ data_pipeline [START]
#   ✓ Extracted: rows=10000
#   ✓ Transformed: rows=9950
#   ✓ Loaded
# ◀ data_pipeline [OK] [1.2s]
```

### Visual Separators

```python
def batch_process():
    for batch in batches:
        process(batch)
        log.separator("-")  # Visual separator line
        
# Or with style
log.separator("═", title="Phase 1 Complete")
# ═══════════════════ Phase 1 Complete ═══════════════════
```

### Grouping/Indentation Levels

```python
# Manual grouping for complex logic
def complex_operation():
    with log.group("Validation"):
        validate_a()
        validate_b()
        # All logs inside indented under "Validation"
    
    with log.group("Processing", collapsed=True):  # Collapsed by default
        process_a()
        process_b()
    
    with log.group("Cleanup"):
        cleanup()

# Output:
# ▼ Validation
#   Validating A... [OK]
#   Validating B... [OK]
# ▶ Processing (collapsed)
# ▼ Cleanup
#   Cleaning up... [OK]
```

### Call Stack Visualization

```python
@log.stack_trace  # Shows call hierarchy
def deep_function():
    another_function()

# Output shows:
# Call Stack:
#   1. main.py:45 → process_orders()
#   2. orders.py:23 → validate_order()
#   3. validation.py:78 → check_inventory()
#   4. current → deep_function()
```

---

## Best Practice Patterns

### 1. Hierarchical Method Tracing

```python
import loggerx as log

class OrderService:
    @log.traced  # Shorthand for logged with tree visualization
    async def create_order(self, request: OrderRequest) -> Order:
        self._validate(request)
        payment = await self._process_payment(request)
        return await self._save_order(payment)
    
    @log.traced
    def _validate(self, request: OrderRequest) -> None:
        if request.total <= 0:
            raise ValueError("Invalid total")
    
    @log.traced
    async def _process_payment(self, request: OrderRequest) -> Payment:
        return await payment_gateway.charge(request.total)
    
    @log.traced
    async def _save_order(self, payment: Payment) -> Order:
        return await self.db.save(payment)
```

### 2. Phase-Based Logging with Checkpoints

```python
@log.traced
def etl_pipeline(source: str, destination: str):
    phases = ["extract", "transform", "load"]
    
    for phase in phases:
        with log.phase(phase):  # Named group with timing
            if phase == "extract":
                data = extract(source)
                log.checkpoint(f"Extracted {len(data)} records")
            elif phase == "transform":
                data = transform(data)
                log.checkpoint(f"Transformed to {len(data)} records")
            elif phase == "load":
                load(data, destination)
                log.checkpoint(f"Loaded to {destination}")

# Output:
# ▶ etl_pipeline(source="db", destination="warehouse") [START]
#   ▶ extract [START]
#     ✓ Checkpoint: Extracted 10000 records
#   ◀ extract [OK] [1.2s]
#   ▶ transform [START]
#     ✓ Checkpoint: Transformed to 9950 records
#   ◀ transform [OK] [3.5s]
#   ▶ load [START]
#     ✓ Checkpoint: Loaded to warehouse
#   ◀ load [OK] [0.8s]
# ◀ etl_pipeline [OK] [5.5s]
```

### 3. Async Context Propagation with Tree

```python
@log.traced
async def parallel_processing(items: list[int]) -> list[Result]:
    with log.scope(batch_id=str(uuid4())):
        # Context propagates, tree maintains hierarchy
        results = await asyncio.gather(
            *[process_item(item) for item in items],
            return_exceptions=True
        )
        return results

@log.traced
async def process_item(item: int) -> Result:
    # Automatically under parallel_processing in tree
    return await compute(item)
```

### 4. Conditional Tree Collapse

```python
@log.traced(min_duration=0.1)  # Only expand if > 100ms
def fast_operation():
    pass  # Will show collapsed if fast

@log.traced(collapse_success=True)  # Collapse on success, expand on error
def risky_operation():
    if random.random() > 0.5:
        raise ValueError("Failed")
```

### 5. Breadcrumb Trail (For Complex Flows)

```python
def complex_user_flow():
    log.breadcrumb("User login", user_id=123)
    authenticate()
    
    log.breadcrumb("View dashboard", user_id=123)
    show_dashboard()
    
    log.breadcrumb("Click checkout", user_id=123, item="premium_plan")
    start_checkout()
    
    # Later can view full breadcrumb trail
```

### 6. Smart Sampling for High-Frequency Logs

```python
@log.sample(rate=0.01)  # Log only 1% in production
def high_frequency_call():
    pass

@log.sample(every=1000)  # Log every 1000th call
def batch_operation():
    pass

@log.adaptive(target_logs_per_sec=10)  # Auto-adjust rate
def variable_rate_call():
    pass
```

---

## Quick Reference: Tree Features

| Feature | Decorator | Context Manager | Description |
|---------|-----------|-----------------|-------------|
| Method trace | `@log.traced` | - | Entry/exit with tree |
| Checkpoint | - | `log.checkpoint(msg)` | Progress marker |
| Separator | - | `log.separator(char)` | Visual line |
| Group | - | `with log.group(name)` | Indent block |
| Phase | - | `with log.phase(name)` | Named timed group |
| Collapsed group | - | `with log.group(name, collapsed=True)` | Start collapsed |
| Breadcrumb | - | `log.breadcrumb(msg)` | Flow tracking |
| Stack trace | `@log.stack_trace` | - | Call hierarchy |

---

## Type Decision Tree

```
Is it None/str/int/float/bool?
  └─→ log.info("msg", value=x)

Is it bytes/bytearray?
  ├─→ Small: log.send("Data", data)
  └─→ Large: log.hex_dump("Data", data)

Is it list/tuple/set/dict?
  └─→ log.send("Items", items)  # Auto-sampling

Is it a class instance/dataclass?
  └─→ log.send("Obj", obj)  # Auto-dict conversion

Is it pandas/numpy/torch?
  ├─→ DataFrame: log.df("Data", df)
  ├─→ Series: log.series("Data", s)
  └─→ Array/Tensor: log.tensor("Data", arr)

Is it PIL/matplotlib?
  ├─→ PIL Image: log.img("Pic", img)
  └─→ Matplotlib: log.plot("Chart", fig)

Is it HTTP response?
  └─→ log.response("API", resp)

Is it Exception?
  └─→ log.exception("Failed", e)

Is it Path?
  └─→ log.path("File", path)
```

---

*Type-aware logging + CodeSite-style tree tracing for modern Python*
