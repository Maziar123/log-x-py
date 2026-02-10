import asyncio
import sys

from logxpy import aaction, log, start_action, to_file


def test_sync():
    print("--- Testing sync log ---")
    log.info("Hello from sync", user="me")
    with log.scope(request_id="123"):
        log.info("Inside scope")
        with start_action(action_type="legacy_action"):
            log.info("Inside legacy action")


async def test_async():
    print("\n--- Testing async log ---")
    async with aaction("async_task", param=1):
        log.info("Inside async action")
        await asyncio.sleep(0.1)
        log.success("Async task done")


if __name__ == "__main__":
    # Configure output to stdout
    to_file(sys.stdout)

    test_sync()
    asyncio.run(test_async())
