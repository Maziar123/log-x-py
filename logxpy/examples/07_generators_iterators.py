"""
07_generators_iterators.py - Tracking progress

Demonstrates:
- @log.generator: Sync generator tracking
- @log.aiterator: Async iterator tracking
"""
import sys
import time
import asyncio
from logxpy import log, to_file

to_file(sys.stdout)

# 1. Sync Generator
@log.generator("Processing items", every=2)
def process_items(items):
    for item in items:
        time.sleep(0.05)
        yield item * 2

# 2. Async Iterator
@log.aiterator("Async stream", every=3)
async def stream_data(count):
    for i in range(count):
        await asyncio.sleep(0.05)
        yield i

def main():
    print("--- 1. Generator Tracking ---")
    items = list(range(10))
    # Will log progress every 2 items
    results = list(process_items(items))
    log.success("Sync processing complete", results=len(results))

    print("\n--- 2. Async Iterator Tracking ---")
    async def run_async():
        count = 0
        async for _ in stream_data(10):
            count += 1
        log.success("Async processing complete", count=count)
    
    asyncio.run(run_async())

if __name__ == "__main__":
    main()
