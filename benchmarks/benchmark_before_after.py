#!/usr/bin/env python3
"""Benchmark comparing old vs new implementation.

Shows the performance improvement from the optimization work:
- Old: Record + json.dumps() 
- New: build_json_line() with f-strings
"""

import sys
import time
import json
from dataclasses import dataclass

sys.path.insert(0, "/mnt/N1/MZ/AMZ/Projects/Prog/a_cross/log-x-py")

from logxpy.src._types import Level, Record
from logxpy.src._base import now
from logxpy.src._json_line import build_json_line


N = 100_000


def benchmark_old_way():
    """Old way: Record + json.dumps()."""
    start = time.perf_counter()
    
    for i in range(N):
        record = Record(
            timestamp=now(),
            level=Level.INFO,
            message="test",
            fields={"i": i},
            context={},
            task_uuid="test",
            task_level=(1,),
            message_type="info"
        )
        log_line = json.dumps(record.to_dict(), default=str)
    
    elapsed = time.perf_counter() - start
    throughput = N / elapsed
    return elapsed, throughput


def benchmark_new_way():
    """New way: build_json_line()."""
    start = time.perf_counter()
    
    for i in range(N):
        log_line = build_json_line(
            message="test",
            message_type="info",
            task_uuid="test",
            task_level=(1,),
            fields={"i": i},
            timestamp=now(),
        )
    
    elapsed = time.perf_counter() - start
    throughput = N / elapsed
    return elapsed, throughput


def benchmark_with_writer():
    """Benchmark actual writer performance."""
    from logxpy.src._writer import create_writer, WriterType, Mode
    
    # Old way with writer
    writer1 = create_writer("/tmp/bench_old.log", WriterType.BLOCK, Mode.TRIGGER, batch_size=1000)
    start = time.perf_counter()
    for i in range(N):
        record = Record(
            timestamp=now(),
            level=Level.INFO,
            message="test",
            fields={"i": i},
            context={},
            task_uuid="test",
            task_level=(1,),
            message_type="info"
        )
        writer1.send(json.dumps(record.to_dict(), default=str))
    writer1.stop()
    old_elapsed = time.perf_counter() - start
    
    # New way with writer
    writer2 = create_writer("/tmp/bench_new.log", WriterType.BLOCK, Mode.TRIGGER, batch_size=1000)
    start = time.perf_counter()
    for i in range(N):
        log_line = build_json_line(
            message="test",
            message_type="info",
            task_uuid="test",
            task_level=(1,),
            fields={"i": i},
            timestamp=now(),
        )
        writer2.send(log_line)
    writer2.stop()
    new_elapsed = time.perf_counter() - start
    
    return old_elapsed, new_elapsed


def main():
    print("=" * 60)
    print("BENCHMARK: Old vs New Implementation")
    print("=" * 60)
    print(f"Iterations: {N:,}")
    print()
    
    # Benchmark serialization only
    print("1. Serialization Only (no writer)")
    print("-" * 60)
    
    old_time, old_tput = benchmark_old_way()
    print(f"Old (Record+json):  {old_time*1000:.1f}ms  {old_tput:,.0f} L/s")
    
    new_time, new_tput = benchmark_new_way()
    print(f"New (_json_line):   {new_time*1000:.1f}ms  {new_tput:,.0f} L/s")
    
    speedup = new_tput / old_tput
    print(f"Speedup:            {speedup:.1f}x faster")
    print()
    
    # Benchmark with writer
    print("2. With Writer (includes I/O)")
    print("-" * 60)
    
    old_w_time, new_w_time = benchmark_with_writer()
    old_w_tput = N / old_w_time
    new_w_tput = N / new_w_time
    
    print(f"Old + writer:       {old_w_time*1000:.1f}ms  {old_w_tput:,.0f} L/s")
    print(f"New + writer:       {new_w_time*1000:.1f}ms  {new_w_tput:,.0f} L/s")
    
    speedup_w = new_w_tput / old_w_tput
    print(f"Speedup:            {speedup_w:.1f}x faster")
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Serialization:     {speedup:.1f}x faster")
    print(f"With I/O:          {speedup_w:.1f}x faster")
    print()
    print("Key improvements:")
    print("  • build_json_line() uses f-strings instead of json.dumps()")
    print("  • No dataclass allocation overhead")
    print("  • No intermediate dict creation")
    print("  • Cached root task UUID")
    print()
    
    # Cleanup
    import os
    for f in ["/tmp/bench_old.log", "/tmp/bench_new.log"]:
        if os.path.exists(f):
            os.remove(f)


if __name__ == "__main__":
    main()
