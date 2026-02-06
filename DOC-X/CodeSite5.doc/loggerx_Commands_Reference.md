# loggerx 4.0 - Zero-Boilerplate Logging

> **Version**: 4.0 | **Python**: 3.12+ | **License**: MIT

```python
import loggerx as log

# Zero config - works immediately
log.info("Hello")

# Or one-line config
log.configure(level="DEBUG", destinations=["console", "otel"])
```

---

## Quick Start

```python
import loggerx as log
from dataclasses import dataclass

@dataclass
class User:
    id: int
    email: str

# Single decorator = entry, exit, timing, args, result, exceptions
@log.logged
async def get_user(user_id: int) -> User:
    return await db.users.find(id=user_id)

# Log any data type automatically
log.send("User loaded", user=User(1, "alice@example.com"))
log.info("Processing complete", count=42, duration_ms=150)
```

---

## Core Logging Methods

### Shorthand `log()` Function

```python
# log() is an alias for log.info() with smart formatting
log("Application started")                           # Simple message
log("User login", user_id=123, role="admin")         # With structured data
log(f"Connected to {host}")                          # f-string support
```

### Level-Based Methods

```python
log.debug("Cache miss", key="user:123")              # Development only
log.info("Request received", method="GET")           # Standard info
log.success("Payment processed", amount=99.99)       # Success (green)
log.note("Remember to backup")                       # Note (blue)
log.warning("Rate limit approaching", limit=1000)    # Warning (yellow)
log.error("Connection failed", error=str(e))         # Error (red)
log.critical("Out of memory", usage="98%")           # Critical (bold red)
log.checkpoint("Phase 1 complete")                   # Progress marker
```

### Universal `send()` Method

```python
# Sends any object with auto-type detection
log.send("Message", data)           # data can be any type
log.send("Count", 42)               # int
log.send("Active", True)            # bool
log.send("User", {"id": 1})         # dict
log.send("Items", [1, 2, 3])        # list

# Smart summaries for large data
log.send("Big DataFrame", df)       # Shows shape + head(5)
log.send("Tensor", tensor)          # Shows shape + dtype + stats
log.send("Image", pil_image)        # Shows thumbnail
```

---

## The `@logged` Decorator (Auto-Everything)

One decorator replaces manual entry/exit logging, timing, and error handling.

```python
@log.logged
async def fetch_data(url: str) -> dict:
    return await http.get(url)

# Auto-output:
# DEBUG → ENTER fetch_data(url="https://api.example.com")
# DEBUG → EXIT fetch_data → {"status": "ok"} [245ms]
```

### Configuration Options

```python
@log.logged(
    level="info",              # Log level for entry/exit
    capture_args=True,         # Log input arguments
    capture_result=True,       # Log return value  
    capture_self=False,        # Skip 'self' in methods (avoid clutter)
    max_depth=3,               # Max depth for nested objects
    max_length=500,            # Truncate long values
    exclude={"password", "token", "secret"},  # Mask sensitive fields
    timer=True,                # Include execution time
    silent_errors=False,       # Don't suppress exceptions
)
def process_payment(user_id: int, amount: Decimal, card: Card) -> Receipt:
    ...
```

### Conditional Logging

```python
@log.logged(when=lambda ctx: ctx.args["amount"] > 1000)
def large_transfer(amount: Decimal, to_account: str):
    """Only logs when amount > 1000"""
    ...

@log.logged(when=lambda ctx: ctx.func.__name__ in DEBUG_FUNCTIONS)
def selective_debug():
    """Only logs in debug mode"""
    ...
```

### Class Methods

```python
class UserService:
    @log.logged(capture_self=False)  # Skip 'self' to reduce noise
    async def get_user(self, user_id: int) -> User:
        return await self.db.get(user_id)
    
    @log.logged(level="debug")
    def validate_email(self, email: str) -> bool:
        return "@" in email
```

---

## Distributed Tracing with `@trace`

OpenTelemetry-compatible tracing with zero configuration.

```python
@log.trace
async def handle_request(request: Request):
    user = await get_user(request.user_id)
    order = await create_order(user)
    return order

# Creates span hierarchy:
# handle_request [200ms]
#   ├── get_user [45ms]
#   └── create_order [150ms]
```

### Custom Span Configuration

```python
@log.trace(
    name="db_query",                          # Custom span name
    kind="server",                            # client/server/producer/consumer/internal
    attributes={"db.system": "postgresql"},   # Static attributes
)
async def query(sql: str) -> list[Row]:
    return await db.execute(sql)
```

### Inline Spans (No Decorator)

```python
async def process():
    with log.span("data_processing") as span:
        data = await fetch()
        span.set_attribute("records", len(data))
        span.set_attribute("source", "api")
        
        with log.span("transformation"):
            result = transform(data)
            
        return result
```

### Adding Span Events

```python
with log.span("upload") as span:
    span.add_event("validation_start")
    validate_file(file)
    span.add_event("upload_start", {"size": len(file)})
    await upload(file)
    span.add_event("upload_complete")
```

---

## Context Propagation

### Automatic Context with `scope()`

```python
from uuid import uuid4

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    with log.scope(
        request_id=request.headers.get("X-Request-ID", str(uuid4())),
        user_id=request.state.user.id,
        path=request.url.path,
    ):
        # All logs inside this block automatically include context
        response = await call_next(request)
        log.info("Request completed", status=response.status_code)
        return response

# In your business logic:
def get_user(user_id: int):
    log.debug("Fetching user")  # Auto-includes request_id, user_id, path
```

### Async Context Propagation

```python
async def main():
    with log.scope(batch_id=str(uuid4())):
        # Context propagates through asyncio.gather automatically
        await asyncio.gather(
            process_batch(1),  # Has batch_id
            process_batch(2),  # Has batch_id
            process_batch(3),  # Has batch_id
        )
```

### Nested Context

```python
with log.scope(service="payment", version="2.1.0"):
    log.info("Service starting")  # service=payment, version=2.1.0
    
    with log.scope(transaction_id="tx-123"):
        log.info("Processing")  # transaction_id + service + version
```

### Manual Context (Builder Pattern)

```python
# Build a pre-configured logger
payment_logger = (
    log.new()
    .ctx(service="payment", version="2.1.0")
    .with_filter(exclude_fields=["cvv", "pin"])
)

payment_logger.info("Initialized")  # Always includes service context
```

---

## Universal Data Type Support

Send any Python object - loggerx automatically detects and formats optimally.

```python
import pandas as pd
import numpy as np
from PIL import Image
import torch

# Primitives
log.send("Count", 42)
log.send("Rate", 3.14)
log.send("Active", True)

# Collections (smart sampling for large collections)
log.send("Users", [{"id": i, "name": f"User{i}"} for i in range(10000)])
# Output: {"type": "list", "len": 10000, "sample": [...], "schema": {...}}

# Objects (auto-inspect)
class Config:
    debug = True
    max_items = 100

log.send("Config", Config())
# Output: {"type": "Config", "debug": True, "max_items": 100}

# Exceptions (auto-capture traceback)
try:
    risky_operation()
except ValueError as e:
    log.send("Operation failed", error=e)
    # Includes: type, message, traceback, local variables
```

### Type-Specific Optimized Methods

```python
# Pandas DataFrame
df = pd.DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})
log.df(df)                    # Shape, dtypes, memory usage, head(5)
log.df(df, title="Users")     # With custom title
log.df(df, max_rows=20)       # Show more rows

# NumPy arrays / PyTorch tensors
arr = np.random.rand(1000, 1000)
log.tensor(arr)               # Shape, dtype, stats (min/max/mean/std)
log.tensor(torch.randn(3, 224, 224))  # PyTorch support

# Images
img = Image.open("screenshot.png")
log.img(img)                  # Shows thumbnail in viewer
log.img(img, max_size=(256, 256))  # Resize before sending

# Matplotlib / Plotly figures
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
log.plot(fig)                 # Embeds figure in log

# Structured data
data = {"nested": {"deep": {"value": 123}}}
log.json(data)                # Pretty-printed JSON
log.tree(data)                # Tree view
log.table([{"a": 1}, {"a": 2}])  # ASCII table
```

---

## Method Chaining (Fluent Interface)

Build complex log operations with clean syntax.

```python
# Chain multiple operations
(
    log.ctx(request_id="req-123")
       .debug("Starting")
       .info("Processing", item_count=42)
       .checkpoint("validation")
       .success("Complete", duration_ms=150)
)

# Pre-configured logger chain
api_logger = (
    log.new()
    .ctx(component="api-gateway")
    .with_level("info")
    .with_destination("otel")
)

api_logger.info("Request", path="/users")
```

---

## Configuration

### 1. Environment Variables (12-Factor)

```bash
export LOGGERX_LEVEL=debug
export LOGGERX_FORMAT=rich              # rich, json, logfmt
export LOGGERX_DESTINATIONS="console,file://app.log,otel://localhost:4317"
export LOGGERX_MASK_FIELDS="password,token,secret,cvv"
```

### 2. pyproject.toml

```toml
[tool.loggerx]
name = "my-app"
level = "info"
format = "rich"
destinations = ["console", "file"]

[tool.loggerx.context]
service = "payment-service"
version = "1.0.0"
environment = "production"

[tool.loggerx.mask]
fields = ["password", "api_key", "credit_card"]
patterns = [
    "\\b\\d{4}-\\d{4}-\\d{4}-\\d{4}\\b",  # Credit cards
    "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"  # Emails
]

[tool.loggerx.file]
path = "logs/app.log"
max_size = "100MB"
max_files = 10
compress = "zstd"
```

### 3. Programmatic Configuration

```python
log.configure(
    level="DEBUG",
    destinations=["console", "file", "otel"],
    format="rich",
    context={"service": "my-app", "version": "1.0.0"},
    mask_fields=["password", "token"],
)
```

### 4. Decorator Configuration

```python
@log.config(level="DEBUG", format="json")
def main():
    ...
```

### 5. Context Manager Configuration

```python
with log.config(destinations=["file"], level="ERROR"):
    # Only errors logged to file in this block
    process_critical()
```

---

## Advanced Patterns

### 1. Pattern Matching (Python 3.10+)

```python
@log.logged
def handle_event(event: dict) -> None:
    match event:
        case {"type": "click", "target": str(t), **rest}:
            log.send("Click", target=t, meta=rest)
        case {"type": "scroll", "delta": int(d)} if d > 100:
            log.send("Big scroll", delta=d)
        case {"type": str(t)}:
            log.debug("Other event", type=t)
        case _:
            log.warning("Unknown event format", event=event)
```

### 2. Walrus Operator for Inline Logging

```python
# Log intermediate values concisely
if (data := fetch_data()) and log.debug("Fetched", rows=len(data)):
    process(data)

# Loop with logging
while (line := file.readline()) and log.trace("Reading", line_no=file.lineno()):
    parse(line)
```

### 3. Generator Progress Tracking

```python
@log.generator("Processing items", every=100)  # Log every 100 items
def process_items(items: list[Item]) -> Iterator[Result]:
    for item in items:
        yield transform(item)

# Output:
# INFO  Processing items: 100/1000 (10%) [ETA: 45s]
# INFO  Processing items: 200/1000 (20%) [ETA: 38s]
```

### 4. Async Iterator Tracking

```python
@log.aiterator("Streaming events", every=50)
async def stream_events(ws: WebSocket) -> AsyncIterator[Event]:
    async for event in ws:
        yield event
```

### 5. Retry with Logging

```python
@log.retry(
    attempts=3,
    delay=1.0,
    backoff=2.0,  # Exponential backoff
    on_retry=lambda n, e: log.warning(f"Retry {n}", error=str(e))
)
async def unreliable_api_call():
    return await fetch_data()
```

### 6. Timing Only (No Args/Result)

```python
@log.timed(metric="db_query_duration")
def query_database(sql: str):
    return db.execute(sql)

# Or inline
with log.timer("heavy_computation") as t:
    result = compute()
    t.label(size=len(result))  # Add custom label
```

---

## Error Handling

### Automatic Exception Capture

```python
@log.logged  # Auto-catches and logs exceptions
def risky_operation():
    raise ValueError("Something went wrong")

# Output includes:
# - Exception type and message
# - Full traceback
# - Local variable values at exception point
```

### Manual Exception Logging

```python
try:
    process()
except ValidationError as e:
    log.error("Validation failed", 
              errors=e.errors(),  # Pydantic-style errors
              input_data=e.model_input)
except Exception as e:
    log.exception("Unexpected error")  # Auto-captures traceback
```

### Exception Groups (Python 3.11+)

```python
async def process_batch(items: list[int]):
    try:
        async with asyncio.TaskGroup() as tg:
            for item in items:
                tg.create_task(process_item(item))
    except* ProcessError as eg:
        log.exception_group("Batch processing failed", eg)
```

---

## Quick Reference Tables

### Decorators

| Decorator | Purpose | When to Use |
|-----------|---------|-------------|
| `@log.logged` | Full logging (entry, exit, args, result, timing, errors) | Most functions |
| `@log.trace` | OpenTelemetry span for distributed tracing | Service boundaries |
| `@log.timed` | Timing only, no args/result | Internal methods |
| `@log.retry` | Log retry attempts | Unstable APIs |
| `@log.generator` | Log generator progress | Large iterations |
| `@log.aiterator` | Log async iterator progress | Streaming data |

### Logging Methods

| Method | Level | Use For |
|--------|-------|---------|
| `log.debug()` | DEBUG | Development, verbose details |
| `log.info()` | INFO | Normal operations |
| `log.success()` | INFO | Successful completions |
| `log.note()` | INFO | Notes/reminders |
| `log.checkpoint()` | INFO | Progress markers |
| `log.warning()` | WARNING | Potential issues |
| `log.error()` | ERROR | Errors, failures |
| `log.critical()` | CRITICAL | System failures |
| `log.send()` | INFO | Universal type logging |

### Data Type Methods

| Method | Best For |
|--------|----------|
| `log.df()` | Pandas DataFrames |
| `log.tensor()` | NumPy/PyTorch/TensorFlow/JAX |
| `log.img()` | PIL Images |
| `log.plot()` | Matplotlib/Plotly figures |
| `log.json()` | Pretty JSON output |
| `log.tree()` | Hierarchical data |
| `log.table()` | List of dicts |

### Context & Scoping

| Pattern | Effect |
|---------|--------|
| `with log.scope(**ctx):` | Set context for block |
| `with log.span(name):` | OpenTelemetry span |
| `log.ctx(**data)` | Add to current context (fluent) |
| `log.new()` | Create fresh logger instance |

---

## Complete Production Example

```python
"""
Production-ready FastAPI service with full observability.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from decimal import Decimal
from typing import AsyncIterator, Annotated
from uuid import uuid4, UUID

import loggerx as log
from fastapi import FastAPI, Request, Header, HTTPException
from pydantic import BaseModel, Field


# Models
class OrderRequest(BaseModel):
    customer_id: int = Field(gt=0)
    items: list[dict] = Field(min_length=1)
    total: Decimal = Field(gt=0)


class Order(BaseModel):
    id: UUID
    customer_id: int
    items: list[dict]
    total: Decimal


# Service layer with auto-logging
class OrderService:
    def __init__(self) -> None:
        self.logger = log.new().ctx(component="order_service")
    
    @log.logged(capture_self=False)
    async def create_order(self, request: OrderRequest) -> Order:
        self.logger.info("Creating order", customer_id=request.customer_id)
        
        with log.span("database_insert"):
            order = Order(
                id=uuid4(),
                customer_id=request.customer_id,
                items=request.items,
                total=request.total
            )
            await self._save(order)
        
        self.logger.success("Order created", order_id=str(order.id))
        return order
    
    @log.retry(attempts=3, on_retry=lambda n, e: log.warning(f"DB retry {n}"))
    async def _save(self, order: Order) -> None:
        # Simulate DB save
        await asyncio.sleep(0.01)
    
    @log.generator("Processing batch", every=100)
    def process_records(self, records: list[dict]) -> Iterator[dict]:
        for record in records:
            yield {"processed": True, **record}


# FastAPI app with logging middleware
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.configure(
        level="INFO",
        destinations=["console", "otel://localhost:4317"],
        mask_fields=["password", "credit_card", "cvv"],
    )
    log.info("Starting up", version=app.version)
    yield
    log.info("Shutting down")


app = FastAPI(title="Order API", version="1.0.0", lifespan=lifespan)
service = OrderService()


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    
    with log.scope(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    ):
        with log.span("http_request") as span:
            try:
                response = await call_next(request)
                span.set_attribute("http.status_code", response.status_code)
                log.info("Request completed", status=response.status_code)
                return response
            except Exception as e:
                span.set_attribute("error", True)
                log.exception("Request failed")
                raise


@app.post("/orders")
@log.logged  # Also works on FastAPI handlers
async def create_order(
    request: OrderRequest,
    x_request_id: Annotated[str | None, Header()] = None
) -> Order:
    return await service.create_order(request)


@app.post("/orders/batch")
async def create_batch(requests: list[OrderRequest]) -> list[Order]:
    with log.scope(batch_size=len(requests)):
        results = []
        for req in requests:
            try:
                order = await service.create_order(req)
                results.append(order)
            except Exception as e:
                log.error("Order failed", error=str(e), customer_id=req.customer_id)
        return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Migration Guide

| From (Classic) | To (loggerx 4.0) |
|----------------|------------------|
| `logging.info("msg")` | `log.info("msg")` or `log("msg")` |
| `logger.debug("x=%s", x)` | `log.debug("x", x=x)` |
| `try: ... except: logger.exception(...)` | `@log.logged` (auto-catches) |
| `logging.Timer(...)` | `@log.timed` or `@log.logged` |
| `structlog.get_logger()` | `log.new()` or `import loggerx as log` |
| Manual OTel span creation | `@log.trace` or `with log.span():` |
| `contextvars.ContextVar` | `with log.scope():` |

---

*Zero boilerplate. Maximum observability.*
