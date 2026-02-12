"""Full sample test - all log methods in one comprehensive test.

This test:
1. Calls ALL log.xxx methods one by one
2. Creates one complete sample log file
3. Verifies every line is correct
4. Tests both async and sync modes
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, "/mnt/N1/MZ/AMZ/Projects/Prog/a_cross/log-x-py")

import pytest

from logxpy import log


class TestFullSampleAsync:
    """Full sample test with async logging."""
    
    def test_all_log_levels(self, tmp_path):
        """Test all log level methods insert correct lines."""
        log_file = tmp_path / "full_sample_async.log"
        
        # Initialize with async
        log.init(str(log_file), async_en=True, size=10, writer_type="block")
        
        # Insert lines one by one - ALL log methods
        log.debug("Debug message", value="debug")
        log.info("Info message", value="info")
        log.success("Success message", value="success")
        log.note("Note message", value="note")
        log.warning("Warning message", value="warning")
        log.error("Error message", value="error")
        log.critical("Critical message", value="critical")
        log.checkpoint("Checkpoint message")
        
        # Shutdown to flush
        log.shutdown_async()
        
        # Read and verify log
        lines = log_file.read_text().strip().split("\n")
        
        # Should have exactly 8 lines (8 log methods)
        assert len(lines) == 8, f"Expected 8 lines, got {len(lines)}"
        
        # Parse each line and verify
        entries = [json.loads(line) for line in lines]
        
        # Verify each entry has required fields
        for entry in entries:
            assert "ts" in entry, "Missing timestamp"
            assert "tid" in entry, "Missing task UUID"
            assert "lvl" in entry, "Missing task level"
            assert "mt" in entry, "Missing message type"
            assert "msg" in entry, "Missing message"
        
        # Verify message types (each method has its own level)
        assert entries[0]["mt"] == "debug"
        assert entries[1]["mt"] == "info"
        assert entries[2]["mt"] == "success"
        assert entries[3]["mt"] == "note"
        assert entries[4]["mt"] == "warning"
        assert entries[5]["mt"] == "error"
        assert entries[6]["mt"] == "critical"
        assert entries[7]["mt"] == "info"  # checkpoint uses info level
        
        # Verify messages
        assert "Debug" in entries[0]["msg"]
        assert "Info" in entries[1]["msg"]
        assert "Success" in entries[2]["msg"]
        assert "Note" in entries[3]["msg"]
        assert "Warning" in entries[4]["msg"]
        assert "Error" in entries[5]["msg"]
        assert "Critical" in entries[6]["msg"]
        assert "Checkpoint" in entries[7]["msg"] or "📍" in entries[7]["msg"]
    
    def test_log_with_various_field_types(self, tmp_path):
        """Test logging with various field types."""
        log_file = tmp_path / "full_sample_fields.log"
        
        log.init(str(log_file), async_en=True, size=10, writer_type="block")
        
        # Different field types
        log.info("String field", name="Alice")
        log.info("Integer field", count=42)
        log.info("Float field", price=19.99)
        log.info("Boolean true", active=True)
        log.info("Boolean false", active=False)
        log.info("List field", items=[1, 2, 3])
        log.info("Dict field", data={"key": "value"})
        log.info("Mixed fields", 
                name="Bob", 
                age=30, 
                score=95.5, 
                active=True,
                tags=["user", "admin"])
        
        log.shutdown_async()
        
        # Verify
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 8
        
        entries = [json.loads(line) for line in lines]
        
        # Verify field values
        assert entries[0]["name"] == "Alice"
        assert entries[1]["count"] == 42
        assert entries[2]["price"] == 19.99
        assert entries[3]["active"] == True
        assert entries[4]["active"] == False
        assert entries[5]["items"] == [1, 2, 3]
        assert entries[6]["data"] == {"key": "value"}
        assert entries[7]["name"] == "Bob"
        assert entries[7]["age"] == 30
        assert entries[7]["score"] == 95.5
        assert entries[7]["active"] == True
        assert entries[7]["tags"] == ["user", "admin"]
    
    def test_log_special_characters(self, tmp_path):
        """Test logging with special characters."""
        log_file = tmp_path / "full_sample_special.log"
        
        log.init(str(log_file), async_en=True, size=10, writer_type="block")
        
        # Special characters in messages
        log.info('Message with "quotes"')
        log.info("Message with 'apostrophes'")
        log.info("Message with \\ backslash")
        log.info("Message with\nnewline")
        log.info("Message with\ttab")
        log.info("Unicode: 你好世界 🌍 ñoño")
        log.info("Path: /tmp/file.txt")
        log.info("JSON-like: {\"key\": \"value\"}")
        
        log.shutdown_async()
        
        # Verify all lines are valid JSON
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 8
        
        for line in lines:
            entry = json.loads(line)  # Should not raise
            assert "msg" in entry
    
    def test_chained_calls(self, tmp_path):
        """Test chained log calls."""
        log_file = tmp_path / "full_sample_chain.log"
        
        log.init(str(log_file), async_en=True, size=10, writer_type="block")
        
        # Chained calls
        log.debug("Step 1").info("Step 2").success("Step 3")
        
        log.shutdown_async()
        
        # Verify 3 lines
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 3
        
        entries = [json.loads(line) for line in lines]
        assert "Step 1" in entries[0]["msg"]
        assert "Step 2" in entries[1]["msg"]
        assert "Step 3" in entries[2]["msg"]


class TestFullSampleSync:
    """Full sample test with sync logging."""
    
    def test_all_levels_sync_mode(self, tmp_path):
        """Test all levels in sync mode."""
        log_file = tmp_path / "full_sample_sync.log"
        
        # Initialize with sync mode
        log.init(str(log_file), async_en=False)
        
        # Insert all levels
        log.debug("Sync debug", value=1)
        log.info("Sync info", value=2)
        log.success("Sync success", value=3)
        log.warning("Sync warning", value=4)
        log.error("Sync error", value=5)
        log.critical("Sync critical", value=6)
        
        # Read and verify (no shutdown needed for sync)
        lines = log_file.read_text().strip().split("\n")
        
        # Should have exactly 6 lines
        assert len(lines) == 6, f"Expected 6 lines, got {len(lines)}"
        
        # Parse and verify
        entries = [json.loads(line) for line in lines]
        
        assert entries[0]["mt"] == "debug"
        assert entries[0]["value"] == 1
        assert entries[1]["mt"] == "info"
        assert entries[1]["value"] == 2
        assert entries[2]["mt"] == "success"
        assert entries[2]["value"] == 3
        assert entries[3]["mt"] == "warning"
        assert entries[3]["value"] == 4
        assert entries[4]["mt"] == "error"
        assert entries[4]["value"] == 5
        assert entries[5]["mt"] == "critical"
        assert entries[5]["value"] == 6
    
    def test_sync_mode_context_manager(self, tmp_path):
        """Test sync mode context manager behavior.
        
        Note: When async is enabled, sync_mode() falls back to BufferingDestination
        (memory), not the file. Only async logs go to the file.
        """
        log_file = tmp_path / "full_sample_sync_ctx.log"
        
        # Start with async
        log.init(str(log_file), async_en=True, size=10, writer_type="block")
        
        # Normal async log - goes to file
        log.info("Async message 1")
        
        # Switch to sync mode - goes to BufferingDestination (memory), not file
        with log.sync_mode():
            log.critical("Critical sync 1")
            log.critical("Critical sync 2")
        
        # Back to async - goes to file
        log.info("Async message 2")
        
        log.shutdown_async()
        
        # Only async logs appear in file
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 2, f"Expected 2 async lines, got {len(lines)}"
        
        entries = [json.loads(line) for line in lines]
        assert "Async" in entries[0]["msg"]
        assert "Async" in entries[1]["msg"]


class TestFullSampleValidation:
    """Comprehensive validation of log output."""
    
    def test_compact_field_names(self, tmp_path):
        """Verify compact field names are used."""
        log_file = tmp_path / "full_sample_compact.log"
        
        log.init(str(log_file), async_en=True, size=10, writer_type="block")
        log.info("Test", data="value")
        log.shutdown_async()
        
        # Read raw line
        line = log_file.read_text().strip()
        
        # Verify compact names (not legacy long names)
        assert '"ts"' in line, "Should use compact 'ts' not 'timestamp'"
        assert '"tid"' in line, "Should use compact 'tid' not 'task_uuid'"
        assert '"lvl"' in line, "Should use compact 'lvl' not 'task_level'"
        assert '"mt"' in line, "Should use compact 'mt' not 'message_type'"
        assert '"msg"' in line, "Should use compact 'msg' not 'message'"
        
        # Should NOT have legacy names
        assert "timestamp" not in line, "Should not have legacy 'timestamp'"
        assert "task_uuid" not in line, "Should not have legacy 'task_uuid'"
        assert "task_level" not in line, "Should not have legacy 'task_level'"
    
    def test_task_uuid_consistency(self, tmp_path):
        """Verify task UUID is consistent (cached)."""
        log_file = tmp_path / "full_sample_tid.log"
        
        log.init(str(log_file), async_en=True, size=10, writer_type="block")
        
        # Log multiple messages
        for i in range(10):
            log.info(f"Message {i}")
        
        log.shutdown_async()
        
        # Read all entries
        lines = log_file.read_text().strip().split("\n")
        entries = [json.loads(line) for line in lines]
        
        # All should have same task UUID (cached root UUID)
        tids = [e["tid"] for e in entries]
        assert len(set(tids)) == 1, f"Task UUIDs should be consistent: {tids}"
    
    def test_task_level_format(self, tmp_path):
        """Verify task level format is correct."""
        log_file = tmp_path / "full_sample_level.log"
        
        log.init(str(log_file), async_en=True, size=10, writer_type="block")
        log.info("Test")
        log.shutdown_async()
        
        line = log_file.read_text().strip()
        entry = json.loads(line)
        
        # lvl should be a list
        assert isinstance(entry["lvl"], list), "lvl should be a list"
        assert entry["lvl"] == [1], "Default level should be [1]"
    
    def test_timestamp_format(self, tmp_path):
        """Verify timestamp is a valid float."""
        log_file = tmp_path / "full_sample_ts.log"
        
        log.init(str(log_file), async_en=True, size=10, writer_type="block")
        log.info("Test")
        log.shutdown_async()
        
        line = log_file.read_text().strip()
        entry = json.loads(line)
        
        # ts should be a float (Unix timestamp)
        assert isinstance(entry["ts"], float), "ts should be a float"
        assert entry["ts"] > 1700000000, "ts should be recent timestamp"
    
    def test_no_trailing_comma(self, tmp_path):
        """Verify no trailing comma in JSON."""
        log_file = tmp_path / "full_sample_json.log"
        
        log.init(str(log_file), async_en=True, size=10, writer_type="block")
        log.info("Test with fields", a=1, b=2)
        log.info("Test no fields")
        log.shutdown_async()
        
        lines = log_file.read_text().strip().split("\n")
        
        for line in lines:
            # Should not have trailing comma before }
            assert ",}" not in line, f"Trailing comma found: {line}"
            # Should be valid JSON
            json.loads(line)  # Will raise if invalid


class TestFullSampleRealWorld:
    """Real-world usage scenarios."""
    
    def test_web_request_logging(self, tmp_path):
        """Simulate web request logging."""
        log_file = tmp_path / "full_sample_web.log"
        
        log.init(str(log_file), async_en=True, size=10, writer_type="block")
        
        # Simulate web request lifecycle
        log.info("Request started", method="GET", path="/api/users", request_id="req-123")
        log.debug("Database query", sql="SELECT * FROM users", duration_ms=5.2)
        log.info("Response sent", status=200, size_bytes=1024, duration_ms=12.5)
        
        log.shutdown_async()
        
        # Verify
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 3
        
        entries = [json.loads(line) for line in lines]
        assert entries[0]["method"] == "GET"
        assert entries[0]["path"] == "/api/users"
        assert entries[1]["sql"] == "SELECT * FROM users"
        assert entries[2]["status"] == 200
    
    def test_error_handling_flow(self, tmp_path):
        """Simulate error handling flow."""
        log_file = tmp_path / "full_sample_error.log"
        
        log.init(str(log_file), async_en=True, size=10, writer_type="block")
        
        try:
            log.info("Operation started")
            log.debug("Processing item", item_id=42)
            raise ValueError("Invalid item")
        except Exception:
            log.exception("Operation failed", operation="process_item")
        
        log.info("Cleanup completed")
        log.shutdown_async()
        
        # Verify
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 4
        
        entries = [json.loads(line) for line in lines]
        assert entries[0]["mt"] == "info"
        assert entries[1]["mt"] == "debug"
        assert entries[2]["mt"] == "error"  # exception logs as error
        assert entries[3]["mt"] == "info"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
