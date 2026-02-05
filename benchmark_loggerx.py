import asyncio
import os
import time

from logxpy import aaction, log, start_action, to_file

# Disable output for benchmarks
to_file(open(os.devnull, "w"))

ITERATIONS = 10000


def bench_sync_old():
    start = time.time()
    for i in range(ITERATIONS):
        with start_action(action_type="test"):
            pass
    end = time.time()
    print(f"Old Sync (start_action): {ITERATIONS / (end - start):.2f} ops/sec")


def bench_sync_new():
    start = time.time()
    for i in range(ITERATIONS):
        log.info("test", i=i)
    end = time.time()
    print(f"New Sync (log.info):     {ITERATIONS / (end - start):.2f} ops/sec")


async def bench_async_new():
    start = time.time()
    for i in range(ITERATIONS):
        async with aaction("test_async", i=i):
            pass
    end = time.time()
    print(f"New Async (aaction):     {ITERATIONS / (end - start):.2f} ops/sec")


if __name__ == "__main__":
    print(f"Benchmarking {ITERATIONS} iterations...")
    bench_sync_old()
    bench_sync_new()
    asyncio.run(bench_async_new())
