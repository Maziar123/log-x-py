#!/usr/bin/env python3
"""Example 06: Deep Nesting (7 Levels) - hierarchical operations."""

import time

from logxpy import log, start_action


def level_7_deepest():
    with start_action(action_type="level_7:operation", depth=7):
        log.info("Deepest level reached")
        time.sleep(0.01)
        log.success("Final computation", result="SUCCESS")


def level_6_database_query():
    with start_action(action_type="level_6:database", depth=6):
        log.info("DB connect", connection="postgres://localhost")
        time.sleep(0.02)
        log.info("Querying", sql="SELECT * FROM records")
        time.sleep(0.03)
        level_7_deepest()
        log.success("Result", rows=42)


def level_5_cache_check():
    with start_action(action_type="level_5:cache", depth=5):
        log.info("Cache lookup", key="user:data:123")
        time.sleep(0.02)
        log.warning("Cache miss", reason="expired")
        level_6_database_query()
        log.success("Cache updated", key="user:data:123", ttl=3600)


def level_4_authentication():
    with start_action(action_type="level_4:auth", depth=4):
        log.info("Validate token", token_id="tok_abc123")
        time.sleep(0.02)
        log.info("Check permissions", user_id="user_123")
        time.sleep(0.02)
        level_5_cache_check()
        log.success("Auth success", user="alice", roles=["admin", "user"])


def level_3_request_validation():
    with start_action(action_type="level_3:validation", depth=3):
        log.info("Validate headers", count=12)
        time.sleep(0.02)
        log.info("Validate body", content_type="application/json", size=1024)
        time.sleep(0.02)
        level_4_authentication()
        log.success("Validation complete")


def level_2_request_handler():
    with start_action(action_type="level_2:http_handler", depth=2):
        log.info("Received", method="POST", path="/api/users/123")
        time.sleep(0.02)
        log.info("Parsing", content_length=1024)
        time.sleep(0.02)
        level_3_request_validation()
        log.success("Response", status=200, duration_ms=150)


def level_1_server_process():
    with start_action(action_type="level_1:server", depth=1):
        log.info("Incoming connection", ip="192.168.1.100", port=8080)
        time.sleep(0.02)
        log.info("Assign worker", worker_id="worker_05")
        time.sleep(0.02)
        level_2_request_handler()
        log.success("Connection closed", duration_ms=200)


def example_class_nesting():
    with start_action(action_type="class:application", component="Application"):
        log.info("App init", version="2.0.0")
        with start_action(action_type="class:service", component="UserService"):
            log.info("Service init")
            with start_action(action_type="class:repository", component="UserRepository"):
                log.info("Repo connect")
                with start_action(action_type="class:connection_pool", component="ConnectionPool"):
                    log.info("Pool acquire", available=10)
                    with start_action(action_type="class:db_connection", component="PostgresConnection"):
                        log.info("DB open", database="users_db")
                        with start_action(action_type="class:query_builder", component="QueryBuilder"):
                            log.info("Query build", table="users")
                            with start_action(action_type="class:executor", component="QueryExecutor"):
                                log.info("Prepare")
                                with start_action(action_type="class:parser", component="ResultParser"):
                                    log.info("Parsing", rows=5)
                                    log.success("Transform complete", records=5)
                                log.success("Executed")
                            log.success("Query done")
                        log.info("DB close")
                    log.info("Pool release")
                log.info("Repo disconnect")
            log.success("Service complete")
        log.success("App shutdown")


def example_recursive_tree():
    with start_action(action_type="recursive:process_tree", node_id="root"):
        log.info("Visit node", node="root")
        with start_action(action_type="recursive:process_tree", node_id="branch_1"):
            log.info("Visit node", node="branch_1")
            with start_action(action_type="recursive:process_tree", node_id="leaf_1_1"):
                log.info("Visit node", node="leaf_1_1")
                with start_action(action_type="recursive:process_data", data_id="data_1"):
                    log.info("Process", size=100)
                    with start_action(action_type="recursive:validate", validator="schema_v1"):
                        log.info("Check", rules=10)
                        with start_action(action_type="recursive:transform", transformer="json_to_xml"):
                            log.info("Convert")
                            with start_action(action_type="recursive:output", format="xml"):
                                log.success("Output written", bytes=1500)
            with start_action(action_type="recursive:process_tree", node_id="leaf_1_2"):
                log.info("Leaf node", has_children=False)
        with start_action(action_type="recursive:process_tree", node_id="branch_2"):
            log.info("Visit node", node="branch_2")
            with start_action(action_type="recursive:process_tree", node_id="leaf_2_1"):
                log.info("Leaf node", has_children=False)
        log.success("Tree complete", total_nodes=7)


# Run all examples
level_1_server_process()
example_class_nesting()
example_recursive_tree()

print("✓ Log created: example_06_deep_nesting.log")
