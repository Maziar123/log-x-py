"""
09_configuration.py - Configuring LoggerX

Demonstrates:
- log.configure(): Runtime configuration
- Destinations: Console, File
- Field Masking: Hiding sensitive data
"""

import os

from logxpy import log

# We won't use to_file(sys.stdout) here because we'll configure it via log.configure


def main():
    print("--- 1. Configuration ---")

    # Configure the logger
    # - Level: DEBUG
    # - Destinations: stdout (via console) and a file
    # - Masking: hide 'password' and 'token' fields
    log.configure(
        level="DEBUG",
        destinations=["console", "file://example_config.log"],
        mask_fields=["password", "token", "secret"],
    )

    log.info("Logger configured")

    print("\n--- 2. Field Masking ---")
    # These fields should be masked in the output
    log.info("User login", username="admin", password="supersecretpassword123")
    log.debug("API Call", url="https://api.com", token="ab83-1234-5678")

    # Nested masking
    log.info(
        "Config dump",
        config={
            "db": {
                "host": "localhost",
                "password": "db_password",
            },
        },
    )

    print("\nCheck 'example_config.log' for file output.")
    with open("example_config.log") as f:
        print(f.read())

    # Clean up
    if os.path.exists("example_config.log"):
        os.remove("example_config.log")


if __name__ == "__main__":
    main()
