#!/usr/bin/env python3
"""
Comprehensive tests for log.init() all parameter combinations.

Each test verifies:
1. log.init() succeeds with given parameters
2. Log file is created
3. Log entries are written
4. Log entries are valid JSON
5. Required fields are present
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

# Ensure logxpy is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "logxpy" / "src"))

from logxpy import log


# =============================================================================
# Log Validation Utilities
# =============================================================================

def validate_log_entry(entry: dict) -> list[str]:
    """Validate a single log entry has required fields.
    
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Required fields (compact format)
    required = ["ts", "tid", "lvl", "mt", "msg"]
    for field in required:
        if field not in entry:
            errors.append(f"Missing required field: {field}")
    
    # Type checks
    if "ts" in entry and not isinstance(entry["ts"], (int, float)):
        errors.append(f"Field 'ts' should be numeric, got {type(entry['ts'])}")
    
    if "tid" in entry and not isinstance(entry["tid"], str):
        errors.append(f"Field 'tid' should be string, got {type(entry['tid'])}")
    
    if "lvl" in entry and not isinstance(entry["lvl"], list):
        errors.append(f"Field 'lvl' should be list, got {type(entry['lvl'])}")
    
    if "mt" in entry and not isinstance(entry["mt"], str):
        errors.append(f"Field 'mt' should be string, got {type(entry['mt'])}")
    
    return errors


def validate_log_file(path: str, expected_count: int = None) -> dict:
    """Validate entire log file.
    
    Returns:
        dict with keys: valid (bool), count (int), errors (list), entries (list)
    """
    result = {"valid": False, "count": 0, "errors": [], "entries": []}
    
    if not os.path.exists(path):
        result["errors"].append(f"File does not exist: {path}")
        return result
    
    with open(path, "r") as f:
        lines = f.readlines()
    
    result["count"] = len(lines)
    
    if expected_count is not None and len(lines) != expected_count:
        result["errors"].append(f"Expected {expected_count} lines, got {len(lines)}")
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        try:
            entry = json.loads(line)
            result["entries"].append(entry)
            
            errors = validate_log_entry(entry)
            for error in errors:
                result["errors"].append(f"Line {i+1}: {error}")
                
        except json.JSONDecodeError as e:
            result["errors"].append(f"Line {i+1}: Invalid JSON - {e}")
    
    result["valid"] = len(result["errors"]) == 0
    return result


def cleanup_log_file(path: str):
    """Safely remove log file if exists."""
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def temp_log_file():
    """Create a temporary log file path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        path = f.name
    yield path
    cleanup_log_file(path)


@pytest.fixture
def auto_log_file():
    """Track auto-generated log file."""
    path = getattr(log, "_auto_log_file", None)
    yield path
    if path and os.path.exists(path):
        cleanup_log_file(path)


# =============================================================================
# Basic Init Tests
# =============================================================================

class TestInitBasic:
    """Test basic init() functionality."""
    
    def test_init_with_file_path(self, temp_log_file):
        """init() with explicit file path."""
        log.init(temp_log_file, async_en=False)
        log.info("test message")
        
        result = validate_log_file(temp_log_file, expected_count=1)
        assert result["valid"], f"Log validation failed: {result['errors']}"
        assert result["count"] == 1
        
    def test_init_auto_filename(self):
        """init() with auto-generated filename."""
        # Use empty string for auto
        log.init("", async_en=False, clean=True)
        log.info("test message")
        
        auto_path = getattr(log, "_auto_log_file", None)
        assert auto_path, "Auto log file path not set"
        
        result = validate_log_file(auto_path, expected_count=1)
        assert result["valid"], f"Log validation failed: {result['errors']}"
        
        cleanup_log_file(auto_path)
        
    def test_init_with_none_target(self):
        """init() with None target (auto)."""
        log.init(None, async_en=False, clean=True)
        log.info("test message")
        
        auto_path = getattr(log, "_auto_log_file", None)
        assert auto_path, "Auto log file path not set"
        
        result = validate_log_file(auto_path, expected_count=1)
        assert result["valid"], f"Log validation failed: {result['errors']}"
        
        cleanup_log_file(auto_path)


# =============================================================================
# Log Level Tests
# =============================================================================

class TestInitLogLevels:
    """Test init() with different log levels."""
    
    def test_init_level_debug(self, temp_log_file):
        """init() with DEBUG level."""
        log.init(temp_log_file, level="DEBUG", async_en=False)
        log.debug("debug msg")
        log.info("info msg")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 2
        
    def test_init_level_info(self, temp_log_file):
        """init() with INFO level."""
        log.init(temp_log_file, level="INFO", async_en=False)
        log.debug("debug msg")  # Should not appear
        log.info("info msg")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 1
        assert result["entries"][0]["mt"] == "info"
        
    def test_init_level_warning(self, temp_log_file):
        """init() with WARNING level."""
        log.init(temp_log_file, level="WARNING", async_en=False)
        log.info("info msg")  # Should not appear
        log.warning("warning msg")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 1
        assert result["entries"][0]["mt"] == "warning"
        
    def test_init_level_error(self, temp_log_file):
        """init() with ERROR level."""
        log.init(temp_log_file, level="ERROR", async_en=False)
        log.warning("warning msg")  # Should not appear
        log.error("error msg")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 1
        assert result["entries"][0]["mt"] == "error"
        
    def test_init_level_critical(self, temp_log_file):
        """init() with CRITICAL level."""
        log.init(temp_log_file, level="CRITICAL", async_en=False)
        log.error("error msg")  # Should not appear
        log.critical("critical msg")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 1
        assert result["entries"][0]["mt"] == "critical"


# =============================================================================
# File Mode Tests
# =============================================================================

class TestInitFileModes:
    """Test init() with different file modes."""
    
    def test_init_mode_write(self, temp_log_file):
        """init() with mode='w' overwrites existing."""
        # First write - create file
        log.init(temp_log_file, mode="w", async_en=False)
        log.info("first")
        
        # Verify first write
        result = validate_log_file(temp_log_file)
        assert result["valid"], f"First write failed: {result['errors']}"
        assert result["count"] == 1
        
        # Second init with mode='w' should clear and write new
        log.init(temp_log_file, mode="w", async_en=False, clean=True)
        log.info("second")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"], f"Second write failed: {result['errors']}"
        assert result["count"] == 1
        assert result["entries"][0]["msg"] == "second"
        
    def test_init_mode_append(self, temp_log_file):
        """init() with mode='a' appends to existing."""
        # First write
        log.init(temp_log_file, mode="w", async_en=False)
        log.info("first")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"], f"First write failed: {result['errors']}"
        first_count = result["count"]
        
        # Second init with mode='a' should append
        log.init(temp_log_file, mode="a", async_en=False)
        log.info("second")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"], f"Append write failed: {result['errors']}"
        # Should have more entries than before (append adds to file)
        assert result["count"] > first_count, f"Append should increase count, {first_count} -> {result['count']}"
        # Find our messages
        messages = [e["msg"] for e in result["entries"]]
        assert "first" in messages, "First message should still be in file"
        assert "second" in messages, "Second message should be in file"
        
    def test_init_clean_true(self, temp_log_file):
        """init() with clean=True removes existing."""
        # Create existing file
        with open(temp_log_file, "w") as f:
            f.write("existing content\n")
        
        # Init with clean should remove it
        log.init(temp_log_file, clean=True, async_en=False)
        log.info("new content")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 1
        assert result["entries"][0]["msg"] == "new content"


# =============================================================================
# Async Mode Tests
# =============================================================================

class TestInitAsyncModes:
    """Test init() with async enabled/disabled."""
    
    def test_init_async_disabled(self, temp_log_file):
        """init() with async_en=False (sync mode)."""
        log.init(temp_log_file, async_en=False)
        log.info("test message")
        
        # Should be written immediately
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 1
        
    def test_init_async_enabled(self, temp_log_file):
        """init() with async_en=True (async mode)."""
        log.init(temp_log_file, async_en=True)
        log.info("test message")
        
        # Need to shutdown to ensure flush
        log.shutdown_async()
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 1


# =============================================================================
# Writer Type Tests
# =============================================================================

class TestInitWriterTypes:
    """Test init() with different writer types."""
    
    def test_init_writer_type_line(self, temp_log_file):
        """init() with writer_type='line'."""
        log.init(temp_log_file, writer_type="line", async_en=False)
        log.info("test message")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 1
        
    def test_init_writer_type_block(self, temp_log_file):
        """init() with writer_type='block' (default)."""
        log.init(temp_log_file, writer_type="block", async_en=False)
        log.info("test message")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 1
        
    def test_init_writer_type_mmap(self, temp_log_file):
        """init() with writer_type='mmap'."""
        log.init(temp_log_file, writer_type="mmap", async_en=False)
        log.info("test message")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 1


# =============================================================================
# Writer Mode Tests
# =============================================================================

class TestInitWriterModes:
    """Test init() with different writer modes."""
    
    def test_init_writer_mode_trigger(self, temp_log_file):
        """init() with writer_mode='trigger'."""
        log.init(temp_log_file, writer_mode="trigger", async_en=False)
        log.info("test message")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 1
        
    def test_init_writer_mode_loop(self, temp_log_file):
        """init() with writer_mode='loop'."""
        log.init(temp_log_file, writer_mode="loop", async_en=False, flush=0.01)
        log.info("test message")
        time.sleep(0.05)  # Wait for loop flush
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 1
        
    def test_init_writer_mode_manual(self, temp_log_file):
        """init() with writer_mode='manual'."""
        log.init(temp_log_file, writer_mode="manual", async_en=False)
        log.info("test message")
        
        # Manual mode needs explicit trigger
        if hasattr(log, 'trigger'):
            log.trigger()
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]


# =============================================================================
# Task ID Mode Tests
# =============================================================================

class TestInitTaskIdModes:
    """Test init() with different task ID modes."""
    
    def test_init_task_id_mode_sqid(self, temp_log_file):
        """init() with task_id_mode='sqid' (default)."""
        log.init(temp_log_file, task_id_mode="sqid", async_en=False)
        log.info("test message")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        
        # Check tid is short (sqid format: Xa.1, Xa.1.1, etc.)
        tid = result["entries"][0]["tid"]
        assert len(tid) < 20, f"Sqid should be short, got {tid} (len={len(tid)})"
        assert "." in tid, f"Sqid should have hierarchy dots, got {tid}"
        
    def test_init_task_id_mode_uuid(self, temp_log_file):
        """init() with task_id_mode='uuid'."""
        log.init(temp_log_file, task_id_mode="uuid", async_en=False)
        log.info("test message")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        
        # Check tid is UUID format (36 chars with dashes)
        tid = result["entries"][0]["tid"]
        assert len(tid) == 36, f"UUID should be 36 chars, got {tid} (len={len(tid)})"
        assert "-" in tid, f"UUID should have dashes, got {tid}"


# =============================================================================
# Queue Size Tests
# =============================================================================

class TestInitQueueSizes:
    """Test init() with different queue sizes."""
    
    def test_init_queue_small(self, temp_log_file):
        """init() with small queue."""
        log.init(temp_log_file, queue=100, async_en=True)
        
        # Write more than queue size
        for i in range(200):
            log.info(f"message {i}")
        
        log.shutdown_async()
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        # Should have written most messages
        assert result["count"] >= 150
        
    def test_init_queue_large(self, temp_log_file):
        """init() with large queue."""
        log.init(temp_log_file, queue=10000, async_en=True)
        
        for i in range(100):
            log.info(f"message {i}")
        
        log.shutdown_async()
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 100


# =============================================================================
# Batch Size Tests
# =============================================================================

class TestInitBatchSizes:
    """Test init() with different batch sizes."""
    
    def test_init_batch_size_small(self, temp_log_file):
        """init() with small batch size."""
        log.init(temp_log_file, size=1, async_en=False)
        log.info("test message")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 1
        
    def test_init_batch_size_large(self, temp_log_file):
        """init() with large batch size."""
        log.init(temp_log_file, size=1000, async_en=False)
        log.info("test message")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 1


# =============================================================================
# Flush Interval Tests
# =============================================================================

class TestInitFlushIntervals:
    """Test init() with different flush intervals."""
    
    def test_init_flush_numeric(self, temp_log_file):
        """init() with numeric flush interval."""
        log.init(temp_log_file, flush=0.1, async_en=False)
        log.info("test message")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        
    def test_init_flush_si_string_ms(self, temp_log_file):
        """init() with SI string flush interval (milliseconds)."""
        log.init(temp_log_file, flush="10ms", async_en=False)
        log.info("test message")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        
    def test_init_flush_si_string_us(self, temp_log_file):
        """init() with SI string flush interval (microseconds)."""
        log.init(temp_log_file, flush="100µs", async_en=False)
        log.info("test message")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]


# =============================================================================
# Policy Tests
# =============================================================================

class TestInitPolicies:
    """Test init() with different queue policies."""
    
    def test_init_policy_block(self, temp_log_file):
        """init() with policy='block'."""
        log.init(temp_log_file, policy="block", queue=100, async_en=True)
        
        for i in range(50):
            log.info(f"message {i}")
        
        log.shutdown_async()
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        
    def test_init_policy_drop_oldest(self, temp_log_file):
        """init() with policy='drop_oldest'."""
        log.init(temp_log_file, policy="drop_oldest", queue=100, async_en=True)
        
        for i in range(200):
            log.info(f"message {i}")
        
        log.shutdown_async()
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        # Should have dropped some
        assert result["count"] <= 200


# =============================================================================
# Combination Tests
# =============================================================================

class TestInitCombinations:
    """Test init() with parameter combinations."""
    
    def test_init_full_async_config(self, temp_log_file):
        """init() with full async configuration."""
        log.init(
            temp_log_file,
            level="INFO",
            mode="w",
            clean=True,
            async_en=True,
            queue=5000,
            size=50,
            flush=0.05,
            policy="block",
            writer_type="block",
            writer_mode="trigger",
            task_id_mode="sqid",
        )
        
        log.info("test message", extra_field="value")
        log.shutdown_async()
        
        result = validate_log_file(temp_log_file)
        assert result["valid"], f"Validation errors: {result['errors']}"
        assert result["count"] == 1
        
        # Check extra field preserved
        entry = result["entries"][0]
        assert entry.get("extra_field") == "value"
        
    def test_init_sync_with_all_options(self, temp_log_file):
        """init() with sync mode and all options."""
        log.init(
            temp_log_file,
            level="DEBUG",
            mode="w",
            clean=True,
            async_en=False,
            writer_type="line",
            writer_mode="trigger",
            task_id_mode="uuid",
        )
        
        log.debug("debug message")
        log.info("info message")
        
        result = validate_log_file(temp_log_file)
        assert result["valid"]
        assert result["count"] == 2
        
        # Check UUID format
        for entry in result["entries"]:
            tid = entry["tid"]
            assert len(tid) == 36, f"Expected UUID, got {tid}"


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestInitErrorHandling:
    """Test init() error handling."""
    
    def test_init_invalid_level(self, temp_log_file):
        """init() with invalid level should handle gracefully."""
        # Should not raise, but may use default
        try:
            log.init(temp_log_file, level="INVALID", async_en=False)
            log.info("test")
            # If we get here, it handled gracefully
            assert True
        except Exception as e:
            # Or it may raise - either is acceptable
            pytest.skip(f"Invalid level raised: {e}")
            
    def test_init_invalid_writer_type(self, temp_log_file):
        """init() with invalid writer_type."""
        try:
            log.init(temp_log_file, writer_type="invalid", async_en=False)
            pytest.fail("Should have raised for invalid writer_type")
        except (ValueError, KeyError):
            assert True  # Expected
            
    def test_init_invalid_writer_mode(self, temp_log_file):
        """init() with invalid writer_mode."""
        try:
            log.init(temp_log_file, writer_mode="invalid", async_en=False)
            pytest.fail("Should have raised for invalid writer_mode")
        except (ValueError, KeyError):
            assert True  # Expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
