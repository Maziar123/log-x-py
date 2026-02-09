#!/usr/bin/env python3
"""
Tutorial 05: Real-World Scenario - REST API Server
===================================================

This tutorial demonstrates a complete real-world scenario:
- HTTP request/response logging
- Database operations
- Authentication and authorization
- External API calls
- Performance metrics
- Error handling and recovery
- Complex nested operations

This simulates a REST API server handling various requests.

Run this script to generate: tutorial_05_api.log
Then view with: logxpy-view tutorial_05_api.log
"""

import time
import random
from pathlib import Path
from datetime import datetime
from _setup_imports import log, to_file, start_action


def setup_logging():
    """Configure logging to write to a file."""
    log_file = Path(__file__).parent / "tutorial_05_api.log"
    to_file(open(log_file, "w"))
    print(f"✓ Logging to: {log_file}")
    return log_file


# ============================================================================
# Simulated API Components
# ============================================================================

class Request:
    """Simulated HTTP request."""
    def __init__(self, method: str, path: str, headers: dict, body: dict = None):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body or {}
        self.ip = "192.168.1." + str(random.randint(1, 255))
        self.request_id = f"req_{random.randint(1000, 9999)}"


def authenticate_request(request: Request):
    """Authenticate API request."""
    with start_action(action_type="auth:verify", request_id=request.request_id):
        log.info("Authenticating request",
                method=request.method,
                path=request.path,
                ip=request.ip)
        
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header:
            log.warning("Missing authorization header")
            raise ValueError("Unauthorized: Missing auth header")
        
        # Simulate token validation
        time.sleep(0.02)
        
        if auth_header.startswith("Bearer invalid"):
            log.error("Invalid token", token_prefix=auth_header[:20])
            raise ValueError("Unauthorized: Invalid token")
        
        user_id = auth_header.split("_")[-1] if "_" in auth_header else "unknown"
        log.success("Authentication successful", user_id=user_id)
        
        return {"user_id": user_id, "roles": ["user", "api_access"]}


def check_rate_limit(user_id: str):
    """Check rate limiting."""
    with start_action(action_type="ratelimit:check", user_id=user_id):
        time.sleep(0.01)
        
        # Simulate rate limit check
        requests_count = random.randint(1, 150)
        limit = 100
        
        log.info("Checking rate limit",
                current_requests=requests_count,
                limit=limit,
                period="1 hour")
        
        if requests_count > limit:
            log.warning("Rate limit exceeded",
                       requests=requests_count,
                       limit=limit,
                       reset_in_seconds=3600)
            raise ValueError("Rate limit exceeded")
        
        log.success("Rate limit OK",
                   remaining=limit - requests_count)


def query_database(query: str, params: dict):
    """Simulate database query."""
    with start_action(action_type="db:query", query_type="SELECT" if "SELECT" in query else "UPDATE"):
        log.info("Executing database query",
                query=query[:50] + "..." if len(query) > 50 else query,
                params=params)
        
        time.sleep(random.uniform(0.05, 0.15))
        
        if random.random() < 0.05:  # 5% chance of DB error
            log.error("Database query failed",
                     error="Connection pool exhausted",
                     retry_recommended=True)
            raise ConnectionError("Database connection failed")
        
        row_count = random.randint(1, 100)
        log.success("Query executed",
                   rows_affected=row_count,
                   execution_time_ms=random.randint(50, 150))
        
        return [{"id": i, "data": f"row_{i}"} for i in range(min(row_count, 5))]


def call_external_service(service: str, endpoint: str, data: dict):
    """Simulate external API call."""
    with start_action(action_type="external:api_call", service=service):
        log.info("Calling external service",
                service=service,
                endpoint=endpoint,
                payload_size=len(str(data)))
        
        time.sleep(random.uniform(0.1, 0.3))
        
        if random.random() < 0.1:  # 10% chance of failure
            log.error("External service call failed",
                     service=service,
                     status_code=503,
                     error="Service unavailable")
            raise TimeoutError(f"{service} is unavailable")
        
        log.success("External service responded",
                   service=service,
                   status_code=200,
                   response_time_ms=random.randint(100, 300))
        
        return {"status": "success", "data": f"response_from_{service}"}


# ============================================================================
# API Endpoint Handlers
# ============================================================================

def handle_get_users(request: Request):
    """Handle GET /api/users."""
    with start_action(action_type="api:get_users", request_id=request.request_id):
        log.info("Processing GET /api/users request",
                request_id=request.request_id,
                method=request.method,
                path=request.path)
        
        # Authenticate
        auth_data = authenticate_request(request)
        check_rate_limit(auth_data["user_id"])
        
        # Query database
        users = query_database(
            "SELECT * FROM users WHERE active = ?",
            {"active": True}
        )
        
        log.success("Request completed",
                   status_code=200,
                   users_count=len(users))
        
        return {"status": 200, "users": users}


def handle_create_order(request: Request):
    """Handle POST /api/orders."""
    with start_action(action_type="api:create_order", request_id=request.request_id):
        log.info("Processing POST /api/orders request",
                request_id=request.request_id,
                order_items=len(request.body.get("items", [])))
        
        # Authenticate
        auth_data = authenticate_request(request)
        user_id = auth_data["user_id"]
        
        check_rate_limit(user_id)
        
        # Validate order
        with start_action(action_type="order:validate"):
            items = request.body.get("items", [])
            if not items:
                log.error("Order validation failed", reason="No items in order")
                raise ValueError("Order must contain items")
            
            total = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
            log.info("Order validated",
                    items_count=len(items),
                    total_amount=total)
        
        # Process payment
        with start_action(action_type="payment:process", amount=total):
            payment_response = call_external_service(
                "payment_gateway",
                "/api/v1/charge",
                {"amount": total, "currency": "USD"}
            )
            log.success("Payment processed",
                       transaction_id=payment_response.get("data"))
        
        # Reserve inventory
        with start_action(action_type="inventory:reserve"):
            for item in items:
                inventory = query_database(
                    "UPDATE inventory SET quantity = quantity - ? WHERE product_id = ?",
                    {"quantity": item["quantity"], "product_id": item["product_id"]}
                )
            log.success("Inventory reserved", items=len(items))
        
        # Create order in database
        order_id = f"ORD-{random.randint(10000, 99999)}"
        query_database(
            "INSERT INTO orders (id, user_id, total, status) VALUES (?, ?, ?, ?)",
            {"id": order_id, "user_id": user_id, "total": total, "status": "pending"}
        )
        
        # Send notification
        with start_action(action_type="notification:send"):
            call_external_service(
                "notification_service",
                "/api/v1/send",
                {"user_id": user_id, "template": "order_confirmation", "order_id": order_id}
            )
            log.success("Notification sent", channel="email")
        
        log.success("Order created successfully",
                   order_id=order_id,
                   total_amount=total,
                   status_code=201)
        
        return {"status": 201, "order_id": order_id}


def handle_analytics_report(request: Request):
    """Handle GET /api/analytics/report."""
    with start_action(action_type="api:analytics_report", request_id=request.request_id):
        log.info("Processing analytics report request",
                request_id=request.request_id,
                report_type=request.body.get("type", "daily"))
        
        # Authenticate
        auth_data = authenticate_request(request)
        
        # Check permissions
        if "admin" not in auth_data.get("roles", []):
            log.warning("Insufficient permissions",
                       user_id=auth_data["user_id"],
                       required_role="admin")
            return {"status": 403, "error": "Forbidden"}
        
        # Fetch data from multiple sources in parallel (simulated)
        report_data = {}
        
        # Source 1: Database metrics
        with start_action(action_type="analytics:db_metrics"):
            metrics = query_database(
                "SELECT metric, value FROM analytics WHERE date = CURRENT_DATE",
                {}
            )
            report_data["database_metrics"] = metrics
        
        # Source 2: External analytics service
        with start_action(action_type="analytics:external"):
            external_data = call_external_service(
                "analytics_service",
                "/api/v1/metrics",
                {"date": str(datetime.now().date())}
            )
            report_data["external_metrics"] = external_data
        
        # Source 3: Cache statistics
        with start_action(action_type="analytics:cache_stats"):
            time.sleep(0.05)
            cache_stats = {"hit_rate": 0.85, "miss_rate": 0.15, "size_mb": 245}
            report_data["cache_stats"] = cache_stats
            log.info("Cache statistics retrieved", **cache_stats)
        
        # Generate report
        with start_action(action_type="report:generate"):
            time.sleep(0.1)
            report_id = f"RPT-{random.randint(10000, 99999)}"
            log.success("Report generated",
                       report_id=report_id,
                       sections=len(report_data))
        
        log.success("Analytics report completed",
                   report_id=report_id,
                   status_code=200)
        
        return {"status": 200, "report_id": report_id, "data": report_data}


# ============================================================================
# Main simulation
# ============================================================================

def simulate_api_requests():
    """Simulate various API requests."""
    
    # Request 1: Successful GET users
    log.info("=== Incoming Request #1 ===")
    req1 = Request(
        "GET",
        "/api/users",
        {"Authorization": "Bearer token_user_123", "User-Agent": "Mozilla/5.0"}
    )
    try:
        response1 = handle_get_users(req1)
        log.success("Request #1 completed", status=response1["status"])
    except Exception as e:
        log.error("Request #1 failed", error=str(e))
    
    time.sleep(0.1)
    
    # Request 2: Successful order creation
    log.info("=== Incoming Request #2 ===")
    req2 = Request(
        "POST",
        "/api/orders",
        {"Authorization": "Bearer token_user_456", "Content-Type": "application/json"},
        body={
            "items": [
                {"product_id": "PROD-001", "quantity": 2, "price": 29.99},
                {"product_id": "PROD-002", "quantity": 1, "price": 49.99}
            ]
        }
    )
    try:
        response2 = handle_create_order(req2)
        log.success("Request #2 completed", status=response2["status"])
    except Exception as e:
        log.error("Request #2 failed", error=str(e))
    
    time.sleep(0.1)
    
    # Request 3: Failed authentication
    log.info("=== Incoming Request #3 ===")
    req3 = Request(
        "GET",
        "/api/users",
        {"Authorization": "Bearer invalid_token"}
    )
    try:
        response3 = handle_get_users(req3)
    except Exception as e:
        log.error("Request #3 authentication failed", error=str(e))
    
    time.sleep(0.1)
    
    # Request 4: Analytics report (with external service timeout)
    log.info("=== Incoming Request #4 ===")
    req4 = Request(
        "GET",
        "/api/analytics/report",
        {"Authorization": "Bearer token_admin_789"},
        body={"type": "daily"}
    )
    try:
        response4 = handle_analytics_report(req4)
        log.success("Request #4 completed", status=response4["status"])
    except Exception as e:
        log.error("Request #4 failed", error=str(e))
    
    time.sleep(0.1)
    
    # Request 5: Order creation with invalid data
    log.info("=== Incoming Request #5 ===")
    req5 = Request(
        "POST",
        "/api/orders",
        {"Authorization": "Bearer token_user_999", "Content-Type": "application/json"},
        body={"items": []}  # Empty items - will fail validation
    )
    try:
        response5 = handle_create_order(req5)
    except Exception as e:
        log.error("Request #5 failed validation", error=str(e))


def main():
    """Run the API simulation."""
    log_file = setup_logging()
    
    print("\n" + "=" * 70)
    print("Tutorial 05: Real-World API Server Simulation")
    print("=" * 70)
    
    with start_action(action_type="server:startup"):
        log.info("API server starting",
                version="1.0.0",
                environment="production",
                port=8080)
        time.sleep(0.05)
        log.success("Server started successfully")
    
    # Simulate API requests
    simulate_api_requests()
    
    with start_action(action_type="server:shutdown"):
        log.info("Shutting down server")
        time.sleep(0.05)
        log.success("Server stopped gracefully")
    
    log.success("Tutorial completed!", tutorial="05_real_world_api")
    
    print("\n" + "=" * 70)
    print("✓ Log file created successfully!")
    print("=" * 70)
    print(f"\nTo view the complete log tree:")
    print(f"  logxpy-view {log_file}")
    print(f"\nTo view only API requests:")
    print(f"  logxpy-view --select 'starts_with(action_type, `api:`)' {log_file}")
    print(f"\nTo view only failed operations:")
    print(f"  logxpy-view --action-status failed {log_file}")
    print(f"\nTo view with human-readable times:")
    print(f"  logxpy-view --human-readable {log_file}")
    print(f"\nTo filter by request ID (example):")
    print(f"  logxpy-view --keyword 'req_' {log_file}")
    print(f"\nTo export to HTML for sharing:")
    print(f"  logxpy-view --export-html report.html {log_file}")


if __name__ == "__main__":
    main()
