"""LogXPy Log Parser - Simple Example

Demonstrates creating and viewing logs with logxpy-cli-view.
This script:
1. Creates a sample log file using logxpy
2. Displays it using logxpy-cli-view
3. Cleans up the log file
"""

from pathlib import Path
import tempfile
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "logxpy"))

from logxpy import log, start_action, to_file


def create_sample_log():
    """Create a sample log file for viewing."""
    log_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
    log_path = Path(log_file.name)

    # Initialize logxpy
    to_file(open(log_path, 'w'))

    # Create hierarchical log entries
    log("Application starting")

    with start_action("http:server", port=8080):
        log.info("Server initialized")

        with start_action("http:request", method="GET", path="/api/users"):
            log("Fetching users list")

            with start_action("db:query", sql="SELECT * FROM users"):
                log.info("Retrieved 10 users")

        with start_action("http:request", method="POST", path="/api/login"):
            log("User login attempt")

            with start_action("auth:validate", user="alice"):
                log.success("Authentication successful")

    with start_action("cache:warmup"):
        log.debug("Loading cache keys")
        log.info(f"Cache warmed: 142 keys loaded")

    log.warning("High memory usage: 85%", usage_mb=2048)

    with start_action("background:job", job="email_cleanup"):
        log.info("Starting email cleanup job")
        log.info("Processed 500 emails")
        log.success("Job completed")

    with start_action("http:request", method="GET", path="/api/products"):
        log.error("Database timeout", error="Connection timed out after 30s")

    log("Application shutting down")

    return log_path


def main():
    log_path = create_sample_log()
    print(f"Created sample log: {log_path.name}")
    print(f"Path: {log_path}\n")

    try:
        # View the log with logxpy-cli-view
        print("Viewing log with tree structure...")
        print("-" * 60)

        result = subprocess.run(
            ["logxpy-view", str(log_path)],
            capture_output=False
        )

        if result.returncode != 0:
            print("\nNote: logxpy-view not found. Install with:")
            print("  pip install logxpy-cli-view")

    finally:
        # Clean up
        log_path.unlink()
        print(f"\nCleaned up: {log_path.name}")


if __name__ == "__main__":
    main()
