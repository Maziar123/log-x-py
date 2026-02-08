#!/usr/bin/env python3
"""
Example 01: Basic Logging
Create basic log messages and view with logxpy_cli_view
"""

import sys
from pathlib import Path

# Add logxpy to path
sys.path.insert(0, str(Path(__file__).parent.parent / "logxpy"))

from logxpy import Message, to_file

# Setup logging to file
log_file = Path(__file__).parent / "example_01_basic.log"
to_file(open(log_file, "w"))

# Log basic messages
Message.log(message_type="app:startup", version="1.0.0", environment="production")
Message.log(message_type="app:info", text="Application started successfully")
Message.log(message_type="user:login", user_id=123, username="alice", ip="192.168.1.100")
Message.log(message_type="database:connect", host="localhost", port=5432, status="connected")
Message.log(message_type="app:warning", text="High memory usage", memory_percent=85)
Message.log(message_type="app:success", text="Data processed", records=1000, duration_ms=234)

print(f"✓ Log created: {log_file}")
print("\nView with: python view_tree.py example_01_basic.log")
