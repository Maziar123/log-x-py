"""
11_complex_ecommerce.py - Complex E-commerce Order Processing
Demonstrates 7-level nested structure with multiple classes and cross-code calls
"""
import time
from logxpy import log

# Setup output - auto-generate log file from __file__, clean old if exists
log.init(clean=True)


# ============================================================================
# Level 1: Order Service (Entry Point)
# ============================================================================
class OrderService:
    """Main order processing service"""

    @log.logged
    def process_order(self, order_id: int, user_id: int, items: list):
        """LEVEL 1: Entry point for order processing"""
        log.info("=" * 60)
        log.info("🚀 STARTING ORDER PROCESSING", order_id=order_id)
        log.info("=" * 60)

        with log.scope(order_id=order_id, user_id=user_id):
            # Validate user
            user = UserValidator().validate_user(user_id)

            # Process payment
            payment_result = PaymentProcessor().process_payment(order_id, user, items)

            # Fulfill order
            fulfillment = FulfillmentService().fulfill_order(order_id, items, user)

            log.info("=" * 60)
            log.success("✅ ORDER COMPLETED", order_id=order_id, total=payment_result["total"])
            log.info("=" * 60)

            return {
                "order_id": order_id,
                "status": "completed",
                "payment": payment_result,
                "fulfillment": fulfillment,
            }


# ============================================================================
# Level 2: User Validation
# ============================================================================
class UserValidator:
    """Validates user eligibility"""

    @log.logged
    def validate_user(self, user_id: int):
        """LEVEL 2: Validate user account"""
        log.info("─" * 60)
        log.info("👤 Validating User", user_id=user_id)

        # Check user exists
        user = self._fetch_user_from_db(user_id)

        # Check user status
        self._check_user_status(user)

        # Check credit limit
        _credit_check = CreditChecker().check_credit_limit(user)

        log.success("✓ User validated", user_id=user_id, status=user["status"])
        return user

    @log.logged
    def _fetch_user_from_db(self, user_id: int):
        """LEVEL 3: Database query for user"""
        log.debug("📊 Querying database for user", user_id=user_id)
        time.sleep(0.01)  # Simulate DB query
        return {
            "user_id": user_id,
            "name": f"User_{user_id}",
            "status": "active",
            "credit_limit": 10000,
        }

    @log.logged
    def _check_user_status(self, user: dict):
        """LEVEL 3: Verify user account status"""
        log.debug("🔍 Checking user status", status=user["status"])
        if user["status"] != "active":
            raise ValueError(f"User account not active: {user['status']}")
        return True


# ============================================================================
# Level 3: Credit Checker (Deep Validation)
# ============================================================================
class CreditChecker:
    """Checks user credit eligibility"""

    @log.logged
    def check_credit_limit(self, user: dict):
        """LEVEL 3: Check credit availability"""
        log.info("💳 Checking credit limit", user_id=user["user_id"])

        # Get credit history
        history = self._get_credit_history(user["user_id"])

        # Calculate available credit
        available = self._calculate_available_credit(user, history)

        log.success("✓ Credit check passed", available=available)
        return available

    @log.logged
    def _get_credit_history(self, user_id: int):
        """LEVEL 4: Fetch credit transaction history"""
        log.debug("📜 Fetching credit history", user_id=user_id)
        time.sleep(0.01)

        # Simulate external credit bureau call
        bureau_data = self._call_credit_bureau(user_id)

        return {
            "transactions": 15,
            "outstanding": 2000,
            "bureau_score": bureau_data["score"],
        }

    @log.logged
    def _call_credit_bureau(self, user_id: int):
        """LEVEL 5: External credit bureau API call"""
        log.debug("🌐 Calling external credit bureau", user_id=user_id)
        time.sleep(0.02)
        return {"score": 750, "rating": "good"}

    @log.logged
    def _calculate_available_credit(self, user: dict, history: dict):
        """LEVEL 4: Calculate available credit"""
        log.debug("🧮 Calculating available credit")
        available = user["credit_limit"] - history["outstanding"]
        return available


# ============================================================================
# Level 2: Payment Processing
# ============================================================================
class PaymentProcessor:
    """Handles payment processing"""

    @log.logged
    def process_payment(self, order_id: int, user: dict, items: list):
        """LEVEL 2: Process payment for order"""
        log.info("─" * 60)
        log.info("💰 Processing Payment", order_id=order_id)

        # Calculate total
        total = self._calculate_total(items)

        # Apply discounts
        discount = DiscountEngine().calculate_discount(user, total)
        final_total = total - discount

        # Charge payment
        payment = self._charge_payment_gateway(user, final_total)

        log.success("✓ Payment processed", total=final_total, transaction_id=payment["transaction_id"])
        return {
            "total": final_total,
            "discount": discount,
            "transaction_id": payment["transaction_id"],
        }

    @log.logged
    def _calculate_total(self, items: list):
        """LEVEL 3: Calculate order total"""
        log.debug("🧾 Calculating order total", item_count=len(items))
        total = sum(item["price"] * item["quantity"] for item in items)
        return total

    @log.logged
    def _charge_payment_gateway(self, user: dict, amount: float):
        """LEVEL 3: Charge via payment gateway"""
        log.info("💳 Charging payment gateway", amount=amount)

        # Tokenize card
        token = self._tokenize_card(user)

        # Process with gateway
        result = self._gateway_transaction(token, amount)

        return result

    @log.logged
    def _tokenize_card(self, user: dict):
        """LEVEL 4: Tokenize payment card"""
        log.debug("🔐 Tokenizing payment card", user_id=user["user_id"])
        time.sleep(0.01)
        return f"tok_{user['user_id']}_xyz"

    @log.logged
    def _gateway_transaction(self, token: str, amount: float):
        """LEVEL 4: Execute gateway transaction"""
        log.debug("⚡ Executing gateway transaction", token=token[:10], amount=amount)
        time.sleep(0.02)

        # Verify with fraud detection
        fraud_check = FraudDetector().check_transaction(token, amount)

        if not fraud_check["safe"]:
            raise ValueError("Transaction flagged as fraudulent")

        return {
            "transaction_id": f"txn_{int(time.time())}",
            "status": "approved",
            "fraud_score": fraud_check["score"],
        }


# ============================================================================
# Level 5: Fraud Detection (Deep Security)
# ============================================================================
class FraudDetector:
    """Detects fraudulent transactions"""

    @log.logged
    def check_transaction(self, token: str, amount: float):
        """LEVEL 5: Fraud detection check"""
        log.info("🛡️ Running fraud detection", amount=amount)

        # Check velocity
        velocity = self._check_velocity(token)

        # Check pattern
        pattern = self._analyze_pattern(token, amount)

        # ML scoring
        ml_score = self._ml_fraud_score(velocity, pattern, amount)

        safe = ml_score < 0.5
        log.success("✓ Fraud check complete", score=ml_score, safe=safe)

        return {"safe": safe, "score": ml_score}

    @log.logged
    def _check_velocity(self, token: str):
        """LEVEL 6: Check transaction velocity"""
        log.debug("📈 Checking transaction velocity", token=token[:10])
        time.sleep(0.005)
        return {"transactions_last_hour": 2, "risk": "low"}

    @log.logged
    def _analyze_pattern(self, token: str, amount: float):
        """LEVEL 6: Analyze transaction pattern"""
        log.debug("🔍 Analyzing transaction pattern", amount=amount)
        time.sleep(0.005)
        return {"pattern": "normal", "anomaly_score": 0.1}

    @log.logged
    def _ml_fraud_score(self, velocity: dict, pattern: dict, amount: float):
        """LEVEL 6: ML-based fraud scoring"""
        log.debug("🤖 Running ML fraud model")
        time.sleep(0.01)

        # Simulate deep learning inference
        model_result = self._run_deep_model(velocity, pattern, amount)

        return model_result["score"]

    @log.logged
    def _run_deep_model(self, velocity: dict, pattern: dict, amount: float):
        """LEVEL 7: Deep learning model inference (DEEPEST LEVEL)"""
        log.debug("🧠 LEVEL 7: Deep model inference", amount=amount)
        time.sleep(0.01)
        # Simulate neural network
        score = 0.15  # Low fraud score
        return {"score": score, "confidence": 0.95}


# ============================================================================
# Level 3: Discount Engine
# ============================================================================
class DiscountEngine:
    """Calculates applicable discounts"""

    @log.logged
    def calculate_discount(self, user: dict, total: float):
        """LEVEL 3: Calculate discounts"""
        log.info("🎁 Calculating discounts", user_id=user["user_id"])

        # Check user tier
        tier_discount = self._get_tier_discount(user)

        # Check promotions
        promo_discount = self._check_promotions(user, total)

        total_discount = max(tier_discount, promo_discount)
        log.success("✓ Discount applied", discount=total_discount)
        return total_discount

    @log.logged
    def _get_tier_discount(self, user: dict):
        """LEVEL 4: Get loyalty tier discount"""
        log.debug("⭐ Checking loyalty tier", user_id=user["user_id"])
        time.sleep(0.005)
        return 50.0  # $50 tier discount

    @log.logged
    def _check_promotions(self, user: dict, total: float):
        """LEVEL 4: Check active promotions"""
        log.debug("🏷️ Checking promotions", total=total)
        time.sleep(0.005)
        return 30.0  # $30 promo


# ============================================================================
# Level 2: Fulfillment Service
# ============================================================================
class FulfillmentService:
    """Handles order fulfillment"""

    @log.logged
    def fulfill_order(self, order_id: int, items: list, user: dict):
        """LEVEL 2: Fulfill order"""
        log.info("─" * 60)
        log.info("📦 Fulfilling Order", order_id=order_id)

        # Check inventory
        _inventory = InventoryManager().check_inventory(items)

        # Create shipment
        shipment = ShippingService().create_shipment(order_id, items, user)

        # Send notifications
        NotificationService().send_notifications(order_id, user, shipment)

        log.success("✓ Order fulfilled", shipment_id=shipment["shipment_id"])
        return shipment


# ============================================================================
# Level 3: Inventory Management
# ============================================================================
class InventoryManager:
    """Manages inventory"""

    @log.logged
    def check_inventory(self, items: list):
        """LEVEL 3: Check inventory availability"""
        log.info("📊 Checking inventory", item_count=len(items))

        results = []
        for item in items:
            available = self._check_warehouse(item)
            results.append(available)

        log.success("✓ Inventory check complete", available=all(results))
        return results

    @log.logged
    def _check_warehouse(self, item: dict):
        """LEVEL 4: Check warehouse stock"""
        log.debug("🏭 Checking warehouse", item_id=item["id"])
        time.sleep(0.005)
        return True


# ============================================================================
# Level 3: Shipping Service
# ============================================================================
class ShippingService:
    """Handles shipping"""

    @log.logged
    def create_shipment(self, order_id: int, items: list, user: dict):
        """LEVEL 3: Create shipment"""
        log.info("🚚 Creating shipment", order_id=order_id)

        # Calculate shipping
        cost = self._calculate_shipping(items, user)

        # Book carrier
        carrier = self._book_carrier(items, user)

        log.success("✓ Shipment created", carrier=carrier["name"])
        return {
            "shipment_id": f"ship_{order_id}",
            "cost": cost,
            "carrier": carrier,
        }

    @log.logged
    def _calculate_shipping(self, items: list, user: dict):
        """LEVEL 4: Calculate shipping cost"""
        log.debug("💲 Calculating shipping cost")
        time.sleep(0.005)
        return 15.99

    @log.logged
    def _book_carrier(self, items: list, user: dict):
        """LEVEL 4: Book with carrier"""
        log.debug("📮 Booking carrier")
        time.sleep(0.01)
        return {"name": "FastShip", "tracking": "FS123456"}


# ============================================================================
# Level 3: Notification Service
# ============================================================================
class NotificationService:
    """Sends notifications"""

    @log.logged
    def send_notifications(self, order_id: int, user: dict, shipment: dict):
        """LEVEL 3: Send notifications"""
        log.info("📧 Sending notifications", order_id=order_id)

        # Email
        self._send_email(user, order_id)

        # SMS
        self._send_sms(user, shipment)

        log.success("✓ Notifications sent")

    @log.logged
    def _send_email(self, user: dict, order_id: int):
        """LEVEL 4: Send email notification"""
        log.debug("📬 Sending email", user_id=user["user_id"])
        time.sleep(0.01)

    @log.logged
    def _send_sms(self, user: dict, shipment: dict):
        """LEVEL 4: Send SMS notification"""
        log.debug("📱 Sending SMS", tracking=shipment.get("carrier", {}).get("tracking"))
        time.sleep(0.01)


# ============================================================================
# Main Execution
# ============================================================================
def main():
    log.info("=" * 60)
    log.info("🏪 E-COMMERCE ORDER PROCESSING SYSTEM")
    log.info("=" * 60)

    # Create order service
    order_service = OrderService()

    # Sample order
    order_data = {
        "order_id": 12345,
        "user_id": 789,
        "items": [
            {"id": "ITEM001", "name": "Laptop", "price": 999.99, "quantity": 1},
            {"id": "ITEM002", "name": "Mouse", "price": 29.99, "quantity": 2},
        ],
    }

    # Process order (this will cascade through all 7 levels)
    try:
        result = order_service.process_order(**order_data)
        log.info("\n" + "=" * 60)
        log.success("🎉 FINAL RESULT", result=result)
        log.info("=" * 60)
    except ValueError:
        log.exception("❌ Order processing failed")


if __name__ == "__main__":
    main()
