"""Debug version - pauses before log.info('Info message')"""
from logxpy import log
import time

# Setup
log.init("", size=0, flush="100µs", clean=True)

# Execute up to line 27
log.info("Hello, World!")
log.warning("This is a warning")
log.info("User logged in", user_id=123, username="alice")
log.success("Database connected", host="localhost", port=5432)
log.debug("Debug message")

# PAUSE HERE - before line 28 log.info("Info message")
print("=" * 60)
print("⏸️  PAUSED: About to execute log.info('Info message')")
print("=" * 60)
print(f"Log file: {log._auto_log_file}")
print()
print("Current log file content:")
print("-" * 60)

# Show current log file
with open(log._auto_log_file) as f:
    print(f.read(), end='')

print("-" * 60)
print()
print("Waiting 0.5s then executing log.info('Info message')...")
time.sleep(0.5)

# NOW execute line 28
log.info("Info message")

print()
print("✅ Executed! Updated log file:")
print("-" * 60)
with open(log._auto_log_file) as f:
    print(f.read(), end='')
print("-" * 60)

log.shutdown_async()
