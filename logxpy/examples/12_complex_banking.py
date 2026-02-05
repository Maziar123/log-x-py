"""
12_complex_banking.py - Complex Banking Transaction System
Demonstrates 7-level nested structure with financial operations
"""

import sys
import time

from logxpy import log, to_file

to_file(sys.stdout)


# ============================================================================
# Level 1: Banking API (Entry Point)
# ============================================================================
class BankingAPI:
    """Main banking API entry point"""

    @log.logged
    def transfer_funds(self, from_account: str, to_account: str, amount: float, currency: str = "USD"):
        """LEVEL 1: Initiate fund transfer"""
        log.info("╔" + "═" * 58 + "╗")
        log.info("║  🏦 FUND TRANSFER INITIATED" + " " * 29 + "║")
        log.info("╚" + "═" * 58 + "╝")

        with log.scope(transaction_type="transfer", currency=currency):
            # Generate transaction ID
            txn_id = f"TXN{int(time.time())}"
            log.info("📝 Transaction ID generated", txn_id=txn_id)

            # Validate accounts
            _validation = AccountValidator().validate_transfer(from_account, to_account, amount)

            # Execute transaction
            result = TransactionExecutor().execute_transfer(
                txn_id,
                from_account,
                to_account,
                amount,
                currency,
            )

            # Post-processing
            PostProcessor().finalize_transaction(txn_id, result)

            log.info("╔" + "═" * 58 + "╗")
            log.success("║  ✅ TRANSFER COMPLETED" + " " * 34 + "║")
            log.info("╚" + "═" * 58 + "╝")

            return result


# ============================================================================
# Level 2: Account Validation
# ============================================================================
class AccountValidator:
    """Validates accounts and balances"""

    @log.logged
    def validate_transfer(self, from_account: str, to_account: str, amount: float):
        """LEVEL 2: Validate transfer eligibility"""
        log.info("┌" + "─" * 58 + "┐")
        log.info("│  🔍 VALIDATION PHASE" + " " * 37 + "│")
        log.info("└" + "─" * 58 + "┘")

        # Validate source account
        source = self._validate_source_account(from_account, amount)

        # Validate destination account
        destination = self._validate_destination_account(to_account)

        # Check compliance
        compliance = ComplianceChecker().check_transfer_compliance(
            source,
            destination,
            amount,
        )

        log.success("✓ All validations passed")
        return {"source": source, "destination": destination, "compliance": compliance}

    @log.logged
    def _validate_source_account(self, account: str, amount: float):
        """LEVEL 3: Validate source account"""
        log.info("  ├─ Validating source account", account=account)

        # Fetch account details
        account_data = self._fetch_account_details(account)

        # Check balance
        self._check_sufficient_balance(account_data, amount)

        # Check account status
        self._verify_account_active(account_data)

        log.success("  ✓ Source account valid")
        return account_data

    @log.logged
    def _validate_destination_account(self, account: str):
        """LEVEL 3: Validate destination account"""
        log.info("  ├─ Validating destination account", account=account)

        account_data = self._fetch_account_details(account)
        self._verify_account_active(account_data)

        log.success("  ✓ Destination account valid")
        return account_data

    @log.logged
    def _fetch_account_details(self, account: str):
        """LEVEL 4: Fetch account from database"""
        log.debug("    📊 Fetching account details", account=account)
        time.sleep(0.01)

        # Simulate database query with retry
        data = DatabaseConnector().query_account(account)

        return data

    @log.logged
    def _check_sufficient_balance(self, account_data: dict, amount: float):
        """LEVEL 4: Check balance sufficiency"""
        log.debug("    💰 Checking balance", balance=account_data["balance"], required=amount)
        if account_data["balance"] < amount:
            raise ValueError(f"Insufficient balance: {account_data['balance']} < {amount}")
        return True

    @log.logged
    def _verify_account_active(self, account_data: dict):
        """LEVEL 4: Verify account status"""
        log.debug("    ✓ Verifying account status", status=account_data["status"])
        if account_data["status"] != "active":
            raise ValueError(f"Account not active: {account_data['status']}")
        return True


# ============================================================================
# Level 5: Database Connector (Infrastructure Layer)
# ============================================================================
class DatabaseConnector:
    """Handles database connections"""

    @log.logged
    def query_account(self, account: str):
        """LEVEL 5: Query database for account"""
        log.debug("      🗄️ Database query", account=account)

        # Get connection
        conn = self._get_connection()

        # Execute query
        result = self._execute_query(conn, account)

        # Release connection
        self._release_connection(conn)

        return result

    @log.logged
    def _get_connection(self):
        """LEVEL 6: Get database connection from pool"""
        log.debug("        🔌 Getting DB connection from pool")
        time.sleep(0.005)
        return {"conn_id": "conn_123", "pool": "primary"}

    @log.logged
    def _execute_query(self, conn: dict, account: str):
        """LEVEL 6: Execute database query"""
        log.debug("        ⚡ Executing query", account=account)
        time.sleep(0.01)

        # Simulate actual query execution
        result = self._parse_result_set(account)

        return result

    @log.logged
    def _parse_result_set(self, account: str):
        """LEVEL 7: Parse database result set (DEEPEST)"""
        log.debug("          📄 LEVEL 7: Parsing result set")
        time.sleep(0.005)
        return {
            "account_number": account,
            "balance": 50000.00,
            "status": "active",
            "account_type": "checking",
            "owner": f"Customer_{account[-4:]}",
        }

    @log.logged
    def _release_connection(self, conn: dict):
        """LEVEL 6: Release connection back to pool"""
        log.debug("        🔓 Releasing connection", conn_id=conn["conn_id"])
        time.sleep(0.002)


# ============================================================================
# Level 3: Compliance Checker
# ============================================================================
class ComplianceChecker:
    """Checks regulatory compliance"""

    @log.logged
    def check_transfer_compliance(self, source: dict, destination: dict, amount: float):
        """LEVEL 3: Check compliance rules"""
        log.info("  ├─ Checking compliance", amount=amount)

        # AML check
        aml = self._aml_check(source, destination, amount)

        # Sanctions screening
        sanctions = self._sanctions_screening(source, destination)

        # Regulatory limits
        limits = self._check_regulatory_limits(amount)

        log.success("  ✓ Compliance checks passed")
        return {"aml": aml, "sanctions": sanctions, "limits": limits}

    @log.logged
    def _aml_check(self, source: dict, destination: dict, amount: float):
        """LEVEL 4: Anti-Money Laundering check"""
        log.debug("    🛡️ AML screening", amount=amount)

        # Pattern analysis
        pattern = AMLEngine().analyze_transaction_pattern(source, destination, amount)

        return pattern

    @log.logged
    def _sanctions_screening(self, source: dict, destination: dict):
        """LEVEL 4: Sanctions list screening"""
        log.debug("    🔍 Sanctions screening")
        time.sleep(0.01)
        return {"source_clear": True, "destination_clear": True}

    @log.logged
    def _check_regulatory_limits(self, amount: float):
        """LEVEL 4: Check regulatory limits"""
        log.debug("    📏 Checking regulatory limits", amount=amount)
        time.sleep(0.005)
        daily_limit = 100000.00
        return {"within_limits": amount < daily_limit, "daily_limit": daily_limit}


# ============================================================================
# Level 5: AML Engine (Advanced Analytics)
# ============================================================================
class AMLEngine:
    """Anti-Money Laundering detection engine"""

    @log.logged
    def analyze_transaction_pattern(self, source: dict, destination: dict, amount: float):
        """LEVEL 5: Analyze transaction patterns"""
        log.debug("      🔬 Analyzing transaction patterns")

        # Historical analysis
        history = self._get_transaction_history(source["account_number"])

        # Risk scoring
        risk_score = self._calculate_risk_score(history, amount)

        # ML detection
        ml_result = self._ml_anomaly_detection(source, destination, amount, history)

        return {
            "risk_score": risk_score,
            "ml_detection": ml_result,
            "flagged": risk_score > 0.7,
        }

    @log.logged
    def _get_transaction_history(self, account: str):
        """LEVEL 6: Get historical transactions"""
        log.debug("        📜 Fetching transaction history", account=account)
        time.sleep(0.01)
        return {
            "total_transactions_30d": 45,
            "average_amount": 1500.00,
            "high_value_transactions": 3,
        }

    @log.logged
    def _calculate_risk_score(self, history: dict, amount: float):
        """LEVEL 6: Calculate risk score"""
        log.debug("        🎯 Calculating risk score", amount=amount)
        time.sleep(0.005)

        # Advanced risk calculation
        score = self._advanced_risk_algorithm(history, amount)

        return score

    @log.logged
    def _advanced_risk_algorithm(self, history: dict, amount: float):
        """LEVEL 7: Advanced risk algorithm (DEEPEST)"""
        log.debug("          🧮 LEVEL 7: Running advanced risk algorithm")
        time.sleep(0.01)
        # Simulate complex calculation
        ratio = amount / history["average_amount"]
        base_score = min(ratio / 10, 1.0)
        return round(base_score * 0.3, 2)  # Low risk

    @log.logged
    def _ml_anomaly_detection(self, source: dict, destination: dict, amount: float, history: dict):
        """LEVEL 6: ML-based anomaly detection"""
        log.debug("        🤖 Running ML anomaly detection")
        time.sleep(0.01)
        return {"anomaly": False, "confidence": 0.95}


# ============================================================================
# Level 2: Transaction Executor
# ============================================================================
class TransactionExecutor:
    """Executes the actual transaction"""

    @log.logged
    def execute_transfer(self, txn_id: str, from_account: str, to_account: str, amount: float, currency: str):
        """LEVEL 2: Execute fund transfer"""
        log.info("┌" + "─" * 58 + "┐")
        log.info("│  ⚡ EXECUTION PHASE" + " " * 38 + "│")
        log.info("└" + "─" * 58 + "┘")

        with log.scope(txn_id=txn_id):
            # Begin transaction
            self._begin_transaction(txn_id)

            try:
                # Debit source
                debit_result = LedgerService().debit_account(from_account, amount, currency)

                # Credit destination
                credit_result = LedgerService().credit_account(to_account, amount, currency)

                # Commit transaction
                self._commit_transaction(txn_id)

                log.success("✓ Transaction executed successfully")

                return {
                    "txn_id": txn_id,
                    "status": "completed",
                    "debit": debit_result,
                    "credit": credit_result,
                }
            except Exception:
                # Rollback on error
                self._rollback_transaction(txn_id)
                raise

    @log.logged
    def _begin_transaction(self, txn_id: str):
        """LEVEL 3: Begin database transaction"""
        log.debug("  ├─ BEGIN TRANSACTION", txn_id=txn_id)
        time.sleep(0.005)

    @log.logged
    def _commit_transaction(self, txn_id: str):
        """LEVEL 3: Commit database transaction"""
        log.debug("  ├─ COMMIT TRANSACTION", txn_id=txn_id)
        time.sleep(0.01)

    @log.logged
    def _rollback_transaction(self, txn_id: str):
        """LEVEL 3: Rollback database transaction"""
        log.error("  ├─ ROLLBACK TRANSACTION", txn_id=txn_id)
        time.sleep(0.01)


# ============================================================================
# Level 3: Ledger Service
# ============================================================================
class LedgerService:
    """Manages account ledger entries"""

    @log.logged
    def debit_account(self, account: str, amount: float, currency: str):
        """LEVEL 3: Debit account"""
        log.info("  ├─ Debiting account", account=account, amount=amount)

        # Create ledger entry
        entry = self._create_ledger_entry(account, -amount, "debit", currency)

        # Update balance
        new_balance = self._update_account_balance(account, -amount)

        # Record in audit trail
        AuditLogger().record_entry(entry)

        log.success("  ✓ Account debited", new_balance=new_balance)
        return entry

    @log.logged
    def credit_account(self, account: str, amount: float, currency: str):
        """LEVEL 3: Credit account"""
        log.info("  ├─ Crediting account", account=account, amount=amount)

        # Create ledger entry
        entry = self._create_ledger_entry(account, amount, "credit", currency)

        # Update balance
        new_balance = self._update_account_balance(account, amount)

        # Record in audit trail
        AuditLogger().record_entry(entry)

        log.success("  ✓ Account credited", new_balance=new_balance)
        return entry

    @log.logged
    def _create_ledger_entry(self, account: str, amount: float, entry_type: str, currency: str):
        """LEVEL 4: Create ledger entry"""
        log.debug("    📝 Creating ledger entry", type=entry_type)
        time.sleep(0.005)
        return {
            "entry_id": f"LE{int(time.time())}",
            "account": account,
            "amount": amount,
            "type": entry_type,
            "currency": currency,
            "timestamp": time.time(),
        }

    @log.logged
    def _update_account_balance(self, account: str, amount: float):
        """LEVEL 4: Update account balance"""
        log.debug("    💰 Updating balance", account=account, change=amount)
        time.sleep(0.01)
        # Simulate balance update
        new_balance = 50000.00 + amount
        return new_balance


# ============================================================================
# Level 4: Audit Logger
# ============================================================================
class AuditLogger:
    """Logs audit trail"""

    @log.logged
    def record_entry(self, entry: dict):
        """LEVEL 4: Record audit entry"""
        log.debug("    📋 Recording audit entry", entry_id=entry["entry_id"])

        # Write to audit log
        self._write_audit_log(entry)

        # Archive if needed
        if abs(entry["amount"]) > 10000:
            self._archive_high_value_entry(entry)

    @log.logged
    def _write_audit_log(self, entry: dict):
        """LEVEL 5: Write to audit log"""
        log.debug("      ✍️ Writing audit log")
        time.sleep(0.005)

    @log.logged
    def _archive_high_value_entry(self, entry: dict):
        """LEVEL 5: Archive high-value transaction"""
        log.debug("      📦 Archiving high-value entry", amount=entry["amount"])
        time.sleep(0.005)


# ============================================================================
# Level 2: Post Processor
# ============================================================================
class PostProcessor:
    """Handles post-transaction processing"""

    @log.logged
    def finalize_transaction(self, txn_id: str, result: dict):
        """LEVEL 2: Finalize transaction"""
        log.info("┌" + "─" * 58 + "┐")
        log.info("│  📊 POST-PROCESSING PHASE" + " " * 31 + "│")
        log.info("└" + "─" * 58 + "┘")

        # Send notifications
        NotificationDispatcher().send_transaction_notifications(txn_id, result)

        # Update analytics
        AnalyticsService().update_metrics(result)

        # Generate receipt
        receipt = ReceiptGenerator().generate_receipt(txn_id, result)

        log.success("✓ Post-processing complete")
        return receipt


# ============================================================================
# Level 3: Supporting Services
# ============================================================================
class NotificationDispatcher:
    @log.logged
    def send_transaction_notifications(self, txn_id: str, result: dict):
        """LEVEL 3: Send notifications"""
        log.debug("  📧 Sending notifications", txn_id=txn_id)
        time.sleep(0.01)


class AnalyticsService:
    @log.logged
    def update_metrics(self, result: dict):
        """LEVEL 3: Update analytics"""
        log.debug("  📈 Updating analytics")
        time.sleep(0.005)


class ReceiptGenerator:
    @log.logged
    def generate_receipt(self, txn_id: str, result: dict):
        """LEVEL 3: Generate receipt"""
        log.debug("  🧾 Generating receipt", txn_id=txn_id)
        time.sleep(0.005)
        return {"receipt_id": f"RCP{txn_id}", "format": "PDF"}


# ============================================================================
# Main Execution
# ============================================================================
def main():
    log.info("\n")
    log.info("╔" + "═" * 58 + "╗")
    log.info("║" + " " * 12 + "🏦 BANKING SYSTEM DEMO" + " " * 24 + "║")
    log.info("╚" + "═" * 58 + "╝")
    log.info("\n")

    # Create banking API
    api = BankingAPI()

    # Execute transfer
    try:
        result = api.transfer_funds(
            from_account="ACC123456789",
            to_account="ACC987654321",
            amount=5000.00,
            currency="USD",
        )

        log.info("\n")
        log.info("╔" + "═" * 58 + "╗")
        log.success("║  🎉 FINAL RESULT" + " " * 41 + "║")
        log.info("╠" + "═" * 58 + "╣")
        log.info(f"║  Transaction ID: {result['txn_id']}" + " " * 22 + "║")
        log.info(f"║  Status: {result['status']}" + " " * 39 + "║")
        log.info("╚" + "═" * 58 + "╝")
        log.info("\n")

    except Exception:
        log.exception("❌ Transaction failed")


if __name__ == "__main__":
    main()
