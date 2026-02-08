#!/usr/bin/env python3
"""
Example 06: Deep Nesting (7 Levels)
====================================

Demonstrates deeply nested operations showing tree structure
with enter/exit at each level up to 7 levels deep.

This shows how logxpy handles complex hierarchical operations.
"""

import sys
import time
from pathlib import Path

# Add logxpy to path
sys.path.insert(0, str(Path(__file__).parent.parent / "logxpy"))

from logxpy import Message, start_action, to_file

# Setup logging to file
log_file = Path(__file__).parent / "example_06_deep_nesting.log"
to_file(open(log_file, "w"))


def level_7_deepest():
    """Level 7 - Deepest operation"""
    with start_action(action_type="level_7:operation", depth=7):
        Message.log(message_type="level_7:start", info="Deepest level reached")
        time.sleep(0.01)
        Message.log(message_type="level_7:processing", data="Final computation")
        time.sleep(0.01)
        Message.log(message_type="level_7:complete", result="SUCCESS")


def level_6_database_query():
    """Level 6 - Database query"""
    with start_action(action_type="level_6:database", depth=6):
        Message.log(message_type="db:connect", connection="postgres://localhost")
        time.sleep(0.02)

        Message.log(message_type="db:query", sql="SELECT * FROM records")
        time.sleep(0.03)

        # Go deeper
        level_7_deepest()

        Message.log(message_type="db:result", rows=42)


def level_5_cache_check():
    """Level 5 - Cache validation"""
    with start_action(action_type="level_5:cache", depth=5):
        Message.log(message_type="cache:lookup", key="user:data:123")
        time.sleep(0.02)

        Message.log(message_type="cache:miss", reason="expired")

        # Need to fetch from database
        level_6_database_query()

        Message.log(message_type="cache:update", key="user:data:123", ttl=3600)


def level_4_authentication():
    """Level 4 - User authentication"""
    with start_action(action_type="level_4:auth", depth=4):
        Message.log(message_type="auth:validate_token", token_id="tok_abc123")
        time.sleep(0.02)

        Message.log(message_type="auth:check_permissions", user_id="user_123")
        time.sleep(0.02)

        # Check cache for user data
        level_5_cache_check()

        Message.log(message_type="auth:success", user="alice", roles=["admin", "user"])


def level_3_request_validation():
    """Level 3 - Request validation"""
    with start_action(action_type="level_3:validation", depth=3):
        Message.log(message_type="validation:headers", count=12)
        time.sleep(0.02)

        Message.log(message_type="validation:body", content_type="application/json", size=1024)
        time.sleep(0.02)

        # Authenticate the request
        level_4_authentication()

        Message.log(message_type="validation:complete", status="valid")


def level_2_request_handler():
    """Level 2 - HTTP request handler"""
    with start_action(action_type="level_2:http_handler", depth=2):
        Message.log(message_type="http:received", method="POST", path="/api/users/123")
        time.sleep(0.02)

        Message.log(message_type="http:parse", content_length=1024)
        time.sleep(0.02)

        # Validate the request
        level_3_request_validation()

        Message.log(message_type="http:response", status=200, duration_ms=150)


def level_1_server_process():
    """Level 1 - Server main process"""
    with start_action(action_type="level_1:server", depth=1):
        Message.log(message_type="server:incoming_connection", ip="192.168.1.100", port=8080)
        time.sleep(0.02)

        Message.log(message_type="server:assign_worker", worker_id="worker_05")
        time.sleep(0.02)

        # Handle the request
        level_2_request_handler()

        Message.log(message_type="server:connection_closed", duration_ms=200)


def example_complex_class_nesting():
    """Demonstrate nested class-based operations"""
    with start_action(action_type="class:application", component="Application"):
        Message.log(message_type="app:init", version="2.0.0")

        # Level 1: Service layer
        with start_action(action_type="class:service", component="UserService"):
            Message.log(message_type="service:init")

            # Level 2: Repository layer
            with start_action(action_type="class:repository", component="UserRepository"):
                Message.log(message_type="repo:connect")

                # Level 3: Connection pool
                with start_action(action_type="class:connection_pool", component="ConnectionPool"):
                    Message.log(message_type="pool:acquire", available=10)

                    # Level 4: Database connection
                    with start_action(action_type="class:db_connection", component="PostgresConnection"):
                        Message.log(message_type="db:open", database="users_db")

                        # Level 5: Query builder
                        with start_action(action_type="class:query_builder", component="QueryBuilder"):
                            Message.log(message_type="query:build", table="users")

                            # Level 6: Query executor
                            with start_action(action_type="class:executor", component="QueryExecutor"):
                                Message.log(message_type="executor:prepare")

                                # Level 7: Result parser
                                with start_action(action_type="class:parser", component="ResultParser"):
                                    Message.log(message_type="parser:parse", rows=5)
                                    Message.log(message_type="parser:transform")
                                    Message.log(message_type="parser:complete", records=5)

                                Message.log(message_type="executor:complete")

                            Message.log(message_type="query:success")

                        Message.log(message_type="db:close")

                    Message.log(message_type="pool:release")

                Message.log(message_type="repo:disconnect")

            Message.log(message_type="service:complete")

        Message.log(message_type="app:shutdown")


def example_recursive_operation():
    """Demonstrate recursive-like deep nesting"""
    with start_action(action_type="recursive:process_tree", node_id="root"):
        Message.log(message_type="node:visit", node="root")

        # Branch 1
        with start_action(action_type="recursive:process_tree", node_id="branch_1"):
            Message.log(message_type="node:visit", node="branch_1")

            with start_action(action_type="recursive:process_tree", node_id="leaf_1_1"):
                Message.log(message_type="node:visit", node="leaf_1_1")

                with start_action(action_type="recursive:process_data", data_id="data_1"):
                    Message.log(message_type="data:process", size=100)

                    with start_action(action_type="recursive:validate", validator="schema_v1"):
                        Message.log(message_type="validate:check", rules=10)

                        with start_action(action_type="recursive:transform", transformer="json_to_xml"):
                            Message.log(message_type="transform:convert")

                            with start_action(action_type="recursive:output", format="xml"):
                                Message.log(message_type="output:write", bytes=1500)
                                Message.log(message_type="output:complete")

            with start_action(action_type="recursive:process_tree", node_id="leaf_1_2"):
                Message.log(message_type="node:visit", node="leaf_1_2")
                Message.log(message_type="node:leaf", has_children=False)

        # Branch 2
        with start_action(action_type="recursive:process_tree", node_id="branch_2"):
            Message.log(message_type="node:visit", node="branch_2")

            with start_action(action_type="recursive:process_tree", node_id="leaf_2_1"):
                Message.log(message_type="node:visit", node="leaf_2_1")
                Message.log(message_type="node:leaf", has_children=False)

        Message.log(message_type="node:complete", total_nodes=7)


def main():
    """Run all deep nesting examples"""
    print("Creating deeply nested log examples...")

    # Example 1: Deep functional nesting (7 levels)
    print("\n1. Deep Functional Nesting (7 levels)")
    level_1_server_process()

    # Example 2: Class-based nesting (7 levels)
    print("2. Class-Based Nesting (7 levels)")
    example_complex_class_nesting()

    # Example 3: Recursive-like nesting
    print("3. Recursive Tree Processing (7 levels)")
    example_recursive_operation()

    print(f"\n✓ Log created: {log_file}")
    print("\nView with: python view_tree.py example_06_deep_nesting.log")
    print("\nThis example shows:")
    print("  - 7 levels of nested actions")
    print("  - Tree enter/exit at each level")
    print("  - Functional nesting pattern")
    print("  - Class-based nesting pattern")
    print("  - Recursive-like nesting pattern")


if __name__ == "__main__":
    main()
