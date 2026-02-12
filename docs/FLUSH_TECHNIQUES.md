# Async Logging Flush Techniques - Comprehensive Guide

> **Research document for high-performance async logging flush mechanisms**
> 
> **Last Updated**: After flush mechanism improvements

> 📚 **Related Documentation**: For complete code-level flow of how logs are written, see [LOGGING_FLOW_SEQUENCE_DIAGRAMS.md](./LOGGING_FLOW_SEQUENCE_DIAGRAMS.md) - specifically:
> - Level 4: Writer Thread flow
> - Level 5: File Write flow
> - Section 8: Sync Mode Fallback

---

## Table of Contents

1. [Fundamental Concepts](#fundamental-concepts)
2. [Flush Techniques](#flush-techniques)
3. [Hybrid Approaches](#3-hybrid-approaches)
4. [Backpressure Strategies](#4-backpressure-strategies)
5. [Comparison Matrix](#5-comparison-matrix)
6. [Current LogXPy Implementation](#6-current-logxpy-implementation)
7. [Implementation Details by File](#7-implementation-details-by-file)
8. [API Reference](#8-api-reference)
9. [References](#9-references)

---

## Fundamental Concepts

### The Flush Problem

In async logging, messages are buffered in memory before writing to disk. The "flush" is the operation that transfers buffered messages to persistent storage.

**Key Trade-offs:**
- **Latency**: Time from `log.info()` to message on disk
- **Throughput**: Messages per second written to disk
- **Reliability**: Guarantee that messages survive crashes
- **Resource Usage**: CPU, memory, disk I/O

### Flush Triggers

| Trigger | When | Use Case |
|---------|------|----------|
| Timer | Fixed interval | Real-time requirements |
| Size | Buffer full | Batch optimization |
| Signal | New message arrival | Low latency |
| Deadline | Max age exceeded | Compliance/Safety |
| On-Demand | Explicit `flush()` call | Critical sections |
| Adaptive | Dynamic based on rate | Variable load |
| Shutdown | Program exit | Cleanup |

---

## Flush Techniques

### 2.1 Timer-Based Flush

**Concept:** Flush at fixed time intervals regardless of queue state.

**Algorithm:**
```python
last_flush = time.now()
while running:
    sleep(flush_interval - (time.now() - last_flush))
    flush_buffer()
    last_flush = time.now()
```

**LogXPy Implementation:**
```python
# File: logxpy/src/_async_writer.py
# Lines: 771-789

timeout = flush_interval - elapsed if elapsed < flush_interval else 0.0

# Wait for message with timeout
try:
    item = q.get(timeout=timeout) if timeout > 0 else q.get_nowait()
except queue.Empty:
    item = None

if item is None:
    # Timeout - flush pending batch
    if batch:
        do_flush(batch)
        batch = []
        last_flush = monotonic()
```

**Pros:**
- Predictable flush intervals
- Simple implementation
- Good for real-time monitoring

**Cons:**
- May delay low-volume messages
- Can lose messages on crash before interval

**Parameters:**
- `flush_interval_ms` in `AsyncConfig` (line 84)

---

### 2.2 Size-Based Flush

**Concept:** Flush when buffer reaches a specific message count.

**Algorithm:**
```python
batch = []
while running:
    msg = queue.get()
    batch.append(msg)
    if len(batch) >= batch_size:
        flush_batch(batch)
        batch = []
```

**LogXPy Implementation:**
```python
# File: logxpy/src/_async_writer.py
# Lines: 800-805

# Add to batch
batch.append(item)
if first_message_time is None:
    first_message_time = monotonic()

# Flush on batch size (disabled if batch_size=0)
if 0 < batch_size <= len(batch):
    do_flush(batch)
    batch = []
    last_flush = monotonic()
    first_message_time = None
```

**Pros:**
- Optimal disk I/O (fewer syscalls)
- Predictable memory usage
- Maximum throughput

**Cons:**
- Unpredictable latency (depends on message rate)
- May delay low-traffic logs indefinitely

**Parameters:**
- `batch_size` in `AsyncConfig` (line 83)

---

### 2.3 On-Demand Flush (NEW)

**Concept:** Application explicitly requests immediate flush via API call.

**LogXPy Implementation:**
```python
# File: logxpy/src/_async_writer.py
# Lines: 402-423

def flush(self, timeout: float = 5.0) -> bool:
    """Force-flush all pending messages without stopping the writer."""
    if not self._running or self._thread is None:
        return True

    self._flush_complete.clear()
    self._flush_requested.set()
    # Wake the writer thread so it sees the request
    with contextlib.suppress(Exception):
        self._queue.put(None, timeout=0)

    return self._flush_complete.wait(timeout)
```

**Writer Loop Handling (Lines 739-758):**
```python
if flush_requested.is_set():
    flush_requested.clear()
    # Drain all remaining items from queue into batch
    while True:
        try:
            queued = q.get_nowait()
        except queue.Empty:
            break
        if queued is not None:
            batch.append(queued)
    if batch:
        do_flush(batch)
        batch = []
        last_flush = monotonic()
    flush_complete.set()
```

**API Usage:**
```python
from logxpy import log

log.init("app.log")
log.info("Critical transaction")
log.flush()  # Force to disk immediately
```

**Pros:**
- Explicit control over flush timing
- Useful for critical operations
- Non-blocking for writer thread

**Cons:**
- Caller must wait for completion
- Requires explicit API call

---

### 2.4 Adaptive Flush (NEW)

**Concept:** Dynamically adjust batch size and interval based on message rate.

**LogXPy Implementation:**
```python
# File: logxpy/src/_async_writer.py
# Lines: 425-445

def enable_adaptive(self, config: AdaptiveFlushConfig | None = None) -> None:
    """Enable adaptive flush that auto-tunes batch size and interval."""
    self._adaptive = _AdaptiveFlushTracker(config or AdaptiveFlushConfig())

# Lines: 731-737 (in _writer_loop)
if adaptive is not None:
    batch_size = adaptive.batch_size
    flush_interval = adaptive.flush_interval
else:
    batch_size = static_batch_size
    flush_interval = static_flush_interval

# Lines: 797-798 (rate tracking)
if adaptive is not None:
    adaptive.record_message()
```

**Configuration:**
```python
from logxpy import log, AdaptiveFlushConfig

config = AdaptiveFlushConfig(
    min_batch_size=10,
    max_batch_size=1000,
    min_flush_interval_ms=10,
    max_flush_interval_ms=1000,
    ema_alpha=0.3,
)
log.init("app.log")
log._async_writer.enable_adaptive(config)
```

**Pros:**
- Auto-tunes for variable load
- Optimizes throughput vs latency
- No manual configuration needed

**Cons:**
- Additional CPU overhead
- More complex to debug

---

### 2.5 Deadline/Timeout Flush

**Concept:** Force flush if oldest message exceeds maximum allowed age.

**LogXPy Implementation:**
```python
# File: logxpy/src/_async_writer.py
# Lines: 760-769

# Check deadline (force flush if oldest message too old)
if deadline_sec and first_message_time:
    time_since_first = now - first_message_time
    if time_since_first >= deadline_sec:
        if batch:
            do_flush(batch)
            batch = []
            last_flush = monotonic()
            first_message_time = None
        continue
```

**Pros:**
- Guaranteed maximum latency
- Safety mechanism for critical logs
- Compliance-friendly

**Cons:**
- Additional timer checks
- May flush small batches

**Parameters:**
- `deadline_ms` in `AsyncConfig` (line 85)

---

### 2.6 Synchronous Flush

**Concept:** Block until message is written to disk.

**LogXPy Implementation:**
```python
# File: logxpy/src/logx.py
# Lines: 716-733

@contextmanager
def sync_mode(self):
    """Temporarily disable async for critical logs."""
    writer_backup = self._async_writer
    self._async_writer = None
    try:
        yield self
    finally:
        self._async_writer = writer_backup
```

**Alternative:** Set `async_en=False` in `init()`
```python
log.init("app.log", async_en=False)  # Fully synchronous
```

**Pros:**
- Zero data loss on crash
- Immediate persistence
- Simple error handling

**Cons:**
- Blocks application
- Lower throughput

---

## 3. Hybrid Approaches

### 3.1 Timer OR Size (LogXPy Default)

Flush when **either** condition is met.

```python
if len(batch) >= size or time_since_flush >= flush_interval:
    flush_batch(batch)
```

**Config:** `size=N, flush=T`

**Use Case:** General-purpose logging

### 3.2 Timer AND On-Demand

Use timer, but support explicit flush for critical moments.

**LogXPy Implementation:**
- Timer in `_writer_loop`
- On-demand via `flush_requested` Event

**Use Case:** Balanced latency and throughput with critical sections

---

## 4. Backpressure Strategies

### 4.1 Block (Default)
```python
def _enqueue_block(self, data):
    q.put(data)  # Blocks until space available
    return True
```
**File:** `_async_writer.py:568-583`

### 4.2 Replace (Circular)
```python
def _enqueue_replace(self, data):
    while q.qsize() >= max_size:
        q.get_nowait()  # Drop oldest
    q.put(data, timeout=0.001)
```
**File:** `_async_writer.py:584-604`

### 4.3 Skip (Drop New)
```python
def _enqueue_skip(self, data):
    if q.qsize() >= max_size:
        return False  # Drop new
    q.put(data, timeout=0.001)
```
**File:** `_async_writer.py:606-618`

### 4.4 Warn (Skip + Alert)
```python
def _enqueue_warn(self, data):
    if q.qsize() >= max_size:
        warnings.warn("Queue full, dropping message")
        return False
```
**File:** `_async_writer.py:620-638`

---

## 5. Comparison Matrix

| Technique | Latency | Throughput | CPU | Memory | Reliability | Complexity |
|-----------|---------|------------|-----|--------|-------------|------------|
| Timer | Medium | Good | Low | Medium | Medium | Low |
| Size | High | Excellent | Low | Medium | Low | Low |
| On-Demand | Very Low | Poor | High | Low | Very High | Low |
| Adaptive | Medium | Excellent | Medium | Medium | Medium | High |
| Deadline | Low | Medium | Medium | Medium | High | Medium |
| Sync | Very Low | Poor | High | Low | Very High | Low |

---

## 6. Current LogXPy Implementation

### Architecture Overview

```
Application Thread:
  log.info() -> serialize -> queue.put(data)
                                    |
                                    | signal (None sentinel)
                                    v
Background Writer Thread (_writer_loop):
  - Check flush_request (on-demand)
  - Check deadline exceeded
  - Check batch_size >= N
  - Check timer expired
  - Check shutdown
            |
            v
  do_flush(batch) -> os.write() -> AsyncFileDestination
```

### Flush Trigger Priority

1. **On-Demand Flush** (`flush_requested.is_set()`) - Immediate
2. **Deadline Exceeded** - Force flush
3. **Batch Size** - Efficient batching
4. **Timer Expired** - Periodic flush
5. **Shutdown** - Final flush

---

## 7. Implementation Details by File

### 7.1 `logxpy/src/_async_writer.py`

| Component | Lines | Description |
|-----------|-------|-------------|
| `AsyncConfig` | 67-98 | Configuration dataclass |
| `AdaptiveFlushConfig` | 120-147 | Adaptive tuning config |
| `QueuePolicy` | 46-59 | Backpressure policies enum |
| `AsyncWriter.flush()` | 402-423 | **On-demand flush** |
| `AsyncWriter.enable_adaptive()` | 425-445 | **Adaptive flush** |
| `_writer_loop()` | 701-815 | Main writer loop |
| `_enqueue_*()` | 568-638 | Backpressure policies |
| `_flush_batch()` | 817-850 | Batch write with fsync |

### 7.2 `logxpy/src/logx.py`

| Component | Lines | Description |
|-----------|-------|-------------|
| `Logger.init()` | 517-612 | Main initialization |
| `Logger.flush()` | 686-698 | **Public flush API** |
| `Logger.sync_mode()` | 716-733 | Temp sync context |

---

## 8. API Reference

### 8.1 Initialization

```python
log.init(
    target="app.log",
    async_en=True,
    queue=10000,
    size=100,
    flush=0.1,
    deadline=None,
    policy="block",
)
```

### 8.2 On-Demand Flush

```python
log.flush(timeout=5.0)  # Force immediate flush
```

### 8.3 Sync Mode Context

```python
with log.sync_mode():
    log.critical("Critical message")
```

### 8.4 Adaptive Flush

```python
from logxpy import AdaptiveFlushConfig

config = AdaptiveFlushConfig(
    min_batch_size=10,
    max_batch_size=1000,
)
log._async_writer.enable_adaptive(config)
```

### 8.5 Configuration Examples

**Mode 1: Balanced**
```python
log.init("app.log", size=100, flush=0.1)
```

**Mode 2: Time Only with On-Demand**
```python
log.init("app.log", size=0, flush="10ms")
log.info("Critical")
log.flush()  # Force immediate
```

**Mode 3: High Throughput with Adaptive**
```python
log.init("app.log", size=1000)
log._async_writer.enable_adaptive()
```

---

## 9. References

- LMAX Disruptor pattern
- Python `queue.SimpleQueue`
- Python `threading.Event`

---

*Document Version: 3.0 - Updated with new flush API*
