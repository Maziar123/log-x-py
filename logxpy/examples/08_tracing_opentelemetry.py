"""
08_tracing_opentelemetry.py - Distributed Tracing

Demonstrates:
- @log.trace: Decorator for spans
- log.span(): Context manager for spans
"""
import sys
import asyncio
from logxpy import log, to_file

to_file(sys.stdout)

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
