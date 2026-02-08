#!/usr/bin/env python3
"""
Comprehensive 3-Level Nested Actions with Colors - LogXPy Example

This example demonstrates:
1. Deep 3-level nested action hierarchy
2. Colors at each level (level 1, 2, 3)
3. All log types (debug, info, success, note, warning, error, critical)
4. Visual separators and color blocks
5. Data type logging (currency, datetime, enum, etc.)
6. System info logging
7. Colored blocks and separators

Run this script to generate a log file, then view it with:
    ./view.sh              # One-line view (default)
    ./view.sh tree         # Tree view
    ./view.sh nocolor      # No colors
"""

from logxpy.loggerx import log
from logxpy import to_file, start_action
from pathlib import Path
from datetime import datetime
from enum import Enum, auto
import logxpy

# Enable compact format for shorter field names
logxpy.COMPACT_FORMAT = True

# Set output file
log_file = Path(__file__).with_suffix('.log')
to_file(open(log_file, 'w'))


class OrderStatus(Enum):
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()


def separator(char="─", length=60):
    """Create a visual separator line."""
    log.colored(char * length, foreground="dark_gray")


def demo_color_methods():
    """Demonstrate all color and style methods."""
    
    # === 1. BASIC LEVEL COLORS (Automatic) ===
    log.colored("▓" * 60, foreground="dark_gray")
    log.info("1. BASIC LEVEL COLORS (Automatic by log level)")
    log.colored("▓" * 60, foreground="dark_gray")
    
    log.debug("DEBUG message - gray text")
    log.info("INFO message - white text")
    log.success("SUCCESS message - bright green text")
    log.note("NOTE message - yellow text")
    log.warning("WARNING message - bright yellow text")
    log.error("ERROR message - red text")
    log.critical("CRITICAL message - bright red")
    
    # === 2. SET FOREGROUND COLOR ===
    log.colored("─" * 60, foreground="dark_gray")
    log.info("2. SET_FOREGROUND() - Persistent foreground colors")
    log.colored("─" * 60, foreground="dark_gray")
    
    log.set_foreground("cyan")
    log.info("Cyan foreground text (persistent)")
    log.success("Success with cyan foreground")
    log.reset_foreground()
    
    log.set_foreground("green")
    log.info("Green foreground text (persistent)")
    log.reset_foreground()
    
    log.set_foreground("magenta")
    log.info("Magenta foreground text (persistent)")
    log.reset_foreground()
    
    # === 3. SET BACKGROUND COLOR ===
    log.colored("─" * 60, foreground="dark_gray")
    log.info("3. SET_BACKGROUND() - Persistent background colors")
    log.colored("─" * 60, foreground="dark_gray")
    
    log.set_background("yellow")
    log.warning("Yellow background - warning style (persistent)")
    log.reset_background()
    
    log.set_background("red")
    log.error("Red background - error style (persistent)")
    log.reset_background()
    
    # === 4. COMBINED FOREGROUND + BACKGROUND ===
    log.colored("═" * 60, foreground="dark_gray")
    log.info("4. COMBINED FG+BG - High visibility blocks")
    log.colored("═" * 60, foreground="dark_gray")
    
    log.set_foreground("white").set_background("red")
    log.critical("White on RED - CRITICAL ERROR style")
    log.reset_foreground().reset_background()
    
    log.set_foreground("black").set_background("yellow")
    log.warning("Black on YELLOW - HIGHLIGHT style")
    log.reset_foreground().reset_background()
    
    log.set_foreground("white").set_background("green")
    log.success("White on GREEN - SUCCESS banner")
    log.reset_foreground().reset_background()
    
    # === 5. ONE-SHOT COLORED MESSAGES ===
    log.colored("▒" * 60, foreground="dark_gray")
    log.info("5. COLORED() - One-shot color messages")
    log.colored("▒" * 60, foreground="dark_gray")
    
    log.colored("Important alert in red", foreground="red")
    log.colored("Success notification in green", foreground="green")
    log.colored("Info highlight in cyan", foreground="cyan")
    
    log.colored(
        "⚠️  WARNING: Black text on yellow background",
        foreground="black",
        background="yellow"
    )
    log.colored(
        "❌ ERROR: White text on red background",
        foreground="white",
        background="red"
    )
    log.colored(
        "✅ SUCCESS: White text on green background",
        foreground="white",
        background="green"
    )
    
    # === 6. UNICODE BOX BLOCKS ===
    log.colored("█" * 60, foreground="dark_gray")
    log.info("6. COLORED BLOCKS - Unicode box drawing")
    log.colored("█" * 60, foreground="dark_gray")
    
    log.colored(
        "╔══════════════════════════════════════════════════════════╗\n"
        "║  ⚠️  WARNING BLOCK - Yellow background                    ║\n"
        "║  High visibility warning message with Unicode borders    ║\n"
        "╚══════════════════════════════════════════════════════════╝",
        foreground="black",
        background="yellow"
    )
    
    log.colored(
        "╔══════════════════════════════════════════════════════════╗\n"
        "║  ❌ ERROR BLOCK - Red background                          ║\n"
        "║  Critical error message with red background highlight    ║\n"
        "╚══════════════════════════════════════════════════════════╝",
        foreground="white",
        background="red"
    )
    
    log.colored(
        "╔══════════════════════════════════════════════════════════╗\n"
        "║  ✅ SUCCESS BLOCK - Green background                      ║\n"
        "║  Success confirmation with green background highlight    ║\n"
        "╚══════════════════════════════════════════════════════════╝",
        foreground="white",
        background="green"
    )
    
    # === 7. COLOR PALETTE DEMO ===
    log.colored("░" * 60, foreground="dark_gray")
    log.info("7. COLOR PALETTE - All available colors")
    log.colored("░" * 60, foreground="dark_gray")
    
    colors = ["red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    for color in colors:
        log.colored(f"  → {color:12s} foreground example", foreground=color)


def main():
    print(f"Generating comprehensive colored log to {log_file}")

    # === COLOR METHODS DEMO ===
    demo_color_methods()

    # === STARTUP BLOCK ===
    log.colored(
        "╔══════════════════════════════════════════════════════════════════╗\n"
        "║  🚀 APPLICATION STARTUP - E-COMMERCE ORDER SYSTEM v2.0             ║\n"
        "║  Environment: Production  |  Region: US-East-1                   ║\n"
        "╚══════════════════════════════════════════════════════════════════╝",
        foreground="black",
        background="yellow"
    )

    # System info at startup
    log.system_info()
    log.memory_status()

    # === LEVEL 1: API Request ===
    with start_action(action_type="api:request", method="POST", path="/api/v2/orders"):
        log.info("📥 Received order request", user_id=12345, request_id="req-abc-789")
        log.note("Processing high-priority order")
        
        # Log order details
        log.send("Order Details", {
            "order_id": "ORD-2024-001",
            "customer": "alice@example.com",
            "items": 3,
            "total": 299.97
        })

        # === SEPARATOR ===
        separator("─")
        log.colored("🔍 PHASE 1: VALIDATION", foreground="cyan")
        separator("─")

        # === LEVEL 2: Validation ===
        with start_action(action_type="validation:check", schema="order_v2"):
            log.info("Starting validation sequence...")
            
            # Debug info
            log.debug("Loading validation schema", schema_version="2.1.0")
            log.debug("Checking input constraints", max_items=100, max_total=10000.00)
            
            log.success("✅ Schema validation passed")
            log.success("✅ Input constraints satisfied")
            log.success("✅ Business rules validated")
            
            # Note for info
            log.note("Order passes all validation checks")

        # === SEPARATOR ===
        separator("═")
        log.colored("💾 PHASE 2: DATABASE OPERATIONS", foreground="blue")
        separator("═")

        # === LEVEL 2: Database Transaction ===
        with start_action(action_type="db:transaction", isolation="serializable"):
            log.info("Starting database transaction", tx_id="tx-xyz-123")
            
            # === LEVEL 3: User Lookup ===
            with start_action(action_type="db:query", table="users", index="pk_user_id"):
                log.info("Fetching user profile", user_id=12345)
                log.debug("Query: SELECT * FROM users WHERE id = ?", params=[12345])
                
                # Color block for user info
                log.colored(
                    "  👤 User: Alice Johnson\n"
                    "  ⭐ Tier: Premium Member (since 2023)\n"
                    "  💳 Payment: Card ending 4242",
                    foreground="light_blue"
                )
                log.success("User profile loaded", loyalty_points=2500)

            # === LEVEL 3: Inventory Check ===
            with start_action(action_type="db:query", table="inventory", operation="SELECT FOR UPDATE"):
                log.info("Checking inventory availability")
                
                items = [
                    {"sku": "SKU-001", "name": "Wireless Headphones", "qty": 1, "price": 99.99},
                    {"sku": "SKU-042", "name": "USB-C Cable", "qty": 2, "price": 19.99},
                    {"sku": "SKU-108", "name": "Laptop Stand", "qty": 1, "price": 79.99},
                ]
                
                for item in items:
                    log.send(f"  📦 {item['name']}", item)
                
                log.success("All items available in stock")

            # === LEVEL 3: Order Insert ===
            with start_action(action_type="db:insert", table="orders"):
                log.info("Creating order record")
                log.send("Order Data", {
                    "order_id": "ORD-2024-001",
                    "customer_id": 12345,
                    "status": OrderStatus.PENDING,
                    "created_at": datetime.now(),
                    "items": items,
                    "subtotal": 219.97,
                    "tax": 18.20,
                    "shipping": 15.00,
                    "total": 253.17
                })
                log.success("✅ Order #ORD-2024-001 created")
                log.note("Audit log entry added", audit_id="aud-567")

            # === LEVEL 3: Inventory Update ===
            with start_action(action_type="db:update", table="inventory"):
                log.info("Reserving inventory")
                for item in items:
                    log.info(f"Reserving {item['qty']} x {item['sku']}")
                log.success("4 items reserved from inventory")

            # === LEVEL 3: Order Items Insert ===
            with start_action(action_type="db:insert", table="order_items"):
                log.info("Inserting order line items")
                log.success("3 line items created")

        # === SEPARATOR ===
        separator("▓")
        log.colored("💳 PHASE 3: PAYMENT PROCESSING", foreground="magenta")
        separator("▓")

        # === LEVEL 2: Payment Processing ===
        with start_action(action_type="payment:process", gateway="stripe", amount=253.17, currency="USD"):
            log.info("Initializing payment", processor="Stripe")
            log.currency("253.17", "USD")
            
            # === LEVEL 3: Card Validation ===
            with start_action(action_type="payment:validate_card"):
                log.info("Validating card details")
                log.debug("Card brand: Visa", last4="4242", exp="12/26")
                log.success("✅ Card validation passed")
                log.note("3D Secure not required")

            # === LEVEL 3: Fraud Check ===
            with start_action(action_type="payment:fraud_check"):
                log.info("Running fraud detection")
                log.warning("⚠️  Unusual location detected", location="New York, NY", usual="Los Angeles, CA")
                log.note("Risk score: 23/100 (low risk)")
                log.success("Transaction approved by fraud system")

            # === LEVEL 3: Create Charge ===
            with start_action(action_type="payment:create_charge"):
                log.info("Creating charge with Stripe")
                log.colored("⚡ Processing $253.17 charge...", foreground="light_yellow")
                log.success("✅ Payment captured successfully", charge_id="ch_3O...xYz")
                
                # Log receipt info
                log.send("Receipt", {
                    "receipt_id": "RCP-789",
                    "paid_amount": 253.17,
                    "paid_at": datetime.now()
                })

        # === SEPARATOR ===
        separator("░")
        log.colored("📧 PHASE 4: NOTIFICATIONS", foreground="green")
        separator("░")

        # === LEVEL 2: Notifications ===
        with start_action(action_type="notification:send"):
            log.info("Sending confirmation notifications")
            
            # Email
            with start_action(action_type="notification:email", provider="sendgrid"):
                log.info("📧 Sending order confirmation email", to="alice@example.com")
                log.success("Email queued successfully", message_id="msg-xyz")
            
            # SMS
            with start_action(action_type="notification:sms", provider="twilio"):
                log.info("📱 Sending SMS notification", to="+1-555-0123")
                log.success("SMS sent", sid="SM-abc")
            
            # Webhook
            with start_action(action_type="notification:webhook", endpoint="https://merchant.com/callback"):
                log.info("🔔 Calling merchant webhook")
                log.success("Webhook delivered", status_code=200)

        # === COMPLETION BLOCK ===
        separator("█")
        log.colored(
            "╔══════════════════════════════════════════════════════════════════╗\n"
            "║  ✅ ORDER COMPLETED SUCCESSFULLY                                  ║\n"
            "║  Order #ORD-2024-001  |  Total: $253.17                          ║\n"
            "║  Receipt: RCP-789  |  Charge: ch_3O...xYz                        ║\n"
            "╚══════════════════════════════════════════════════════════════════╝",
            foreground="white",
            background="green"
        )
        
        log.success("✅ API response sent", order_id="ORD-2024-001", total=253.17)
        log.memory_status()

    # === SHUTDOWN BLOCK ===
    separator("▒")
    log.colored(
        "╔══════════════════════════════════════════════════════════════════╗\n"
        "║  🏁 APPLICATION SHUTDOWN                                          ║\n"
        "║  All connections closed gracefully                                ║\n"
        "╚══════════════════════════════════════════════════════════════════╝",
        foreground="black",
        background="light_gray"
    )
    
    log.info("Cleaning up resources...")
    log.debug("Closing database connection pool")
    log.debug("Releasing memory buffers")
    log.success("Application shutdown complete")
    
    # Final stats
    log.send("Session Summary", {
        "orders_processed": 1,
        "total_revenue": 253.17,
        "database_queries": 7,
        "api_calls": 3,
        "peak_memory_mb": 42.5
    })

    print(f"\n{'='*60}")
    print(f"Generated log file: {log_file}")
    print(f"{'='*60}")
    print(f"View with:")
    print(f"  ./view.sh              # One-line view (default)")
    print(f"  ./view.sh tree         # Tree view")
    print(f"  ./view.sh nocolor      # No colors")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
