#!/usr/bin/env python3
"""Example 08: Ultra Deep Nesting (25 Levels) - enterprise system simulation."""

import time

from logxpy import log, start_action


# Level 25-21: Network/Serialization layers
def level_25_network():
    with start_action(action_type="network:transmit", level=25, protocol="TCP"):
        log.info("Packet create", size_bytes=1024)
        time.sleep(0.001)
        log.success("Transmitted", destination="client:ip", port=443, encrypted=True)


def level_24_encryption():
    with start_action(action_type="encryption:process", level=24, algorithm="AES-256-GCM"):
        log.info("Key retrieve", key_id="key_prod_42", keyvault="aws:kms")
        time.sleep(0.002)
        log.info("Encrypting", input_size=1024, output_size=1040)
        level_25_network()
        log.success("Encrypted", cipher_version="v2")


def level_23_compression():
    with start_action(action_type="compression:compress", level=23, algorithm="gzip"):
        log.info("Analyzing", original_size=5120, content_type="application/json")
        time.sleep(0.002)
        log.info("Compressed", ratio=5.0, saved_bytes=4096)
        level_24_encryption()


def level_22_serialization(data):
    with start_action(action_type="serialization:serialize", level=22, format="json"):
        log.info("Validating schema", schema="api_response_v3")
        time.sleep(0.001)
        log.info("Encoding", field_count=15, nested_objects=5)
        level_23_compression()
        log.success("Serialized", charset="utf-8")


def level_21_response_builder(data):
    with start_action(action_type="response:build", level=21, status_code=200):
        log.info("Headers", content_type="application/json", cache_control="no-cache")
        log.info("Body", data_items=len(data), total_size=4800)
        level_22_serialization(data)
        log.success("Response ready", headers_count=8)


# Level 20-16: Data processing layers
def level_20_data_transformer(raw_data):
    with start_action(action_type="transform:execute", level=20, transformer="api_v3"):
        log.info("Input", source_type="db_record", count=len(raw_data))
        log.info("Field mapping", mappings=10, renames=3)
        transformed = [{"id": i, "name": f"item_{i}"} for i in range(10)]
        level_21_response_builder(transformed)
        log.success("Transformed", output_count=len(transformed))


def level_19_result_parser(db_result):
    with start_action(action_type="parse:database_result", level=19):
        log.info("Parsing", rows=len(db_result), columns=8)
        log.info("Null handling", null_count=2, strategy="default")
        level_20_data_transformer(db_result)
        log.success("Parsed", errors=0)


def level_18_query_executor(sql, params):
    with start_action(action_type="database:execute", level=18):
        log.info("Executing", sql=sql[:50] + "...", params_count=len(params))
        time.sleep(0.005)
        log.info("Fetching", rows_fetched=10, buffers=5)
        result = [{"id": i, "name": f"user_{i}"} for i in range(10)]
        level_19_result_parser(result)
        log.success("Complete", rows_returned=len(result))


def level_17_query_optimizer(sql, params):
    with start_action(action_type="database:optimize", level=17):
        log.info("Analyzing", tables=["users", "profiles"], joins=1)
        log.info("Index selected", index="users_email_idx", reason="equality_filter")
        log.info("Cost estimate", initial=1000, optimized=50)
        level_18_query_executor(sql, params)


def level_16_query_builder(table, filters):
    with start_action(action_type="database:build_query", level=16):
        log.info("Building", table=table, columns=["id", "name", "email"])
        log.info("Where", clauses=len(filters), operators=["=", "LIKE"])
        sql = f"SELECT id, name, email FROM {table} WHERE {' AND '.join(filters)}"
        level_17_query_optimizer(sql, ["user@example.com"])
        log.success("Built", query_length=len(sql))


# Level 15-11: Database/Auth layers
def level_15_transaction():
    with start_action(action_type="database:transaction", level=15, isolation="read_committed"):
        log.info("Begin", transaction_id="txn_12345", readonly=True)
        log.info("Lock", lock_type="access_share", tables=["users"])
        level_16_query_builder("users", ["email = ?", "status = 'active'"])
        log.success("Committed", transaction_id="txn_12345")


def level_14_connection_pool():
    with start_action(action_type="database:pool_acquire", level=14):
        log.info("Pool status", size=20, available=5, in_use=15)
        log.info("Acquired", connection_id="conn_42", wait_ms=1)
        level_15_transaction()
        log.success("Released", connection_id="conn_42")


def level_13_cache(key):
    with start_action(action_type="cache:get", level=13, cache_type="redis"):
        log.info("Lookup", key=key)
        log.warning("Cache miss", reason="expired")
        log.info("Backfill", strategy="lazy_loading", ttl=3600)
        level_14_connection_pool()
        log.success("Cached", key=key, ttl=3600)


def level_12_authorization(user, resource, action):
    with start_action(action_type="auth:authorize", level=12):
        log.info("Subject", user_id=user["id"], role=user["role"])
        log.info("Resource", resource=resource, action=action)
        log.info("Policy", policy_id="policy_api_read", effect="allow")
        level_13_cache(f"authz:{user['id']}:{resource}:{action}")
        log.success("Authorized", allowed=True)


def level_11_authentication(token):
    with start_action(action_type="auth:authenticate", level=11, auth_type="jwt"):
        log.info("Token", token_type="Bearer", token_length=256)
        log.info("Validating", algorithm="RS256", issuer="https://auth.example.com")
        time.sleep(0.003)
        user = {"id": "user_123", "role": "admin"}
        level_12_authorization(user, "/api/users", "GET")
        log.success("Authenticated", user_id=user["id"])


# Level 10-6: Application layers
def level_10_validation(request_data):
    with start_action(action_type="validation:validate", level=10):
        log.info("Schema", schema_name="user_list_request", version="3.0")
        log.info("Headers", header_count=8, all_valid=True)
        log.info("Params", params={"page": "1", "limit": "10"})
        level_11_authentication(request_data.get("token", ""))
        log.success("Valid", error_count=0)


def level_09_business_logic(operation):
    with start_action(action_type="business:execute", level=9, domain="user_management"):
        log.info("Operation", name=operation, complexity="medium")
        log.info("Rules", applied=5, skipped=0)
        level_10_validation({"token": "Bearer eyJ..."})
        log.success("Complete", state="completed")


def level_08_service(endpoint):
    with start_action(action_type="service:handle", level=8, service="user_service"):
        log.info("Endpoint", endpoint=endpoint, method="GET")
        log.info("Dependencies", services=["cache", "database"])
        log.info("Circuit breaker", state="closed", failure_count=0)
        level_09_business_logic("list_users")
        log.success("Handled", service_version="3.2.1")


def level_07_controller(request):
    with start_action(action_type="controller:dispatch", level=7):
        log.info("Route match", route="/api/users", action="list")
        log.info("Middleware", names=["auth", "logging", "ratelimit", "cors"])
        level_08_service(request["path"])
        log.success("Dispatched", response_ready=True)


def level_06_request_handler(request):
    with start_action(action_type="http:handler", level=6):
        log.info("Received", method=request["method"], path=request["path"])
        log.info("Query", query_string="page=1&limit=10", param_count=2)
        level_07_controller(request)
        log.success("Response", status_code=200, content_length=1024)


# Level 5-1: Infrastructure layers
def level_05_container(request):
    with start_action(action_type="container:process", level=5):
        log.info("Container", container_id="cnt_user_api_01", runtime="docker")
        log.info("Resources", cpu_percent=45, memory_mb=256, threads=8)
        level_06_request_handler(request)
        log.success("Processed")


def level_04_service_mesh(request):
    with start_action(action_type="mesh:route", level=4, mesh="istio"):
        log.info("Routing", source="api-gateway", destination="user-api")
        log.info("Telemetry", trace_id="trace_xyz789", span_id="span_abc123")
        level_05_container(request)
        log.success("Routed", latency_ms=5)


def level_03_api_gateway(request):
    with start_action(action_type="gateway:process", level=3, gateway="kong"):
        log.info("Received", host="api.example.com", port=443)
        log.info("Plugins", names=["rate-limit", "jwt-auth", "correlation"])
        level_04_service_mesh(request)
        log.success("Processed", request_id="req_abc123")


def level_02_load_balancer(request):
    with start_action(action_type="loadbalancer:distribute", level=2):
        log.info("Received", vip="10.0.0.100", port=443, protocol="https")
        log.info("Selected backend", backend="api-gateway-02", healthy_backends=3)
        level_03_api_gateway(request)
        log.success("Distributed", backend_response="200")


def level_01_edge_gateway(client_request):
    with start_action(action_type="gateway:edge", level=1, edge="aws_cloudfront"):
        log.info("Client", client_ip=client_request["ip"], country="US")
        log.info("CDN", distribution_id="E123ABC", cache_status="MISS")
        log.info("WAF", rules_matched=0, blocked=False)
        log.info("TLS", version="TLSv1.3", cipher="TLS_AES_256_GCM_SHA384")
        level_02_load_balancer(client_request)
        log.success("Edge complete", response_time_ms=15)


# Run the full 25-level enterprise flow
client_request = {
    "ip": "203.0.113.42",
    "method": "GET",
    "path": "/api/users?page=1&limit=10",
}
level_01_edge_gateway(client_request)

# Recursive 25-level scenario
def recursive_deep(depth=25):
    with start_action(action_type="recursive:process", depth=depth):
        log.info("Depth", current=depth, remaining=depth - 1)
        if depth > 1:
            with start_action(action_type="recursive:child", level=depth):
                recursive_deep(depth - 1)
        else:
            log.success("Base case reached")
        log.success("Complete", depth=depth)

recursive_deep()

print("✓ Log created: example_08_ultra_deep_nesting.log")
