"""Tests for base classes."""

import pytest

from writer.base import Mode, Q, QEmpty


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


class TestMode:
    """Tests for Mode enum."""

    def test_modes_exist(self):
        """All modes are defined."""
        assert Mode.TRIGGER
        assert Mode.LOOP
        assert Mode.MANUAL

    def test_mode_comparison(self):
        """Modes can be compared."""
        assert Mode.TRIGGER is not Mode.LOOP
        assert Mode.TRIGGER is Mode.TRIGGER
