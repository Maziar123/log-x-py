"""Tests for logxpy/src/_writer.py -- Choose-L2 based writer.

Tests cover:
- WriterType / Mode / QueuePolicy enums
- WriterMetrics (unit)
- Q queue operations
- BaseFileWriterThread lifecycle (start/stop)
- LineBufferedWriter / BlockBufferedWriter / MemoryMappedWriter
- Integration with log.init() writer_type and writer_mode params
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_file():
    """Provide temporary file path."""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def queue():
    """Provide fresh Q instance."""
    return Q()


# ============================================================================
# WriterType / Mode / QueuePolicy
# ============================================================================

class TestWriterType:
    def test_values(self):
        assert WriterType.LINE == "line"
        assert WriterType.BLOCK == "block"
        assert WriterType.MMAP == "mmap"


class TestMode:
    def test_values(self):
        assert Mode.TRIGGER == "trigger"
        assert Mode.LOOP == "loop"
        assert Mode.MANUAL == "manual"


class TestQueuePolicy:
    def test_values(self):
        assert QueuePolicy.BLOCK == "block"
        assert QueuePolicy.DROP_OLDEST == "drop_oldest"
        assert QueuePolicy.DROP_NEWEST == "drop_newest"
        assert QueuePolicy.WARN == "warn"


# ============================================================================
# Q (Queue)
# ============================================================================

class TestQ:
    def test_put_get(self):
        """Basic put/get works."""
        q = Q()
        q.put("test")
        assert q.get(timeout=0.1) == "test"

    def test_get_returns_none_on_stop(self):
        """get() returns None after stop()."""
        q = Q()
        q.put("test")
        q.stop()
        
        assert q.get() == "test"
        assert q.get() is None

    def test_drain(self):
        """drain() returns all items."""
        q = Q()
        for i in range(5):
            q.put(f"item{i}")
        
        items = q.drain()
        assert items == ["item0", "item1", "item2", "item3", "item4"]
        assert not q.has_data()

    def test_drain_stops_at_sentinel(self):
        """drain() stops at stop sentinel."""
        q = Q()
        q.put("before")
        q.stop()
        q.put("after")  # Should not be returned
        
        items = q.drain()
        assert items == ["before"]

    def test_empty_raises_qempty(self):
        """get() raises QEmpty on timeout."""
        q = Q()
        with pytest.raises(QEmpty):
            q.get(timeout=0.001)

    def test_qsize(self):
        """qsize() returns approximate size."""
        q = Q()
        assert q.qsize() == 0
        q.put("test")
        assert q.qsize() == 1


# ============================================================================
# WriterMetrics
# ============================================================================

class TestWriterMetrics:
    def test_initial_values(self):
        m = WriterMetrics()
        assert m.enqueued == 0
        assert m.written == 0
        assert m.dropped == 0
        assert m.errors == 0
        assert m.pending == 0

    def test_record_enqueued(self):
        m = WriterMetrics()
        m.record_enqueued()
        assert m.enqueued == 1
        assert m.pending == 1

    def test_record_written(self):
        m = WriterMetrics()
        m.record_enqueued()
        m.record_written()
        assert m.written == 1
        assert m.pending == 0

    def test_record_dropped(self):
        m = WriterMetrics()
        m.record_dropped()
        assert m.dropped == 1

    def test_record_error(self):
        m = WriterMetrics()
        m.record_error()
        assert m.errors == 1

    def test_get_snapshot(self):
        m = WriterMetrics()
        m.record_enqueued()
        m.record_written()
        snapshot = m.get_snapshot()
        assert snapshot == {
            "enqueued": 1,
            "written": 1,
            "dropped": 0,
            "errors": 0,
            "pending": 0,
        }


# ============================================================================
# LineBufferedWriter
# ============================================================================

class TestLineBufferedWriter:
    def test_basic_write(self, temp_file, queue):
        """Basic write works."""
        writer = LineBufferedWriter(queue, temp_file, Mode.TRIGGER)
        
        writer.send("line 1")
        writer.send("line 2")
        
        queue.stop()
        writer.join()
        
        assert writer.lines_written == 2
        
        with open(temp_file) as f:
            lines = f.read().strip().split("\n")
        assert lines == ["line 1", "line 2"]

    def test_all_modes(self, temp_file):
        """All modes work."""
        for mode in [Mode.TRIGGER, Mode.LOOP, Mode.MANUAL]:
            q = Q()
            
            if mode is Mode.LOOP:
                writer = LineBufferedWriter(q, temp_file, mode, tick=0.01)
            else:
                writer = LineBufferedWriter(q, temp_file, mode)
            
            for i in range(10):
                writer.send(f"line {i}")
                if mode is Mode.MANUAL:
                    writer.trigger()
            
            if mode is Mode.MANUAL:
                writer.trigger()
            
            q.stop()
            writer.join(timeout=2.0)
            
            assert writer.lines_written == 10, f"Mode {mode.name} failed"
            
            # Clean up file
            if os.path.exists(temp_file):
                os.remove(temp_file)


# ============================================================================
# BlockBufferedWriter
# ============================================================================

class TestBlockBufferedWriter:
    def test_large_batch(self, temp_file, queue):
        """Large batch write works."""
        writer = BlockBufferedWriter(queue, temp_file, Mode.TRIGGER)
        
        for i in range(1000):
            writer.send(f"line {i}")
        
        queue.stop()
        writer.join()
        
        assert writer.lines_written == 1000


# ============================================================================
# MemoryMappedWriter
# ============================================================================

class TestMemoryMappedWriter:
    def test_mmap_write(self, temp_file, queue):
        """Memory-mapped write works."""
        writer = MemoryMappedWriter(queue, temp_file, Mode.TRIGGER)
        
        for i in range(100):
            writer.send(f"line {i}")
        
        queue.stop()
        writer.join()
        writer.close()  # Truncates the mmap file
        
        assert writer.lines_written == 100
        
        with open(temp_file) as f:
            lines = f.read().strip().split("\n")
        assert len(lines) == 100


# ============================================================================
# create_writer factory
# ============================================================================

class TestCreateWriter:
    def test_creates_line_writer(self, temp_file):
        writer = create_writer(temp_file, WriterType.LINE)
        assert isinstance(writer, LineBufferedWriter)
        writer.close()

    def test_creates_block_writer(self, temp_file):
        writer = create_writer(temp_file, WriterType.BLOCK)
        assert isinstance(writer, BlockBufferedWriter)
        writer.close()

    def test_creates_mmap_writer(self, temp_file):
        writer = create_writer(temp_file, WriterType.MMAP)
        assert isinstance(writer, MemoryMappedWriter)
        writer.close()

    def test_creates_with_trigger_mode(self, temp_file):
        writer = create_writer(temp_file, WriterType.BLOCK, Mode.TRIGGER)
        assert writer._mode == Mode.TRIGGER
        writer.close()

    def test_creates_with_loop_mode(self, temp_file):
        writer = create_writer(temp_file, WriterType.BLOCK, Mode.LOOP)
        assert writer._mode == Mode.LOOP
        writer.close()

    def test_creates_with_manual_mode(self, temp_file):
        writer = create_writer(temp_file, WriterType.BLOCK, Mode.MANUAL)
        assert writer._mode == Mode.MANUAL
        writer.close()


# ============================================================================
# Integration with logx.py
# ============================================================================

class TestLogxIntegration:
    def test_init_with_block_writer(self):
        """log.init() works with block writer."""
        from logxpy import log, WriterType, Mode
        
        temp_path = tempfile.mktemp(suffix=".log")
        try:
            log.init(
                temp_path,
                async_en=True,
                writer_type="block",
                writer_mode="trigger",
            )
            log.info("Test message", key="value")
            log.shutdown_async()
            
            with open(temp_path) as f:
                content = f.read()
                assert "Test message" in content
                assert "key" in content
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_init_with_line_writer(self):
        """log.init() works with line writer."""
        from logxpy import log, WriterType, Mode
        
        temp_path = tempfile.mktemp(suffix=".log")
        try:
            log.init(
                temp_path,
                async_en=True,
                writer_type="line",
                writer_mode="trigger",
            )
            log.info("Test message", key="value")
            log.shutdown_async()
            
            with open(temp_path) as f:
                content = f.read()
                assert "Test message" in content
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_init_with_mmap_writer(self):
        """log.init() works with mmap writer."""
        from logxpy import log, WriterType, Mode
        
        temp_path = tempfile.mktemp(suffix=".log")
        try:
            log.init(
                temp_path,
                async_en=True,
                writer_type="mmap",
                writer_mode="trigger",
            )
            log.info("Test message", key="value")
            log.shutdown_async()
            
            with open(temp_path) as f:
                content = f.read()
                assert "Test message" in content
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_get_async_metrics(self):
        """log.get_async_metrics() returns metrics."""
        from logxpy import log
        
        temp_path = tempfile.mktemp(suffix=".log")
        try:
            log.init(temp_path, async_en=True)
            log.info("Test")
            log.shutdown_async()
            
            metrics = log.get_async_metrics()
            assert "enqueued" in metrics
            assert "written" in metrics
            assert metrics["written"] >= 0
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
