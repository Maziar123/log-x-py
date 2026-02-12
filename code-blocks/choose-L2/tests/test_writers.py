"""Tests for writer implementations."""

import os
import time

import pytest

from writer import (
    BlockBufferedWriter,
    LineBufferedWriter,
    MemoryMappedWriter,
    Mode,
    Q,
    QueuePolicy,
    WriterType,
    create_writer,
)


class TestLineBufferedWriter:
    """Tests for LineBufferedWriter."""

    def test_basic_write(self, temp_file):
        """Basic write works."""
        q = Q()
        writer = LineBufferedWriter(q, temp_file, mode=Mode.TRIGGER, running=False)
        
        writer.send("line1")
        writer.send("line2")
        writer._write_batch(["line1", "line2"])
        writer.close()
        
        with open(temp_file) as f:
            content = f.read()
        
        assert "line1" in content
        assert "line2" in content

    def test_all_modes(self, temp_file):
        """Works with all modes."""
        for mode in [Mode.TRIGGER, Mode.LOOP, Mode.MANUAL]:
            q = Q()
            writer = LineBufferedWriter(q, temp_file, mode=mode, running=False)
            writer._write_batch(["test"])
            writer.close()
            
            with open(temp_file) as f:
                assert "test" in f.read()


class TestBlockBufferedWriter:
    """Tests for BlockBufferedWriter."""

    def test_basic_write(self, temp_file):
        """Basic write works."""
        q = Q()
        writer = BlockBufferedWriter(q, temp_file, mode=Mode.TRIGGER, running=False)
        
        writer._write_batch(["line1", "line2", "line3"])
        writer.close()
        
        with open(temp_file) as f:
            content = f.read()
        
        assert "line1" in content
        assert "line2" in content
        assert "line3" in content

    def test_large_batch(self, temp_file):
        """Large batch write works."""
        q = Q()
        writer = BlockBufferedWriter(q, temp_file, mode=Mode.TRIGGER, running=False)
        
        lines = [f"line{i}" for i in range(100)]
        writer._write_batch(lines)
        writer.close()
        
        with open(temp_file) as f:
            content = f.read()
        
        assert "line0" in content
        assert "line99" in content


class TestMemoryMappedWriter:
    """Tests for MemoryMappedWriter."""

    def test_basic_write(self, temp_file):
        """Basic write works."""
        q = Q()
        writer = MemoryMappedWriter(q, temp_file, mode=Mode.TRIGGER, running=False)
        
        writer._write_batch(["line1", "line2"])
        writer.close()  # This flushes and truncates
        
        with open(temp_file) as f:
            content = f.read()
        
        assert "line1" in content
        assert "line2" in content


class TestCreateWriter:
    """Tests for create_writer factory."""

    def test_creates_line_writer(self, temp_file):
        """Factory creates LineBufferedWriter."""
        writer = create_writer(
            temp_file,
            writer_type=WriterType.LINE,
            mode=Mode.TRIGGER,
        )
        assert isinstance(writer, LineBufferedWriter)
        writer.close()

    def test_creates_block_writer(self, temp_file):
        """Factory creates BlockBufferedWriter."""
        writer = create_writer(
            temp_file,
            writer_type=WriterType.BLOCK,
            mode=Mode.TRIGGER,
        )
        assert isinstance(writer, BlockBufferedWriter)
        writer.close()

    def test_creates_mmap_writer(self, temp_file):
        """Factory creates MemoryMappedWriter."""
        writer = create_writer(
            temp_file,
            writer_type=WriterType.MMAP,
            mode=Mode.TRIGGER,
        )
        assert isinstance(writer, MemoryMappedWriter)
        writer.close()

    def test_creates_with_trigger_mode(self, temp_file):
        """Factory creates writer with TRIGGER mode."""
        writer = create_writer(temp_file, mode=Mode.TRIGGER)
        assert writer._mode == Mode.TRIGGER
        writer.close()

    def test_creates_with_loop_mode(self, temp_file):
        """Factory creates writer with LOOP mode."""
        writer = create_writer(temp_file, mode=Mode.LOOP)
        assert writer._mode == Mode.LOOP
        writer.close()

    def test_creates_with_manual_mode(self, temp_file):
        """Factory creates writer with MANUAL mode."""
        writer = create_writer(temp_file, mode=Mode.MANUAL)
        assert writer._mode == Mode.MANUAL
        writer.close()


class TestWriterMetrics:
    """Tests for WriterMetrics."""

    def test_initial_values(self):
        """Metrics start at zero."""
        from writer import WriterMetrics
        
        m = WriterMetrics()
        assert m.enqueued == 0
        assert m.written == 0
        assert m.dropped == 0
        assert m.errors == 0
        assert m.pending == 0

    def test_record_enqueued(self):
        """record_enqueued increments counter."""
        from writer import WriterMetrics
        
        m = WriterMetrics()
        m.record_enqueued()
        m.record_enqueued()
        assert m.enqueued == 2

    def test_record_written(self):
        """record_written increments counter."""
        from writer import WriterMetrics
        
        m = WriterMetrics()
        m.record_written(5)
        assert m.written == 5

    def test_pending_calculation(self):
        """pending is calculated correctly."""
        from writer import WriterMetrics
        
        m = WriterMetrics()
        m.record_enqueued()
        m.record_enqueued()
        m.record_enqueued()
        m.record_written(1)
        
        assert m.pending == 2  # 3 - 1 - 0

    def test_get_snapshot(self):
        """get_snapshot returns correct dict."""
        from writer import WriterMetrics
        
        m = WriterMetrics()
        m.record_enqueued()
        m.record_written(1)
        
        snapshot = m.get_snapshot()
        assert snapshot["enqueued"] == 1
        assert snapshot["written"] == 1
        assert snapshot["pending"] == 0


class TestWriterModes:
    """Tests for writer mode loops."""

    def test_trigger_mode(self, temp_file):
        """TRIGGER mode processes messages."""
        q = Q()
        writer = BlockBufferedWriter(
            q, temp_file, mode=Mode.TRIGGER,
            batch_size=2, flush_interval=0.1
        )
        
        writer.send("line1")
        writer.send("line2")  # Should trigger batch flush
        
        time.sleep(0.2)  # Wait for flush
        writer.close()
        
        with open(temp_file) as f:
            content = f.read()
        
        assert "line1" in content
        assert "line2" in content

    def test_loop_mode(self, temp_file):
        """LOOP mode processes messages."""
        q = Q()
        writer = BlockBufferedWriter(
            q, temp_file, mode=Mode.LOOP,
            batch_size=10, flush_interval=0.05
        )
        
        writer.send("line1")
        writer.send("line2")
        
        time.sleep(0.15)  # Wait for timer flush
        writer.close()
        
        with open(temp_file) as f:
            content = f.read()
        
        assert "line1" in content
        assert "line2" in content
