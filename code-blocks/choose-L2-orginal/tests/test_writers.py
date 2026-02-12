"""Tests for writer implementations."""

import os

import pytest

from writer import FileWriter, Mode, Q
from writer.sync import (
    BlockBufferedWriter,
    LineBufferedWriter,
    MemoryMappedWriter,
)


class TestLineBufferedWriter:
    """Tests for LineBufferedWriter."""

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


class TestBlockBufferedWriter:
    """Tests for BlockBufferedWriter."""

    def test_large_batch(self, temp_file, queue):
        """Large batch write works."""
        writer = BlockBufferedWriter(queue, temp_file, Mode.TRIGGER)
        
        for i in range(1000):
            writer.send(f"line {i}")
        
        queue.stop()
        writer.join()
        
        assert writer.lines_written == 1000


class TestMemoryMappedWriter:
    """Tests for MemoryMappedWriter."""

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


class TestFileWriter:
    """Tests for default FileWriter (BlockBuffered)."""

    def test_default_is_block_buffered(self, temp_file, queue):
        """Default FileWriter is BlockBuffered."""
        writer = FileWriter(queue, temp_file, Mode.TRIGGER)
        assert isinstance(writer, BlockBufferedWriter)

    def test_context_manager(self, temp_file, queue):
        """Context manager works."""
        with FileWriter(queue, temp_file, Mode.TRIGGER) as writer:
            writer.send("line 1")
            writer.send("line 2")
        
        queue.stop()
        
        with open(temp_file) as f:
            lines = f.read().strip().split("\n")
        assert len(lines) == 2
