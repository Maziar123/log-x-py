"""Tests for logxpy/src/_async_writer.py -- Async writer."""
from __future__ import annotations
import time
from logxpy.src._async_writer import (
    AsyncConfig, QueuePolicy, AsyncMetrics, AsyncWriter, create_default_writer,
)
from logxpy.src._types import Level, Record

class TestAsyncConfig:
    def test_defaults(self):
        cfg = AsyncConfig()
        assert cfg.max_queue_size == 10_000
        assert cfg.batch_size == 100
        assert cfg.queue_policy == QueuePolicy.BLOCK

    def test_custom_config(self):
        cfg = AsyncConfig(max_queue_size=500, batch_size=10)
        assert cfg.max_queue_size == 500
        assert cfg.batch_size == 10

    def test_flush_interval_sec(self):
        cfg = AsyncConfig(flush_interval_ms=200.0)
        assert cfg.flush_interval_sec == 0.2

class TestQueuePolicy:
    def test_values(self):
        assert QueuePolicy.BLOCK == "block"
        assert QueuePolicy.DROP_OLDEST == "drop_oldest"
        assert QueuePolicy.DROP_NEWEST == "drop_newest"
        assert QueuePolicy.WARN == "warn"

class TestAsyncMetrics:
    def test_initial_values(self):
        m = AsyncMetrics()
        assert m.enqueued == 0
        assert m.written == 0
        assert m.dropped == 0
        assert m.errors == 0

    def test_record_enqueued(self):
        m = AsyncMetrics()
        m.record_enqueued()
        assert m.enqueued == 1

    def test_record_written(self):
        m = AsyncMetrics()
        m.record_written(5)
        assert m.written == 5

    def test_pending(self):
        m = AsyncMetrics()
        m.record_enqueued()
        m.record_enqueued()
        m.record_written(1)
        assert m.pending == 1

    def test_snapshot(self):
        m = AsyncMetrics()
        m.record_enqueued()
        snap = m.get_snapshot()
        assert snap["enqueued"] == 1
        assert "pending" in snap

class TestAsyncWriter:
    def test_start_stop(self):
        writer = AsyncWriter(AsyncConfig(batch_size=1, flush_interval_ms=10))
        writer.start()
        assert writer.is_running
        stopped = writer.stop(timeout=2.0)
        assert stopped
        assert not writer.is_running

    def test_write_message(self):
        received = []
        writer = AsyncWriter(AsyncConfig(batch_size=1, flush_interval_ms=10))
        writer.add_destination(lambda data: received.append(data))
        writer.start()
        record = Record(
            timestamp=1.0, level=Level.INFO, message="test",
            fields={}, context={}, task_uuid="X.1", task_level=(1,),
            message_type="info",
        )
        writer.enqueue(record)
        time.sleep(0.2)  # Give writer thread time
        writer.stop(timeout=2.0)
        assert len(received) >= 1

    def test_metrics_tracking(self):
        writer = AsyncWriter(AsyncConfig(batch_size=1, flush_interval_ms=10))
        writer.add_destination(lambda data: None)
        writer.start()
        record = Record(
            timestamp=1.0, level=Level.INFO, message="test",
            fields={}, context={}, task_uuid="X.1", task_level=(1,),
            message_type="info",
        )
        writer.enqueue(record)
        time.sleep(0.2)
        writer.stop(timeout=2.0)
        assert writer.metrics.enqueued >= 1

class TestCreateDefaultWriter:
    def test_creates_writer(self):
        writer = create_default_writer()
        assert isinstance(writer, AsyncWriter)

    def test_string_policy(self):
        writer = create_default_writer(policy="block")
        assert isinstance(writer, AsyncWriter)
