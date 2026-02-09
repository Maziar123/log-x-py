"""
04_async_tasks.py - Async logging and tasks

Demonstrates:
- aaction: Async context manager for actions
- @log.logged on async functions
- Async context propagation
"""
from pathlib import Path
import asyncio
from logxpy import log, aaction, to_file

# Setup output to log file (delete old log first)
LOG_FILE = Path(__file__).with_suffix(".log")
if LOG_FILE.exists():
    LOG_FILE.unlink()
with open(LOG_FILE, "w", encoding="utf-8") as f:
    to_file(f)

# 1. Async Decorator
@log.logged
async def fetch_data(url):
    await asyncio.sleep(0.1)
    return {"data": "bytes", "url": url}

# 2. Async Context Manager (Action)
async def process_data(data):
    # 'aaction' is the async equivalent of 'action'/'start_action'
    async with aaction("process_data", size=len(data)):
        await asyncio.sleep(0.05)
        log.info("Transforming data")
        return "processed"

async def main():
    print("--- 1. Async Decorator ---")
    result = await fetch_data("http://example.com")

    print("\n--- 2. Async Actions ---")
    # Context propagates automatically in asyncio
    with log.scope(task_id="main-task"):
        processed = await process_data(result)
        log.success("Done", result=processed)

    print("\n--- 3. Concurrent Tasks ---")
    # Each task gets its own context/action tree
    async with aaction("batch_job"):
        await asyncio.gather(
            fetch_data("http://a.com"),
            fetch_data("http://b.com"),
            fetch_data("http://c.com")
        )

if __name__ == "__main__":
    asyncio.run(main())
