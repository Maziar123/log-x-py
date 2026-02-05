import asyncio
import sys

try:
    import eliot

    print(f"Eliot file: {eliot.__file__}")
    print(f"Eliot dir: {dir(eliot)}")
    from logxpy import aaction, log, start_action, to_file
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)


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
