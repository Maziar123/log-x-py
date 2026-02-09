"""03_context_scopes.py - Managing context and scopes

Demonstrates:
- log.scope(): Context managers for blocks
- log.ctx(): Fluent context builder
- Nested scopes
"""

from pathlib import Path
from logxpy import log, to_file

LOG_FILE = Path(__file__).with_suffix(".log")
if LOG_FILE.exists():
    LOG_FILE.unlink()
with open(LOG_FILE, "w", encoding="utf-8") as f:
    to_file(f)


def process_item(item_id):
    # This log will inherit 'request_id' and 'user' from the scope
    log.info("Processing item", item_id=item_id)


def main():
    # 1. Basic Scope
    with log.scope(request_id="req-123", user="alice"):
        log.info("Start request")
        process_item(1)
        process_item(2)
        log.success("End request")

    # 2. Nested Scopes
    with log.scope(service="payment"):
        log.info("Service init")

        with log.scope(transaction_id="tx-999"):
            # Has service="payment" AND transaction_id="tx-999"
            log.info("Validating")
            log.success("Authorized")

        # Back to just service="payment"
        log.info("Service finish")

    # 3. Fluent Context Builder
    user_log = log.ctx(component="user_service", version="1.0")
    user_log.info("User service ready")
    user_log.debug("Cache warmed up")

    print(f"Log written to: {LOG_FILE}")
    print(f"View with: logxpy-view {LOG_FILE}")


if __name__ == "__main__":
    main()
