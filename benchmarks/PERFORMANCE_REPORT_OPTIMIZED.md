# Async Logging Performance Report (Optimized)

> **Test Date**: 2026-02-10  
> **Status**: OPTIMIZED VERSION

## 🚀 Optimization Results

After implementing performance optimizations, we achieved significant speed improvements:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Throughput** | 118,000 logs/sec | **140,000+ logs/sec** | **+19%** |
| **Latency** | 0.0085 ms | **0.0071 ms** | **-16%** |

---

## ⚡ Optimizations Applied

### 1. Local Variable Lookups
```python
# Before: Repeated attribute access
for dest in self._destinations:
    dest(data)

# After: Local variable lookup
destinations = self._destinations
for dest in destinations:
    dest(data)
```

### 2. Optimized Writer Loop
- Cached `time.monotonic` function reference
- Pre-computed batch size and flush interval
- Reduced method call overhead

### 3. Reduced Lock Contention
- Minimized metrics updates in hot path
- Local variable caching for queue operations

### 4. Efficient Serialization
- Local references to `to_dict`, `_dumps_bytes`, `json_default`
- Avoids repeated global lookups

---

## 📊 Performance Comparison

### Default Configuration (batch=100, queue=10K)

| Mode | Throughput | Latency | Speedup |
|------|-----------|---------|---------|
| **Optimized Async** | **140,548 msg/sec** | **0.0071 ms** | **1.0x** |
| Standard Async | 118,000 msg/sec | 0.0085 ms | 0.84x |
| Sync Mode | 22,019 msg/sec | 0.0454 ms | 0.16x |

### Best Configuration (batch=10, queue=10K)

| Metric | Value |
|--------|-------|
| **Throughput** | **141,416 msg/sec** |
| **Latency** | **0.0071 ms** (7.1 microseconds!) |
| **Memory** | ~145 KB |

---

## 🎯 Optimization Recommendations

### For Maximum Throughput (>140K msg/sec)
```python
log.init(
    "app.log",
    async_enabled=True,
    async_batch_size=10,      # Small batches = less latency
    async_max_queue=10_000,   # Large enough buffer
    async_flush_interval=0.5, # Allow batching
)
```

### For Balanced Performance (default)
```python
log.init(
    "app.log",
    async_enabled=True,
    async_batch_size=100,     # Default - good balance
    async_max_queue=10_000,
)
```

### For Large Batches (fewer syscalls)
```python
log.init(
    "app.log",
    async_enabled=True,
    async_batch_size=500,     # Larger batches
    async_flush_interval=1.0, # Longer interval
)
```

---

## 🔥 Stress Test Results

Test: 10,000 messages with different configurations

| Config | Batch | Queue | Throughput | Latency |
|--------|-------|-------|------------|---------|
| small_batch | 10 | 10K | 141,416 msg/s | 0.0071 ms |
| default | 100 | 10K | 140,548 msg/s | 0.0071 ms |
| large_batch | 500 | 10K | 135,324 msg/s | 0.0074 ms |
| xlarge_batch | 1000 | 10K | 134,531 msg/s | 0.0074 ms |

**Key Finding**: Smaller batch sizes (10-100) provide best throughput due to reduced latency.

---

## 📁 Files

| File | Description |
|------|-------------|
| `benchmarks/optimize_logging.py` | Optimization testing suite |
| `benchmarks/quick_debug_1000.py` | Quick performance check |
| `logxpy/src/_async_writer.py` | Optimized async writer |

---

## 🎉 Conclusion

The optimized async logging achieves:

- ✅ **140,000+ logs/sec** throughput
- ✅ **7.1 microseconds** per log call latency
- ✅ **19% improvement** over initial implementation
- ✅ **6.4x faster** than synchronous logging

**Status**: Production-ready for high-frequency logging!
