"""Tests for base classes."""

import pytest

from writer.base import Mode, Q, QEmpty, QueuePolicy, WriterType


class TestQ:
    """Tests for Q class."""

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
        q.put("item1")
        assert q.qsize() == 1
        q.put("item2")
        assert q.qsize() == 2
        q.get(timeout=0.1)
        assert q.qsize() == 1

    def test_maxsize_drop_newest(self):
        """DROP_NEWEST policy drops new messages when full."""
        q = Q(maxsize=2)
        assert q.put("item1", policy=QueuePolicy.DROP_NEWEST) is True
        assert q.put("item2", policy=QueuePolicy.DROP_NEWEST) is True
        assert q.put("item3", policy=QueuePolicy.DROP_NEWEST) is False  # Dropped
        assert q.qsize() == 2

    def test_maxsize_drop_oldest(self):
        """DROP_OLDEST policy removes oldest when full."""
        q = Q(maxsize=2)
        q.put("item1", policy=QueuePolicy.DROP_OLDEST)
        q.put("item2", policy=QueuePolicy.DROP_OLDEST)
        q.put("item3", policy=QueuePolicy.DROP_OLDEST)  # Drops item1
        
        assert q.qsize() == 2
        items = q.drain()
        assert items == ["item2", "item3"]


class TestMode:
    """Tests for Mode enum."""

    def test_modes_exist(self):
        """All modes are defined."""
        assert Mode.TRIGGER
        assert Mode.LOOP
        assert Mode.MANUAL

    def test_mode_values(self):
        """Modes have correct string values."""
        assert Mode.TRIGGER.value == "trigger"
        assert Mode.LOOP.value == "loop"
        assert Mode.MANUAL.value == "manual"


class TestWriterType:
    """Tests for WriterType enum."""

    def test_types_exist(self):
        """All writer types are defined."""
        assert WriterType.LINE
        assert WriterType.BLOCK
        assert WriterType.MMAP

    def test_type_values(self):
        """Writer types have correct string values."""
        assert WriterType.LINE.value == "line"
        assert WriterType.BLOCK.value == "block"
        assert WriterType.MMAP.value == "mmap"


class TestQueuePolicy:
    """Tests for QueuePolicy enum."""

    def test_policies_exist(self):
        """All policies are defined."""
        assert QueuePolicy.BLOCK
        assert QueuePolicy.DROP_OLDEST
        assert QueuePolicy.DROP_NEWEST
        assert QueuePolicy.WARN

    def test_policy_values(self):
        """Policies have correct string values."""
        assert QueuePolicy.BLOCK.value == "block"
        assert QueuePolicy.DROP_OLDEST.value == "drop_oldest"
        assert QueuePolicy.DROP_NEWEST.value == "drop_newest"
        assert QueuePolicy.WARN.value == "warn"
