"""Test script to simulate debugging scenario."""

from logxpy import log
import time
import sys

# Setup logging exactly like the example
log.init("", size=0, flush="100µs", clean=True)
print(f"Log file: {log._auto_log_file}")


def main():
    # Line 19
    log.info("Hello, World!")
    
    # SIMULATE DEBUGGER PAUSE - in real debugging, you'd pause here
    # We'll simulate by just continuing
    
    # Line 20
    log.warning("This is a warning")
    
    # Give async writer time to flush
    time.sleep(0.01)  # 10ms is enough for 100µs flush interval
    
    # Print results
    with open(log._auto_log_file) as f:
        content = f.read()
        lines = [l for l in content.split("\n") if l.strip()]
        print(f"\nLog file contains {len(lines)} lines:")
        for i, line in enumerate(lines, 1):
            print(f"  {i}. {line[:60]}...")


if __name__ == "__main__":
    main()
