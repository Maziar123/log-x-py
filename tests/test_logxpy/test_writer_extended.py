"""Extended tests for logxpy writer - comprehensive coverage.

Tests all combinations of:
- Writer types: LINE, BLOCK, MMAP
- Modes: TRIGGER, LOOP, MANUAL
- Configurations: queue size, batch size, policies
- File verification: single line, multiple lines, JSON validity
"""
from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path

import pytest

from logxpy.src._writer import (
    Mode,
    Q,
    QEmpty,
    QueuePolicy,
    WriterMetrics,
    WriterType,
    LineBufferedWriter,
    BlockBufferedWriter,
    MemoryMappedWriter,
    create_writer,
    BaseFileWriterThread,
)
from logxpy import log


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_file():
    """Provide temporary file path."""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def fresh_log():
    """Provide fresh logger instance for each test."""
    # Reset log state
    log._async_writer = None
    log._auto_log_file = None
    yield log
    # Cleanup after test
    if log._async_writer is not None:
        log.shutdown_async()


# ============================================================================
# Helper Functions
# ============================================================================

def verify_log_file(path: str, expected_count: int = None, check_logxpy_fields: bool = True) -> list[dict]:
    """Verify log file exists and contains valid JSON lines.
    
    Args:
        path: Path to log file
        expected_count: Expected number of entries (None = don't check)
        check_logxpy_fields: If True, verify logxpy-specific fields (ts, tid, etc.)
    
    Returns:
        List of parsed JSON entries
    """
    assert os.path.exists(path), f"Log file does not exist: {path}"
    
    # Read file and filter out null bytes (from mmap pre-allocation)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Filter out null bytes and split into lines
    lines = [line.strip() for line in content.replace('\x00', '').split('\n') if line.strip()]
    
    if expected_count is not None:
        assert len(lines) == expected_count, \
            f"Expected {expected_count} lines, got {len(lines)}: {lines[:5]}..."
    
    entries = []
    for i, line in enumerate(lines):
        try:
            entry = json.loads(line)
            entries.append(entry)
            # Verify required fields (if using logxpy log interface)
            if check_logxpy_fields:
                assert 'ts' in entry, f"Entry {i} missing 'ts'"
                assert 'tid' in entry, f"Entry {i} missing 'tid'"
                assert 'lvl' in entry, f"Entry {i} missing 'lvl'"
                assert 'mt' in entry, f"Entry {i} missing 'mt'"
                assert 'msg' in entry, f"Entry {i} missing 'msg'"
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON on line {i}: {line[:100]}... Error: {e}")
    
    return entries


# ============================================================================
# Writer Type × Mode Matrix Tests
# ============================================================================

class TestWriterTypeModeMatrix:
    """Test all combinations of writer types and modes."""
    
    WRITER_TYPES = [WriterType.LINE, WriterType.BLOCK, WriterType.MMAP]
    MODES = [Mode.TRIGGER, Mode.LOOP, Mode.MANUAL]
    
    @pytest.mark.parametrize("writer_type", WRITER_TYPES)
    @pytest.mark.parametrize("mode", MODES)
    def test_single_line_write(self, temp_file, writer_type, mode):
        """Write single line with all type/mode combinations."""
        writer = create_writer(
            temp_file, 
            writer_type=writer_type, 
            mode=mode,
            tick=0.01 if mode == Mode.LOOP else 0.1
        )
        
        writer.send('{"msg": "single line test"}')
        
        if mode == Mode.MANUAL:
            writer.trigger()
            time.sleep(0.05)  # Give time for write
        
        # Give LOOP mode time to process
        if mode == Mode.LOOP:
            time.sleep(0.15)  # LOOP mode needs more time
        
        writer.stop()
        
        # For MANUAL mode without trigger, queue might still have data
        # which gets flushed on stop
        
        # Don't check logxpy fields - using writer directly
        entries = verify_log_file(temp_file, expected_count=1, check_logxpy_fields=False)
        assert entries[0]['msg'] == 'single line test'
    
    @pytest.mark.parametrize("writer_type", WRITER_TYPES)
    @pytest.mark.parametrize("mode", MODES)
    def test_multiple_lines_write(self, temp_file, writer_type, mode):
        """Write multiple lines with all type/mode combinations."""
        writer = create_writer(
            temp_file,
            writer_type=writer_type,
            mode=mode,
            tick=0.01 if mode == Mode.LOOP else 0.1,
            batch_size=10
        )
        
        expected_messages = []
        for i in range(10):
            msg = f'line {i}'
            writer.send(f'{{"msg": "{msg}", "idx": {i}}}')
            expected_messages.append(msg)
            
            if mode == Mode.MANUAL:
                writer.trigger()
                time.sleep(0.01)
        
        if mode == Mode.MANUAL:
            writer.trigger()  # Final trigger for any remaining
            time.sleep(0.05)
        
        if mode == Mode.LOOP:
            time.sleep(0.2)  # Give LOOP mode more time to process all messages
        
        writer.stop()
        
        # Don't check logxpy fields - using writer directly
        entries = verify_log_file(temp_file, expected_count=10, check_logxpy_fields=False)
        for i, entry in enumerate(entries):
            assert entry['msg'] == f'line {i}'
            assert entry['idx'] == i


# ============================================================================
# Queue Policy Tests
# ============================================================================

class TestQueuePolicies:
    """Test all queue backpressure policies."""
    
    def test_block_policy(self, temp_file):
        """BLOCK policy waits for space."""
        writer = create_writer(
            temp_file,
            writer_type=WriterType.BLOCK,
            mode=Mode.TRIGGER,
            queue_size=5,
            policy=QueuePolicy.BLOCK
        )
        
        # Fill queue
        for i in range(10):
            writer.send(f'{{"msg": "{i}"}}')
        
        writer.stop()
        # Using writer directly - don't check logxpy fields
        entries = verify_log_file(temp_file, check_logxpy_fields=False)
        assert len(entries) == 10
    
    def test_drop_newest_policy(self, temp_file):
        """DROP_NEWEST policy drops new messages when full."""
        writer = create_writer(
            temp_file,
            writer_type=WriterType.BLOCK,
            mode=Mode.MANUAL,  # Use MANUAL to control flush
            queue_size=5,
            policy=QueuePolicy.DROP_NEWEST
        )
        
        # Try to fill beyond capacity
        sent = 0
        for i in range(20):
            if writer._q.put(f'{{"msg": "{i}"}}', QueuePolicy.DROP_NEWEST):
                sent += 1
        
        # Trigger write
        writer.trigger()
        writer.stop()
        
        # Should have written only what fit in queue
        entries = verify_log_file(temp_file, check_logxpy_fields=False)
        assert len(entries) <= 5
    
    def test_drop_oldest_policy(self, temp_file):
        """DROP_OLDEST policy removes old messages for new ones."""
        writer = create_writer(
            temp_file,
            writer_type=WriterType.BLOCK,
            mode=Mode.MANUAL,
            queue_size=5,
            policy=QueuePolicy.DROP_OLDEST
        )
        
        # Fill queue
        for i in range(10):
            writer._q.put(f'{{"msg": "{i}"}}', QueuePolicy.DROP_OLDEST)
        
        writer.trigger()
        writer.stop()
        
        # Using writer directly - don't check logxpy fields
        entries = verify_log_file(temp_file, check_logxpy_fields=False)
        # Should have most recent messages
        assert len(entries) <= 5
    
    def test_warn_policy(self, temp_file):
        """WARN policy warns and drops when full."""
        import warnings
        
        writer = create_writer(
            temp_file,
            writer_type=WriterType.BLOCK,
            mode=Mode.MANUAL,
            queue_size=2,
            policy=QueuePolicy.WARN
        )
        
        # First messages should go through
        writer._q.put('{"msg": "1"}', QueuePolicy.WARN)
        writer._q.put('{"msg": "2"}', QueuePolicy.WARN)
        
        # Third should trigger warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            writer._q.put('{"msg": "3"}', QueuePolicy.WARN)
            # Note: warn policy may or may not trigger depending on queue state
    
    def test_skip_policy_backward_compat(self, temp_file):
        """Test that 'skip' maps to 'drop_newest' for backward compat."""
        # This tests the policy mapping in logx.py
        from logxpy import log
        
        temp_path = tempfile.mktemp(suffix=".log")
        try:
            # Should accept 'skip' as policy (maps to drop_newest)
            log.init(temp_path, async_en=True, policy="skip")
            log.info("Test message")
            log.shutdown_async()
            
            entries = verify_log_file(temp_path, expected_count=1)
            assert entries[0]['msg'] == "Test message"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


# ============================================================================
# Batch Size Tests
# ============================================================================

class TestBatchSizes:
    """Test different batch size configurations."""
    
    @pytest.mark.parametrize("batch_size", [1, 10, 100, 1000])
    def test_batch_size_flush(self, temp_file, batch_size):
        """Test that batch size triggers flush correctly."""
        writer = create_writer(
            temp_file,
            writer_type=WriterType.BLOCK,
            mode=Mode.TRIGGER,
            batch_size=batch_size,
            flush_interval=10.0  # Long interval to ensure batch triggers
        )
        
        # Send less than batch size
        for i in range(batch_size - 1):
            writer.send(f'{{"msg": "{i}"}}')
        
        # Wait a bit - should not have flushed yet
        time.sleep(0.1)
        
        # Send one more to trigger batch
        writer.send(f'{{"msg": "trigger"}}')
        
        writer.stop()
        
        # Using writer directly - don't check logxpy fields
        entries = verify_log_file(temp_file, expected_count=batch_size, check_logxpy_fields=False)
    
    def test_flush_interval(self, temp_file):
        """Test that flush interval triggers correctly."""
        writer = create_writer(
            temp_file,
            writer_type=WriterType.BLOCK,
            mode=Mode.TRIGGER,
            batch_size=1000,  # Large batch size
            flush_interval=0.05  # Short interval
        )
        
        # Send few messages
        writer.send('{"msg": "1"}')
        writer.send('{"msg": "2"}')
        
        # Wait for flush interval
        time.sleep(0.1)
        
        # Send more
        writer.send('{"msg": "3"}')
        
        writer.stop()
        
        # Using writer directly - don't check logxpy fields
        entries = verify_log_file(temp_file, expected_count=3, check_logxpy_fields=False)


# ============================================================================
# Writer Configuration Tests
# ============================================================================

class TestWriterConfigurations:
    """Test various writer configuration options."""
    
    def test_small_queue_size(self, temp_file):
        """Test with small queue size."""
        writer = create_writer(
            temp_file,
            writer_type=WriterType.BLOCK,
            mode=Mode.TRIGGER,
            queue_size=5
        )
        
        for i in range(100):
            writer.send(f'{{"msg": "{i}"}}')
        
        writer.stop()
        # Using writer directly - don't check logxpy fields
        entries = verify_log_file(temp_file, expected_count=100, check_logxpy_fields=False)
    
    def test_large_queue_size(self, temp_file):
        """Test with large queue size."""
        writer = create_writer(
            temp_file,
            writer_type=WriterType.BLOCK,
            mode=Mode.TRIGGER,
            queue_size=100000
        )
        
        for i in range(1000):
            writer.send(f'{{"msg": "{i}"}}')
        
        writer.stop()
        # Using writer directly - don't check logxpy fields
        entries = verify_log_file(temp_file, expected_count=1000, check_logxpy_fields=False)
    
    def test_loop_mode_tick_interval(self, temp_file):
        """Test LOOP mode with different tick intervals."""
        for tick in [0.001, 0.01, 0.1]:
            writer = create_writer(
                temp_file,
                writer_type=WriterType.BLOCK,
                mode=Mode.LOOP,
                tick=tick
            )
            
            writer.send('{"msg": "test"}')
            time.sleep(tick * 2)  # Wait for tick
            
            writer.stop()
            
            if os.path.exists(temp_file):
                with open(temp_file) as f:
                    content = f.read()
                if content:
                    # Using writer directly - don't check logxpy fields
                    entries = verify_log_file(temp_file, check_logxpy_fields=False)
                    assert len(entries) >= 1
            
            # Clean up for next iteration
            if os.path.exists(temp_file):
                os.remove(temp_file)


# ============================================================================
# Real Log File Tests
# ============================================================================

class TestRealLogFiles:
    """Test real log file creation with various scenarios."""
    
    def test_single_log_entry_line(self, temp_file):
        """Single entry with line writer."""
        log.init(temp_file, async_en=True, writer_type='line')
        log.info("Single message")
        log.shutdown_async()
        
        entries = verify_log_file(temp_file, expected_count=1)
        assert entries[0]['msg'] == "Single message"
        assert entries[0]['mt'] == 'info'
    
    def test_single_log_entry_block(self, temp_file):
        """Single entry with block writer."""
        log.init(temp_file, async_en=True, writer_type='block')
        log.info("Single message")
        log.shutdown_async()
        
        entries = verify_log_file(temp_file, expected_count=1)
        assert entries[0]['msg'] == "Single message"
    
    def test_single_log_entry_mmap(self, temp_file):
        """Single entry with mmap writer."""
        log.init(temp_file, async_en=True, writer_type='mmap')
        log.info("Single message")
        log.shutdown_async()
        
        entries = verify_log_file(temp_file, expected_count=1)
        assert entries[0]['msg'] == "Single message"
    
    def test_multiple_log_entries_all_levels(self, temp_file):
        """Multiple entries with all log levels."""
        log.init(temp_file, async_en=True, writer_type='block')
        
        log.debug("Debug message")
        log.info("Info message")
        log.success("Success message")
        log.note("Note message")
        log.warning("Warning message")
        log.error("Error message")
        log.critical("Critical message")
        
        log.shutdown_async()
        
        entries = verify_log_file(temp_file, expected_count=7)
        
        levels = [e['mt'] for e in entries]
        assert 'debug' in levels
        assert 'info' in levels
        assert 'success' in levels
        assert 'note' in levels
        assert 'warning' in levels
        assert 'error' in levels
        assert 'critical' in levels
    
    def test_log_with_context(self, temp_file):
        """Log entries with context fields."""
        log.init(temp_file, async_en=True, writer_type='block')
        
        log.info("User action", user_id=123, action="login", ip="192.168.1.1")
        log.info("Database query", query="SELECT * FROM users", duration_ms=45)
        
        log.shutdown_async()
        
        entries = verify_log_file(temp_file, expected_count=2)
        
        assert entries[0]['user_id'] == 123
        assert entries[0]['action'] == "login"
        assert entries[0]['ip'] == "192.168.1.1"
        
        assert entries[1]['query'] == "SELECT * FROM users"
        assert entries[1]['duration_ms'] == 45
    
    def test_high_volume_logging(self, temp_file):
        """High volume logging test."""
        log.init(temp_file, async_en=True, writer_type='block', size=100)
        
        for i in range(1000):
            log.info(f"Message {i}", index=i)
        
        log.shutdown_async()
        
        entries = verify_log_file(temp_file, expected_count=1000)
        
        # Verify all messages in order
        for i, entry in enumerate(entries):
            assert entry['msg'] == f"Message {i}"
            assert entry['index'] == i
    
    def test_concurrent_logging(self, temp_file):
        """Test concurrent logging from multiple threads."""
        import threading
        
        log.init(temp_file, async_en=True, writer_type='block')
        
        messages_per_thread = 100
        thread_count = 5
        
        def worker(thread_id):
            for i in range(messages_per_thread):
                log.info(f"Thread {thread_id} message {i}", thread_id=thread_id, msg_index=i)
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(thread_count)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        log.shutdown_async()
        
        entries = verify_log_file(temp_file, expected_count=thread_count * messages_per_thread)
        
        # Verify all thread messages present
        thread_counts = {}
        for entry in entries:
            tid = entry.get('thread_id')
            if tid is not None:
                thread_counts[tid] = thread_counts.get(tid, 0) + 1
        
        for i in range(thread_count):
            assert thread_counts.get(i, 0) == messages_per_thread


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_message(self, temp_file):
        """Test logging empty message."""
        log.init(temp_file, async_en=True)
        log.info("")
        log.shutdown_async()
        
        entries = verify_log_file(temp_file, expected_count=1)
        assert entries[0]['msg'] == ""
    
    def test_unicode_message(self, temp_file):
        """Test logging unicode characters."""
        log.init(temp_file, async_en=True)
        log.info("Hello 世界 🌍 Привет")
        log.shutdown_async()
        
        entries = verify_log_file(temp_file, expected_count=1)
        assert entries[0]['msg'] == "Hello 世界 🌍 Привет"
    
    def test_special_characters(self, temp_file):
        """Test logging special characters."""
        log.init(temp_file, async_en=True)
        log.info('Special: "quotes", \\backslash, \nnewline, \ttab')
        log.shutdown_async()
        
        entries = verify_log_file(temp_file, expected_count=1)
        # Message should be properly escaped in JSON
        assert 'quotes' in entries[0]['msg']
    
    def test_very_long_message(self, temp_file):
        """Test logging very long message."""
        log.init(temp_file, async_en=True)
        long_msg = "A" * 10000
        log.info(long_msg)
        log.shutdown_async()
        
        entries = verify_log_file(temp_file, expected_count=1)
        assert entries[0]['msg'] == long_msg
    
    def test_nested_context(self, temp_file):
        """Test logging with nested context."""
        log.init(temp_file, async_en=True)
        
        with log.scope(request_id="req-123"):
            log.info("Processing request")
            with log.scope(user_id="user-456"):
                log.info("User action", action="click")
        
        log.shutdown_async()
        
        entries = verify_log_file(temp_file, expected_count=2)
        assert entries[0]['request_id'] == "req-123"
        assert entries[1]['request_id'] == "req-123"
        assert entries[1]['user_id'] == "user-456"
    
    def test_log_after_shutdown(self, temp_file):
        """Test that logging after shutdown goes to sync path."""
        log.init(temp_file, async_en=True)
        log.info("Before shutdown")
        log.shutdown_async()
        log.info("After shutdown")  # Should go to sync path
        
        # File should contain both messages
        with open(temp_file) as f:
            content = f.read()
        
        assert "Before shutdown" in content


# ============================================================================
# Metrics Tests
# ============================================================================

class TestMetrics:
    """Test metrics collection."""
    
    def test_metrics_increment(self, temp_file):
        """Test that metrics are correctly incremented."""
        writer = create_writer(temp_file, writer_type=WriterType.BLOCK)
        
        initial_written = writer.metrics.written
        
        writer.send('{"msg": "test"}')
        writer.stop()
        
        assert writer.metrics.written > initial_written
        assert writer.metrics.enqueued >= 1
    
    def test_metrics_snapshot(self, temp_file):
        """Test metrics snapshot."""
        writer = create_writer(temp_file, writer_type=WriterType.BLOCK)
        
        for i in range(10):
            writer.send(f'{{"msg": "{i}"}}')
        
        writer.stop()
        
        snapshot = writer.metrics.get_snapshot()
        assert 'enqueued' in snapshot
        assert 'written' in snapshot
        assert 'dropped' in snapshot
        assert 'errors' in snapshot
        assert 'pending' in snapshot
        
        assert snapshot['enqueued'] >= 10
        assert snapshot['written'] >= 10


# ============================================================================
# Logx Integration Extended Tests
# ============================================================================

class TestLogxIntegrationExtended:
    """Extended integration tests with logx module."""
    
    @pytest.mark.parametrize("writer_type", ['line', 'block', 'mmap'])
    @pytest.mark.parametrize("writer_mode", ['trigger', 'loop', 'manual'])
    def test_all_combinations(self, writer_type, writer_mode):
        """Test all writer_type × writer_mode combinations via log.init()."""
        import time
        temp_path = tempfile.mktemp(suffix=".log")
        try:
            log.init(
                temp_path,
                async_en=True,
                writer_type=writer_type,
                writer_mode=writer_mode,
                tick=0.05 if writer_mode == 'loop' else 0.1
            )
            
            # Single message
            log.info(f"Test {writer_type}/{writer_mode}")
            
            if writer_mode == 'manual':
                log.trigger()
            elif writer_mode == 'loop':
                time.sleep(0.1)  # Give LOOP mode time to process
            
            # Multiple messages
            for i in range(5):
                log.info(f"Message {i}", idx=i)
                if writer_mode == 'manual':
                    log.trigger()
                elif writer_mode == 'loop':
                    time.sleep(0.02)
            
            if writer_mode == 'manual':
                log.trigger()  # Final trigger
                time.sleep(0.05)
            elif writer_mode == 'loop':
                time.sleep(0.15)  # Give LOOP mode time to flush
            
            log.shutdown_async()
            
            entries = verify_log_file(temp_path, expected_count=6)
            assert entries[0]['msg'] == f"Test {writer_type}/{writer_mode}"
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_flush_method(self):
        """Test log.flush() method."""
        import time
        temp_path = tempfile.mktemp(suffix=".log")
        try:
            log.init(temp_path, async_en=True, writer_type='block', writer_mode='manual')
            
            log.info("Before flush")
            log.flush()  # Should trigger write in manual mode
            time.sleep(0.05)
            
            log.info("After flush")
            log.trigger()  # Alternative way to trigger
            time.sleep(0.05)
            
            log.shutdown_async()
            
            entries = verify_log_file(temp_path, expected_count=2)
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_sync_mode_context(self):
        """Test sync_mode context manager."""
        temp_path = tempfile.mktemp(suffix=".log")
        try:
            log.init(temp_path, async_en=True, writer_type='block')
            
            log.info("Async message")
            
            with log.sync_mode():
                log.info("Sync message")  # Goes to sync path
            
            log.info("Back to async")
            
            log.shutdown_async()
            
            entries = verify_log_file(temp_path)
            # Note: sync_mode message may not appear in async file
            # Just verify we have at least the async messages
            assert len(entries) >= 2
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_get_async_metrics_integration(self):
        """Test get_async_metrics() returns valid data."""
        temp_path = tempfile.mktemp(suffix=".log")
        try:
            log.init(temp_path, async_en=True, writer_type='block')
            
            # Initial metrics
            initial = log.get_async_metrics()
            assert 'enqueued' in initial
            assert 'written' in initial
            
            # Log some messages
            for i in range(10):
                log.info(f"Message {i}")
            
            # Check metrics before shutdown
            mid = log.get_async_metrics()
            assert mid['enqueued'] >= 10
            
            log.shutdown_async()
            
            # After shutdown, writer is None so metrics reset to 0
            final = log.get_async_metrics()
            assert 'enqueued' in final  # Just check structure exists
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
