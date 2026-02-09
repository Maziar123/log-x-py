"""
08_tracing_opentelemetry.py - Distributed Tracing

Demonstrates:
- @log.trace: Decorator for spans
- log.span(): Context manager for spans
"""
from pathlib import Path
import asyncio
from logxpy import log, to_file

# Setup output to log file (delete old log first)
LOG_FILE = Path(__file__).with_suffix(".log")
if LOG_FILE.exists():
    LOG_FILE.unlink()
with open(LOG_FILE, "w", encoding="utf-8") as f:
    to_file(f)

# Note: For this to actually send data to a collector, you need to configure
# the OTel destination. Without it, it still works but acts as a no-op
# or local logger depending on config.

@log.trace(name="db_query", attributes={"db.system": "postgresql"})
async def query_db(query):
    await asyncio.sleep(0.1)
    return [{"id": 1, "val": "result"}]

async def handle_request():
    # Start a parent span
    with log.span("handle_request", method="GET", path="/api/data"):
        log.info("Parsing request")

        # Child span via decorator
        result = await query_db("SELECT * FROM table")

        # Child span via context manager
        with log.span("process_result"):
            log.info("Processing", rows=len(result))

    log.success("Request handled")

if __name__ == "__main__":
    print("--- OpenTelemetry Tracing Demo ---")
    print("(Requires opentelemetry-sdk installed for actual tracing)")
    asyncio.run(handle_request())
