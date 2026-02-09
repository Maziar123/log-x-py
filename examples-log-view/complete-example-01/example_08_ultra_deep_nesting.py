#!/usr/bin/env python3
"""
Example 08: Ultra Deep Nesting (25 Levels)
===========================================

Demonstrates extremely deeply nested operations with 25 levels of nesting.
This example simulates a complex enterprise system with multiple layers:

1. Application Gateway
2. Load Balancer
3. API Gateway
4. Service Mesh
5. Microservice Container
6. Request Handler
7. Controller Layer
8. Service Layer
9. Business Logic Layer
10. Validation Layer
11. Authentication Layer
12. Authorization Layer
13. Cache Layer
14. Database Connection Pool
15. Database Transaction
16. Query Builder
17. Query Optimizer
18. Query Executor
19. Result Parser
20. Data Transformer
21. Response Builder
22. Serialization Layer
23. Compression Layer
24. Encryption Layer
25. Network Transmission

Each level demonstrates realistic enterprise operations with proper logging.
"""

import sys
import time
from pathlib import Path

# Add logxpy to path
sys.path.insert(0, str(Path(__file__).parent.parent / "logxpy"))

from logxpy import Message, start_action, to_file

# Setup logging to file (delete old log first)
log_file = Path(__file__).parent / "example_08_ultra_deep_nesting.log"
if log_file.exists():
    log_file.unlink()
with open(log_file, "w", encoding="utf-8") as f:
    to_file(f)


# ===== LEVEL 25: Network Transmission =====
def level_25_network_transmission():
    """Level 25 - Network packet transmission"""
    with start_action(action_type="network:transmit", level=25, protocol="TCP"):
        Message.log(message_type="network:packet_create", size_bytes=1024, packet_id="pkt_final")
        time.sleep(0.001)
        Message.log(message_type="network:socket_write", socket_fd=42, bytes_written=1024)
        time.sleep(0.001)
        Message.log(message_type="network:transmit_complete", destination="client:ip", port=443, encrypted=True)


# ===== LEVEL 24: Encryption Layer =====
def level_24_encryption_layer():
    """Level 24 - Data encryption"""
    with start_action(action_type="encryption:process", level=24, algorithm="AES-256-GCM"):
        Message.log(message_type="encryption:key_retrieve", key_id="key_production_42", keyvault="aws:kms")
        time.sleep(0.002)
        Message.log(message_type="encryption:iv_generate", iv_length=12, iv_bytes="0x1a2b3c...")
        time.sleep(0.001)
        Message.log(message_type="encryption:encrypt", input_size=1024, output_size=1040)
        time.sleep(0.003)
        Message.log(message_type="encryption:auth_tag", tag_length=16, tag_valid=True)
        level_25_network_transmission()
        Message.log(message_type="encryption:success", data_encrypted=True, cipher_version="v2")


# ===== LEVEL 23: Compression Layer =====
def level_23_compression_layer():
    """Level 23 - Response compression"""
    with start_action(action_type="compression:compress", level=23, algorithm="gzip"):
        Message.log(message_type="compression:analyze", original_size=5120, content_type="application/json")
        time.sleep(0.002)
        Message.log(message_type="compression:compress", level=9, strategy="default")
        time.sleep(0.003)
        Message.log(message_type="compression:result", compressed_size=1024, ratio=5.0, saved_bytes=4096)
        level_24_encryption_layer()
        Message.log(message_type="compression:complete", encoding="gzip", quality="optimal")


# ===== LEVEL 22: Serialization Layer =====
def level_22_serialization_layer(data):
    """Level 22 - Data serialization"""
    with start_action(action_type="serialization:serialize", level=22, format="json"):
        Message.log(message_type="serialization:validate", schema="api_response_v3", valid=True)
        time.sleep(0.001)
        Message.log(message_type="serialization:encode", field_count=15, nested_objects=5)
        time.sleep(0.002)
        Message.log(message_type="serialization:datetime_format", format="iso8601", timezone="UTC")
        time.sleep(0.001)
        Message.log(message_type="serialization:result", output_size_bytes=5120, encoded=True)
        level_23_compression_layer()
        Message.log(message_type="serialization:complete", format="json", charset="utf-8", pretty_print=False)


# ===== LEVEL 21: Response Builder =====
def level_21_response_builder(data):
    """Level 21 - Build HTTP response"""
    with start_action(action_type="response:build", level=21, status_code=200):
        Message.log(message_type="response:headers", content_type="application/json", cache_control="no-cache")
        time.sleep(0.001)
        Message.log(message_type="response:metadata", request_id="req_abc123", trace_id="trace_xyz789")
        time.sleep(0.001)
        Message.log(message_type="response:body", data_items=len(data), total_size=4800)
        time.sleep(0.002)
        Message.log(message_type="response:etag", etag='"33a64df551425fcc55e4d42a148795d9f25f89d4"', weak=False)
        level_22_serialization_layer(data)
        Message.log(message_type="response:ready", status="complete", headers_count=8)


# ===== LEVEL 20: Data Transformer =====
def level_20_data_transformer(raw_data):
    """Level 20 - Transform raw data to response format"""
    with start_action(action_type="transform:execute", level=20, transformer="api_v3"):
        Message.log(message_type="transform:input", source_type="db_record", count=len(raw_data))
        time.sleep(0.002)
        Message.log(message_type="transform:field_map", mappings=10, renames=3)
        time.sleep(0.002)
        Message.log(message_type="transform:type_convert", int_to_str=5, date_to_iso=2)
        time.sleep(0.002)
        Message.log(message_type="transform:filter", filtered_count=0, reason="all_valid")
        transformed_data = [{"id": i, "name": f"item_{i}", "value": i * 10} for i in range(10)]
        level_21_response_builder(transformed_data)
        Message.log(message_type="transform:complete", output_count=len(transformed_data), duration_ms=8)


# ===== LEVEL 19: Result Parser =====
def level_19_result_parser(db_result):
    """Level 19 - Parse database result"""
    with start_action(action_type="parse:database_result", level=19, result_type="cursor"):
        Message.log(message_type="parse:row_count", rows=len(db_result), columns=8)
        time.sleep(0.001)
        Message.log(message_type="parse:types", detected_types={"id": "int", "name": "str", "created_at": "datetime"})
        time.sleep(0.002)
        Message.log(message_type="parse:null_handling", null_count=2, null_strategy="default")
        level_20_data_transformer(db_result)
        Message.log(message_type="parse:success", parsed_rows=len(db_result), errors=0)


# ===== LEVEL 18: Query Executor =====
def level_18_query_executor(sql, params):
    """Level 18 - Execute the query"""
    with start_action(action_type="database:execute", level=18, executor="postgresql"):
        Message.log(message_type="execute:query", sql=sql[:50] + "...", params_count=len(params))
        time.sleep(0.005)
        Message.log(message_type="execute:plan", plan_type="index_scan", index="users_pkey")
        time.sleep(0.003)
        Message.log(message_type="execute:fetch", rows_fetched=10, buffers=5)
        result = [{"id": i, "name": f"user_{i}"} for i in range(10)]
        level_19_result_parser(result)
        Message.log(message_type="execute:complete", rows_returned=len(result), execution_time_ms=8)


# ===== LEVEL 17: Query Optimizer =====
def level_17_query_optimizer(sql, params):
    """Level 17 - Optimize the query"""
    with start_action(action_type="database:optimize", level=17, optimizer="cost_based"):
        Message.log(message_type="optimize:analyze", tables=["users", "profiles"], joins=1)
        time.sleep(0.002)
        Message.log(message_type="optimize:index_select", index_used="users_email_idx", reason="equality_filter")
        time.sleep(0.001)
        Message.log(message_type="optimize:cost_estimate", initial_cost=1000, optimized_cost=50)
        time.sleep(0.001)
        Message.log(message_type="optimize:join_order", join_type="nested_loop", outer_table="users")
        level_18_query_executor(sql, params)
        Message.log(message_type="optimize:result", optimization_saved_ms=5, plan_hash="abc123")


# ===== LEVEL 16: Query Builder =====
def level_16_query_builder(table, filters):
    """Level 16 - Build SQL query"""
    with start_action(action_type="database:build_query", level=16, builder_type="orm"):
        Message.log(message_type="builder:table", table=table, alias="u")
        time.sleep(0.001)
        Message.log(message_type="builder:select", columns=["id", "name", "email"], column_count=3)
        time.sleep(0.001)
        Message.log(message_type="builder:where", clauses=len(filters), operators=["=", "LIKE"])
        time.sleep(0.001)
        Message.log(message_type="builder:order_by", field="created_at", direction="DESC")
        sql = f"SELECT id, name, email FROM {table} WHERE {' AND '.join(filters)} ORDER BY created_at DESC"
        params = ["user@example.com"]
        level_17_query_optimizer(sql, params)
        Message.log(message_type="builder:complete", query_length=len(sql), param_count=len(params))


# ===== LEVEL 15: Database Transaction =====
def level_15_database_transaction():
    """Level 15 - Manage database transaction"""
    with start_action(action_type="database:transaction", level=15, isolation_level="read_committed"):
        Message.log(message_type="transaction:begin", transaction_id="txn_12345", readonly=True)
        time.sleep(0.001)
        Message.log(message_type="transaction:snapshot", snapshot_id="snap_67890", xmin=12345)
        time.sleep(0.001)
        Message.log(message_type="transaction:lock", lock_type="access_share", tables=["users"])
        level_16_query_builder("users", ["email = ?", "status = 'active'"])
        Message.log(message_type="transaction:commit", transaction_id="txn_12345", duration_ms=15)
        time.sleep(0.001)
        Message.log(message_type="transaction:complete", status="committed", changes=0)


# ===== LEVEL 14: Database Connection Pool =====
def level_14_connection_pool():
    """Level 14 - Get connection from pool"""
    with start_action(action_type="database:pool_acquire", level=14, pool_name="main_pool"):
        Message.log(message_type="pool:status", pool_size=20, available=5, in_use=15)
        time.sleep(0.001)
        Message.log(message_type="pool:acquire", connection_id="conn_42", wait_time_ms=1)
        time.sleep(0.001)
        Message.log(message_type="connection:validate", is_valid=True, last_used_seconds_ago=5)
        level_15_database_transaction()
        Message.log(message_type="pool:release", connection_id="conn_42", new_available=6)
        Message.log(message_type="pool:complete", pool_utilization=0.75, healthy=True)


# ===== LEVEL 13: Cache Layer =====
def level_13_cache_layer(key):
    """Level 13 - Check cache"""
    with start_action(action_type="cache:get", level=13, cache_type="redis"):
        Message.log(message_type="cache:key", key=key, key_type="string")
        time.sleep(0.002)
        Message.log(message_type="cache:miss", ttl="none", reason="expired")
        time.sleep(0.001)
        Message.log(message_type="cache:backfill", strategy="lazy_loading", ttl_seconds=3600)
        level_14_connection_pool()
        Message.log(message_type="cache:set", key=key, stored=True, ttl_seconds=3600)
        Message.log(message_type="cache:complete", hit=False, miss=True)


# ===== LEVEL 12: Authorization Layer =====
def level_12_authorization(user, resource, action):
    """Level 12 - Check authorization"""
    with start_action(action_type="auth:authorize", level=12, framework="casbin"):
        Message.log(message_type="authz:subject", user_id=user["id"], user_role=user["role"])
        time.sleep(0.002)
        Message.log(message_type="authz:resource", resource=resource, resource_type="api_endpoint")
        time.sleep(0.001)
        Message.log(message_type="authz:action", action=action, http_method="GET")
        time.sleep(0.002)
        Message.log(message_type="authz:policy", policy_id="policy_api_read", effect="allow")
        level_13_cache_layer(f"authz:{user['id']}:{resource}:{action}")
        Message.log(message_type="authz:decision", allowed=True, reason="policy_match")


# ===== LEVEL 11: Authentication Layer =====
def level_11_authentication(token):
    """Level 11 - Authenticate request"""
    with start_action(action_type="auth:authenticate", level=11, auth_type="jwt"):
        Message.log(message_type="auth:token", token_type="Bearer", token_length=256)
        time.sleep(0.002)
        Message.log(message_type="auth:validate", algorithm="RS256", issuer="https://auth.example.com")
        time.sleep(0.003)
        Message.log(message_type="auth:claims", sub="user_123", exp=1735689600, scopes=["read", "write"])
        time.sleep(0.001)
        user = {"id": "user_123", "role": "admin"}
        level_12_authorization(user, "/api/users", "GET")
        Message.log(message_type="auth:success", user_id=user["id"], authenticated=True)


# ===== LEVEL 10: Validation Layer =====
def level_10_validation(request_data):
    """Level 10 - Validate request"""
    with start_action(action_type="validation:validate", level=10, schema="api_v3"):
        Message.log(message_type="validation:schema", schema_name="user_list_request", version="3.0")
        time.sleep(0.001)
        Message.log(message_type="validation:headers", header_count=8, all_valid=True)
        time.sleep(0.001)
        Message.log(message_type="validation:params", params={"page": "1", "limit": "10"}, all_valid=True)
        time.sleep(0.001)
        Message.log(message_type="validation:body", body_size=0, content_type="application/json")
        level_11_authentication(request_data.get("token", ""))
        Message.log(message_type="validation:complete", valid=True, error_count=0)


# ===== LEVEL 9: Business Logic Layer =====
def level_09_business_logic(operation):
    """Level 9 - Execute business logic"""
    with start_action(action_type="business:execute", level=9, domain="user_management"):
        Message.log(message_type="business:operation", operation_name=operation, complexity="medium")
        time.sleep(0.002)
        Message.log(message_type="business:rules", rules_applied=5, rules_skipped=0)
        time.sleep(0.002)
        Message.log(message_type="business:workflow", workflow_id="wf_list_users", step="execute")
        level_10_validation({"token": "Bearer eyJ..."})
        Message.log(message_type="business:complete", result="success", state="completed")


# ===== LEVEL 8: Service Layer =====
def level_08_service(endpoint):
    """Level 8 - Service layer orchestration"""
    with start_action(action_type="service:handle", level=8, service="user_service"):
        Message.log(message_type="service:endpoint", endpoint=endpoint, method="GET")
        time.sleep(0.001)
        Message.log(message_type="service:dependency", services=["cache", "database"], count=2)
        time.sleep(0.001)
        Message.log(message_type="service:circuit_breaker", state="closed", failure_count=0)
        level_09_business_logic("list_users")
        Message.log(message_type="service:complete", status="handled", service_version="3.2.1")


# ===== LEVEL 7: Controller Layer =====
def level_07_controller(request):
    """Level 7 - Controller handling"""
    with start_action(action_type="controller:dispatch", level=7, controller="UserController"):
        Message.log(message_type="controller:match", route="/api/users", action="list")
        time.sleep(0.001)
        Message.log(message_type="controller:middleware", middleware_count=4, middleware_names=["auth", "logging", "ratelimit", "cors"])
        time.sleep(0.001)
        Message.log(message_type="controller:bind", params={"page": 1, "limit": 10})
        level_08_service(request["path"])
        Message.log(message_type="controller:complete", status="dispatched", response_ready=True)


# ===== LEVEL 6: Request Handler =====
def level_06_request_handler(request):
    """Level 6 - HTTP request handler"""
    with start_action(action_type="http:handler", level=6, handler="async_handler"):
        Message.log(message_type="http:receive", method=request["method"], path=request["path"])
        time.sleep(0.001)
        Message.log(message_type="http:headers", content_type="application/json", accept="application/json")
        time.sleep(0.001)
        Message.log(message_type="http:query", query_string="page=1&limit=10", param_count=2)
        level_07_controller(request)
        Message.log(message_type="http:response_prepare", status_code=200, content_length=1024)


# ===== LEVEL 5: Microservice Container =====
def level_05_microservice_container(request):
    """Level 5 - Container-level processing"""
    with start_action(action_type="container:process", level=5, container="user-api-v3"):
        Message.log(message_type="container:receive", container_id="cnt_user_api_01", runtime="docker")
        time.sleep(0.001)
        Message.log(message_type="container:resource", cpu_percent=45, memory_mb=256, threads=8)
        time.sleep(0.001)
        Message.log(message_type="container:health", status="healthy", uptime_seconds=86400)
        level_06_request_handler(request)
        Message.log(message_type="container:complete", processed=True, container_state="running")


# ===== LEVEL 4: Service Mesh =====
def level_04_service_mesh(request):
    """Level 4 - Service mesh routing"""
    with start_action(action_type="mesh:route", level=4, mesh="istio"):
        Message.log(message_type="mesh:incoming", source_service="api-gateway", destination="user-api")
        time.sleep(0.002)
        Message.log(message_type="mesh:route", virtual_service="user-api-routes", subset="v3")
        time.sleep(0.001)
        Message.log(message_type="mesh:telemetry", trace_id="trace_xyz789", span_id="span_abc123")
        level_05_microservice_container(request)
        Message.log(message_type="mesh:complete", route_status="success", latency_ms=5)


# ===== LEVEL 3: API Gateway =====
def level_03_api_gateway(request):
    """Level 3 - API gateway processing"""
    with start_action(action_type="gateway:process", level=3, gateway="kong"):
        Message.log(message_type="gateway:receive", host="api.example.com", port=443)
        time.sleep(0.001)
        Message.log(message_type="gateway:plugins", plugins=["rate-limit", "jwt-auth", "correlation"], count=3)
        time.sleep(0.002)
        Message.log(message_type="gateway:route", service="user-api", strip_path=True)
        time.sleep(0.001)
        level_04_service_mesh(request)
        Message.log(message_type="gateway:complete", status="processed", request_id="req_abc123")


# ===== LEVEL 2: Load Balancer =====
def level_02_load_balancer(request):
    """Level 2 - Load balancing"""
    with start_action(action_type="loadbalancer:distribute", level=2, algorithm="round_robin"):
        Message.log(message_type="lb:receive", vip="10.0.0.100", port=443, protocol="https")
        time.sleep(0.001)
        Message.log(message_type="lb:upstream", upstream_pool="api-gateway-pool", healthy_backends=3)
        time.sleep(0.001)
        Message.log(message_type="lb:selected", backend="api-gateway-02", weight=100)
        time.sleep(0.001)
        Message.log(message_type="lb:session", affinity="none", sticky=False)
        level_03_api_gateway(request)
        Message.log(message_type="lb:complete", distributed=True, backend_response="200")


# ===== LEVEL 1: Application Gateway =====
def level_01_application_gateway(client_request):
    """Level 1 - Edge gateway"""
    with start_action(action_type="gateway:edge", level=1, edge="aws_cloudfront"):
        Message.log(message_type="edge:receive", client_ip=client_request["ip"], country="US")
        time.sleep(0.001)
        Message.log(message_type="edge:cdn", distribution_id="E123ABC", cache_status="MISS")
        time.sleep(0.001)
        Message.log(message_type="edge:waf", waf_id="aws-waf-prod", rules_matched=0, blocked=False)
        time.sleep(0.001)
        Message.log(message_type="edge:tls", tls_version="TLSv1.3", cipher_suite="TLS_AES_256_GCM_SHA384")
        level_02_load_balancer(client_request)
        Message.log(message_type="edge:complete", status="success", edge_response_time_ms=15)


# ===== COMPLEX NESTED SCENARIO: Recursive-like Pattern =====
def recursive_deep_nesting_scenario(depth=25):
    """Generate a recursive-like deep nesting scenario"""
    with start_action(action_type="recursive:process", depth=25, current_depth=depth):
        Message.log(message_type="recursive:depth", current=depth, remaining=depth - 1)
        time.sleep(0.001)

        if depth > 1:
            # Create a child action for each level
            with start_action(action_type="recursive:child", level=depth, child_of=depth):
                Message.log(message_type="recursive:before_recurse", going_to=depth - 1)
                recursive_deep_nesting_scenario(depth - 1)
                Message.log(message_type="recursive:after_recurse", returned_from=depth - 1)
        else:
            Message.log(message_type="recursive:base_case", reached_bottom=True)

        Message.log(message_type="recursive:complete", depth=depth)


# ===== COMPLEX NESTED SCENARIO: Enterprise Request Flow =====
def enterprise_request_flow():
    """Full enterprise request flow with 25 levels"""
    client_request = {
        "ip": "203.0.113.42",
        "method": "GET",
        "path": "/api/users?page=1&limit=10",
        "headers": {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
    }
    level_01_application_gateway(client_request)


# ===== COMPLEX NESTED SCENARIO: Parallel Branches =====
def parallel_branches_scenario():
    """Scenario with multiple parallel branches at various depths"""
    with start_action(action_type="parallel:root", scenario="branches"):
        Message.log(message_type="parallel:start", branches=3)

        # Branch 1: Deep nesting through API flow
        with start_action(action_type="parallel:branch", branch_id=1, name="api_flow"):
            enterprise_request_flow()

        # Branch 2: Direct database access pattern
        with start_action(action_type="parallel:branch", branch_id=2, name="db_flow"):
            with start_action(action_type="branch_2:service"):
                with start_action(action_type="branch_2:repository"):
                    with start_action(action_type="branch_2:database"):
                        with start_action(action_type="branch_2:connection"):
                            with start_action(action_type="branch_2:transaction"):
                                with start_action(action_type="branch_2:query"):
                                    with start_action(action_type="branch_2:result"):
                                        with start_action(action_type="branch_2:transform"):
                                            Message.log(message_type="branch_2:complete")

        # Branch 3: Cache-aside pattern
        with start_action(action_type="parallel:branch", branch_id=3, name="cache_flow"):
            with start_action(action_type="branch_3:api"):
                with start_action(action_type="branch_3:cache"):
                    with start_action(action_type="branch_3:miss"):
                        with start_action(action_type="branch_3:database"):
                            with start_action(action_type="branch_3:query"):
                                with start_action(action_type="branch_3:populate"):
                                    Message.log(message_type="branch_3:success")

        Message.log(message_type="parallel:complete", all_branches=3)


def main():
    """Run all ultra deep nesting examples"""
    print("Creating ultra deep (25 level) nesting log examples...")

    # Example 1: Full enterprise request flow (25 levels)
    print("\n1. Enterprise Request Flow (25 levels)")
    enterprise_request_flow()

    # Example 2: Recursive-like scenario (25 levels)
    print("2. Recursive Deep Nesting (25 levels)")
    recursive_deep_nesting_scenario()

    # Example 3: Multiple parallel branches
    print("3. Parallel Branches Scenario")
    parallel_branches_scenario()

    # Additional deep nesting scenarios
    print("4. Additional Deep Scenarios")
    with start_action(action_type="scenario:multi_tier", tiers=25):
        for i in range(25):
            with start_action(action_type=f"tier_{i+1}:process", tier=i+1):
                Message.log(message_type=f"tier_{i+1}:data", value=i * 10)
                if i > 0:
                    Message.log(message_type=f"tier_{i+1}:parent", parent_tier=i)

    print(f"\nLog created: {log_file}")
    print("\nView with: python view_tree.py example_08_ultra_deep_nesting.log")
    print("\nThis example demonstrates:")
    print("  - 25 levels of nested actions")
    print("  - Enterprise application architecture")
    print("  - Realistic logging at each layer")
    print("  - Multiple complex nesting scenarios")
    print("  - Recursive-like deep nesting patterns")
    print("  - Parallel branch scenarios")


if __name__ == "__main__":
    main()
