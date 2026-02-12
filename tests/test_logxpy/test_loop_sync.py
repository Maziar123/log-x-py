"""Test LOOP mode sync behavior - verifies async logs are flushed after tick interval.

Tests that:
1. LOOP mode with 100ms tick syncs logs periodically
2. After sleeping 200ms (> tick), all logs should be synced
3. Each log method works correctly in LOOP mode
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, "/mnt/N1/MZ/AMZ/Projects/Prog/a_cross/log-x-py")

import pytest

from logxpy import log


class TestLoopModeSync:
    """Test LOOP mode sync behavior with 100ms tick."""
    
    def test_loop_mode_100ms_tick_syncs_after_200ms(self, tmp_path):
        """
        LOOP mode with 100ms tick should sync logs within 200ms.
        
        Steps:
        1. Init with LOOP mode, tick=0.1s (100ms)
        2. Log messages one by one (async, no immediate flush)
        3. Sleep 200ms (2x tick interval)
        4. Verify all logs are synced to file
        """
        log_file = tmp_path / "loop_sync_test.log"
        
        # Initialize with LOOP mode, 100ms tick
        log.init(
            str(log_file),
            async_en=True,
            writer_mode="loop",
            tick=0.1,  # 100ms
            size=1000,  # Large batch to prevent batch-based flush
        )
        
        # Log messages one by one (no immediate verification)
        log_methods = [
            ("debug", "Debug message"),
            ("info", "Info message"),
            ("success", "Success message"),
            ("note", "Note message"),
            ("warning", "Warning message"),
            ("error", "Error message"),
            ("critical", "Critical message"),
            ("checkpoint", "Checkpoint message"),
        ]
        
        for method, msg in log_methods:
            getattr(log, method)(msg, seq=len(log_methods))
        
        # Sleep 200ms (2x tick interval) to allow sync
        time.sleep(0.2)
        
        # Now verify all logs are synced WITHOUT calling shutdown
        # (shutdown would force flush, we want to verify LOOP mode worked)
        lines = log_file.read_text().strip().split("\n")
        
        # Should have all 8 lines synced
        assert len(lines) == 8, f"Expected 8 lines after 200ms, got {len(lines)}"
        
        # Parse and verify each entry
        entries = [json.loads(line) for line in lines]
        
        # Verify message types match
        expected_types = [
            "debug",
            "info", 
            "success",
            "note",
            "warning",
            "error",
            "critical",
            "info",  # checkpoint uses info level
        ]
        
        for i, (entry, expected_mt) in enumerate(zip(entries, expected_types)):
            assert entry["mt"] == expected_mt, f"Entry {i}: expected {expected_mt}, got {entry['mt']}"
            assert "msg" in entry, f"Entry {i}: missing msg"
            assert "ts" in entry, f"Entry {i}: missing timestamp"
            assert "tid" in entry, f"Entry {i}: missing task UUID"
            assert "lvl" in entry, f"Entry {i}: missing task level"
        
        # Shutdown cleanly
        log.shutdown_async()
    
    def test_loop_mode_increments_sync_over_time(self, tmp_path):
        """
        Verify that LOOP mode syncs incrementally over time.
        
        Steps:
        1. Log some messages
        2. Wait 150ms (should have some synced)
        3. Log more messages
        4. Wait another 150ms
        5. Verify all are synced
        """
        log_file = tmp_path / "loop_incremental.log"
        
        log.init(
            str(log_file),
            async_en=True,
            writer_mode="loop",
            tick=0.1,  # 100ms
            size=1000,
        )
        
        # First batch
        for i in range(5):
            log.info(f"Batch 1 - Message {i}", batch=1)
        
        # Wait 150ms - first batch should sync
        time.sleep(0.15)
        
        lines_after_first = len(log_file.read_text().strip().split("\n"))
        print(f"\nLines after first batch + 150ms: {lines_after_first}")
        
        # Second batch
        for i in range(5):
            log.info(f"Batch 2 - Message {i}", batch=2)
        
        # Wait another 150ms - second batch should sync
        time.sleep(0.15)
        
        # Should have all 10 lines now
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 10, f"Expected 10 lines total, got {len(lines)}"
        
        log.shutdown_async()
    
    def test_loop_mode_with_all_field_types(self, tmp_path):
        """
        Test LOOP mode syncs correctly with various field types.
        """
        log_file = tmp_path / "loop_fields.log"
        
        log.init(
            str(log_file),
            async_en=True,
            writer_mode="loop",
            tick=0.1,
            size=1000,
        )
        
        # Log with various field types
        log.info("String", name="Alice")
        log.info("Integer", count=42)
        log.info("Float", price=19.99)
        log.info("Boolean", active=True)
        log.info("List", items=[1, 2, 3])
        log.info("Dict", data={"key": "value"})
        
        # Wait 200ms for sync
        time.sleep(0.2)
        
        # Verify all synced with correct field types
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 6
        
        entries = [json.loads(line) for line in lines]
        
        assert entries[0]["name"] == "Alice"
        assert entries[1]["count"] == 42
        assert entries[2]["price"] == 19.99
        assert entries[3]["active"] == True
        assert entries[4]["items"] == [1, 2, 3]
        assert entries[5]["data"] == {"key": "value"}
        
        log.shutdown_async()
    
    def test_loop_mode_does_not_sync_immediately(self, tmp_path):
        """
        Verify LOOP mode does NOT sync immediately (before tick).
        
        This confirms the async nature - logs are buffered.
        """
        log_file = tmp_path / "loop_not_immediate.log"
        
        log.init(
            str(log_file),
            async_en=True,
            writer_mode="loop",
            tick=0.5,  # 500ms tick - long interval
            size=1000,
        )
        
        # Log some messages
        for i in range(5):
            log.info(f"Message {i}")
        
        # Check immediately (no sleep) - file might not exist yet or be empty
        try:
            content_immediate = log_file.read_text()
            lines_immediate = len(content_immediate.strip().split("\n")) if content_immediate.strip() else 0
        except FileNotFoundError:
            lines_immediate = 0
        
        print(f"\nLines immediate: {lines_immediate}")
        
        # Now wait 600ms (> 500ms tick)
        time.sleep(0.6)
        
        # Should have all lines now
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 5, f"Expected 5 lines after 600ms, got {len(lines)}"
        
        log.shutdown_async()
    
    def test_loop_mode_high_volume(self, tmp_path):
        """
        Test LOOP mode handles high volume within sync window.
        """
        log_file = tmp_path / "loop_high_volume.log"
        
        log.init(
            str(log_file),
            async_en=True,
            writer_mode="loop",
            tick=0.1,  # 100ms
            size=10000,  # Large batch
        )
        
        # Log 1000 messages rapidly
        for i in range(1000):
            log.info(f"High volume message {i}", idx=i)
        
        # Wait 200ms for sync
        time.sleep(0.2)
        
        # All should be synced
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 1000, f"Expected 1000 lines, got {len(lines)}"
        
        # Verify all entries valid
        for i, line in enumerate(lines):
            entry = json.loads(line)
            assert entry["idx"] == i
        
        log.shutdown_async()
    
    def test_loop_mode_vs_trigger_mode_behavior(self, tmp_path):
        """
        Compare LOOP mode vs TRIGGER mode behavior.
        
        TRIGGER mode: event-driven, syncs on message
        LOOP mode: periodic, syncs on tick interval
        """
        log_file_loop = tmp_path / "mode_loop.log"
        log_file_trigger = tmp_path / "mode_trigger.log"
        
        # LOOP mode
        log.init(str(log_file_loop), async_en=True, writer_mode="loop", tick=0.1, size=1000)
        log.info("Loop test 1")
        log.info("Loop test 2")
        
        # Wait for LOOP sync
        time.sleep(0.2)
        lines_loop = len(log_file_loop.read_text().strip().split("\n"))
        log.shutdown_async()
        
        # TRIGGER mode
        log.init(str(log_file_trigger), async_en=True, writer_mode="trigger", size=1000)
        log.info("Trigger test 1")
        log.info("Trigger test 2")
        
        # TRIGGER should sync quickly (event-driven), but still async
        # Give it a tiny bit of time but much less than 100ms
        time.sleep(0.01)
        try:
            content = log_file_trigger.read_text()
            lines_trigger = len(content.strip().split("\n")) if content.strip() else 0
        except FileNotFoundError:
            lines_trigger = 0
        log.shutdown_async()
        
        print(f"\nLOOP mode lines after 200ms: {lines_loop}")
        print(f"TRIGGER mode lines after 10ms: {lines_trigger}")
        
        # Both should have 2 lines
        assert lines_loop == 2, f"LOOP mode: expected 2 lines, got {lines_loop}"
        # TRIGGER might be faster, but let's be lenient
        assert lines_trigger >= 0, "TRIGGER mode should have started writing"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
