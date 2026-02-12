"""Tests for task_id_mode configuration (sqid vs uuid)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, "/mnt/N1/MZ/AMZ/Projects/Prog/a_cross/log-x-py")

import pytest

from logxpy import log
import logxpy.src.logx as logx_module


class TestTaskIdMode:
    """Test task_id_mode configuration."""
    
    def test_default_task_id_mode_is_sqid(self, tmp_path):
        """Default mode should be sqid."""
        log_file = tmp_path / "default_mode.log"
        
        log.init(str(log_file))
        log.info("Test")
        log.shutdown_async()
        
        with open(log_file) as f:
            entry = json.loads(f.readline())
            tid = entry["tid"]
            # Sqid is short (4-12 chars)
            assert len(tid) <= 12, f"Expected Sqid (short), got {tid} ({len(tid)} chars)"
    
    def test_sqid_mode_short_ids(self, tmp_path):
        """Sqid mode produces short hierarchical IDs."""
        log_file = tmp_path / "sqid_mode.log"
        
        # Reset cache
        logx_module._root_task_uuid = None
        logx_module._root_task_uuid_mode = None
        
        log.init(str(log_file), task_id_mode="sqid")
        
        # Log multiple messages - all should have same short tid
        for i in range(5):
            log.info(f"Message {i}")
        
        log.shutdown_async()
        
        with open(log_file) as f:
            lines = f.readlines()
            for line in lines:
                entry = json.loads(line)
                tid = entry["tid"]
                assert len(tid) <= 12, f"Expected short Sqid, got {tid}"
                # Sqid format: PREFIX.COUNTER or PREFIX.COUNTER.CHILD
                assert "." in tid, f"Expected hierarchical format, got {tid}"
    
    def test_uuid_mode_long_ids(self, tmp_path):
        """UUID mode produces UUID4 (36 chars)."""
        log_file = tmp_path / "uuid_mode.log"
        
        # Reset cache
        logx_module._root_task_uuid = None
        logx_module._root_task_uuid_mode = None
        
        log.init(str(log_file), task_id_mode="uuid")
        log.info("Test")
        log.shutdown_async()
        
        with open(log_file) as f:
            entry = json.loads(f.readline())
            tid = entry["tid"]
            # UUID4 is exactly 36 chars
            assert len(tid) == 36, f"Expected UUID4 (36 chars), got {tid} ({len(tid)} chars)"
            # UUID format: 8-4-4-4-12 hex digits
            parts = tid.split("-")
            assert len(parts) == 5, f"Expected UUID format, got {tid}"
    
    def test_uuid_mode_same_across_logs(self, tmp_path):
        """UUID mode should use same UUID for all logs in session."""
        log_file = tmp_path / "uuid_same.log"
        
        # Reset cache
        logx_module._root_task_uuid = None
        logx_module._root_task_uuid_mode = None
        
        log.init(str(log_file), task_id_mode="uuid")
        
        for i in range(10):
            log.info(f"Message {i}")
        
        log.shutdown_async()
        
        with open(log_file) as f:
            lines = f.readlines()
            tids = [json.loads(line)["tid"] for line in lines]
            
            # All should be same UUID
            assert len(set(tids)) == 1, f"Expected same UUID, got {set(tids)}"
    
    def test_mode_switch_regenerates_id(self, tmp_path):
        """Switching mode should regenerate the task ID."""
        # First init with sqid
        logx_module._root_task_uuid = None
        logx_module._root_task_uuid_mode = None
        
        log_file1 = tmp_path / "switch_sqid.log"
        log.init(str(log_file1), task_id_mode="sqid")
        log.info("Sqid message")
        log.shutdown_async()
        
        with open(log_file1) as f:
            tid_sqid = json.loads(f.readline())["tid"]
        
        # Reset and init with uuid
        logx_module._root_task_uuid = None
        logx_module._root_task_uuid_mode = None
        
        log_file2 = tmp_path / "switch_uuid.log"
        log.init(str(log_file2), task_id_mode="uuid")
        log.info("UUID message")
        log.shutdown_async()
        
        with open(log_file2) as f:
            tid_uuid = json.loads(f.readline())["tid"]
        
        # Should be different formats
        assert len(tid_sqid) <= 12, "First should be Sqid"
        assert len(tid_uuid) == 36, "Second should be UUID"
    
    def test_sqid_format_structure(self, tmp_path):
        """Sqid format should be PREFIX.COUNTER[.CHILD]."""
        log_file = tmp_path / "sqid_format.log"
        
        # Reset cache
        logx_module._root_task_uuid = None
        logx_module._root_task_uuid_mode = None
        
        log.init(str(log_file), task_id_mode="sqid")
        log.info("Test")
        log.shutdown_async()
        
        with open(log_file) as f:
            entry = json.loads(f.readline())
            tid = entry["tid"]
            
            # Should have at least one dot
            parts = tid.split(".")
            assert len(parts) >= 2, f"Expected hierarchical format, got {tid}"
            
            # First part: 2-char prefix (base62 PID)
            assert len(parts[0]) == 2, f"Expected 2-char prefix, got {parts[0]}"
            
            # Second part: counter (base62)
            assert parts[1].isalnum(), f"Counter should be alphanumeric, got {parts[1]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
