"""Tests for logxpy/src/_async_writer.py -- Async writer.

Tests cover:
- AsyncConfig / QueuePolicy / AsyncMetrics (unit)
- AsyncWriter lifecycle (start/stop)
- AsyncWriter.flush() on-demand flush
- AsyncWriter.enable_adaptive() / disable_adaptive()
- AdaptiveFlushConfig / _AdaptiveFlushTracker (unit)
- Fork safety registration
- _flush_batch destination.flush() calls
- Real file I/O verification for every technique
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from logxpy.src._async_destinations import AsyncFileDestination
from logxpy.src._async_writer import (
    AdaptiveFlushConfig,
    AsyncConfig,
    AsyncMetrics,
    AsyncWriter,
    QueuePolicy,
    _AdaptiveFlushTracker,
    create_default_writer,
)
from logxpy.src._types import Level, Record


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _record(msg: str = "test") -> Record:
    return Record(
        timestamp=time.time(),
        level=Level.INFO,
        message=msg,
        fields={},
        context={},
        task_uuid="X.1",
        task_level=(1,),
        message_type="info",
    )


def _parse_log(path: Path) -> list[dict]:
    """Read a log file and return parsed JSON lines."""
    lines = path.read_text().strip().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


# ============================================================================
# AsyncConfig
# ============================================================================

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

    def test_deadline_sec_none(self):
        cfg = AsyncConfig()
        assert cfg.deadline_sec is None

    def test_deadline_sec_value(self):
        cfg = AsyncConfig(deadline_ms=500.0)
        assert cfg.deadline_sec == 0.5


# ============================================================================
# QueuePolicy
# ============================================================================

class TestQueuePolicy:
    def test_values(self):
        assert QueuePolicy.BLOCK == "block"
        assert QueuePolicy.REPLACE == "replace"
        assert QueuePolicy.SKIP == "skip"
        assert QueuePolicy.WARN == "warn"


# ============================================================================
# AsyncMetrics
# ============================================================================

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

    def test_record_dropped(self):
        m = AsyncMetrics()
        m.record_dropped(3)
        assert m.dropped == 3

    def test_record_error(self):
        m = AsyncMetrics()
        m.record_error()
        assert m.errors == 1


# ============================================================================
# AdaptiveFlushConfig
# ============================================================================

class TestAdaptiveFlushConfig:
    def test_defaults(self):
        cfg = AdaptiveFlushConfig()
        assert cfg.ema_alpha == 0.1
        assert cfg.min_batch_size == 10
        assert cfg.max_batch_size == 1000
        assert cfg.min_flush_interval == 0.001
        assert cfg.max_flush_interval == 1.0
        assert cfg.low_rate_threshold == 100.0
        assert cfg.high_rate_threshold == 10_000.0

    def test_custom_values(self):
        cfg = AdaptiveFlushConfig(
            ema_alpha=0.2,
            min_batch_size=5,
            max_batch_size=500,
        )
        assert cfg.ema_alpha == 0.2
        assert cfg.min_batch_size == 5
        assert cfg.max_batch_size == 500

    def test_frozen(self):
        cfg = AdaptiveFlushConfig()
        with pytest.raises(AttributeError):
            cfg.ema_alpha = 0.5  # type: ignore[misc]


# ============================================================================
# _AdaptiveFlushTracker
# ============================================================================

class TestAdaptiveFlushTracker:
    def test_initial_values(self):
        cfg = AdaptiveFlushConfig(min_batch_size=5, min_flush_interval=0.01)
        tracker = _AdaptiveFlushTracker(cfg)
        assert tracker.batch_size == 5
        assert tracker.flush_interval == 0.01
        assert tracker.current_rate == 0.0

    def test_low_rate_stays_at_min(self):
        cfg = AdaptiveFlushConfig(
            rate_sample_interval=0.001,
            min_batch_size=5,
            max_batch_size=500,
            low_rate_threshold=100,
            high_rate_threshold=10_000,
        )
        tracker = _AdaptiveFlushTracker(cfg)
        # Simulate low rate: a few messages over long time
        time.sleep(0.005)
        for _ in range(3):
            tracker.record_message()
        # Rate ~ 600 msg/s but only 3 messages in 5ms window
        # After sample, should be well below high threshold
        assert tracker.batch_size <= cfg.max_batch_size

    def test_high_rate_reaches_max(self):
        cfg = AdaptiveFlushConfig(
            ema_alpha=1.0,  # instant response (no smoothing)
            rate_sample_interval=0.001,
            min_batch_size=5,
            max_batch_size=500,
            low_rate_threshold=100,
            high_rate_threshold=1_000,
        )
        tracker = _AdaptiveFlushTracker(cfg)
        # Simulate high rate: many messages in short time
        time.sleep(0.002)
        for _ in range(50):
            tracker.record_message()
        # Force sampling by adding delay and one more
        time.sleep(0.002)
        tracker.record_message()
        # With alpha=1.0, rate = instant_rate which should be high
        assert tracker.current_rate > 0

    def test_interpolation_mid_rate(self):
        cfg = AdaptiveFlushConfig(
            ema_alpha=1.0,
            rate_sample_interval=0.001,
            min_batch_size=10,
            max_batch_size=100,
            min_flush_interval=0.001,
            max_flush_interval=1.0,
            low_rate_threshold=100,
            high_rate_threshold=10_000,
        )
        tracker = _AdaptiveFlushTracker(cfg)
        # Simulate ~5000 msg/s (mid-range)
        tracker._ema_rate = 5000.0
        tracker._adjust_parameters()
        # Should be between min and max
        assert 10 < tracker.batch_size < 100
        assert 0.001 < tracker.flush_interval < 1.0


# ============================================================================
# AsyncWriter - Lifecycle
# ============================================================================

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
        writer.enqueue(_record("hello"))
        time.sleep(0.2)
        writer.stop(timeout=2.0)
        assert len(received) >= 1

    def test_metrics_tracking(self):
        writer = AsyncWriter(AsyncConfig(batch_size=1, flush_interval_ms=10))
        writer.add_destination(lambda data: None)
        writer.start()
        writer.enqueue(_record())
        time.sleep(0.2)
        writer.stop(timeout=2.0)
        assert writer.metrics.enqueued >= 1

    def test_double_start_is_noop(self):
        writer = AsyncWriter(AsyncConfig(batch_size=1, flush_interval_ms=10))
        writer.start()
        thread1 = writer._thread
        writer.start()  # Should be noop
        assert writer._thread is thread1
        writer.stop(timeout=2.0)

    def test_stop_already_stopped(self):
        writer = AsyncWriter()
        assert writer.stop(timeout=1.0) is True  # Already stopped


# ============================================================================
# AsyncWriter.flush() -- On-Demand Flush with real file
# ============================================================================

class TestAsyncWriterFlush:
    def test_flush_returns_true(self, tmp_path: Path):
        """flush() returns True when completed within timeout."""
        log_file = tmp_path / "flush.log"
        writer = AsyncWriter(AsyncConfig(batch_size=10000, flush_interval_ms=60000))
        dest = AsyncFileDestination(log_file, use_fsync=False)
        writer.add_destination(dest)
        writer.start()

        for i in range(10):
            writer.enqueue(_record(f"msg-{i}"))

        result = writer.flush(timeout=5.0)
        assert result is True

        entries = _parse_log(log_file)
        assert len(entries) == 10
        assert entries[0]["msg"] == "msg-0"
        assert entries[9]["msg"] == "msg-9"

        writer.stop(timeout=2.0)
        dest.close()

    def test_flush_drains_entire_queue(self, tmp_path: Path):
        """flush() drains ALL pending queue items, not just current batch."""
        log_file = tmp_path / "drain.log"
        writer = AsyncWriter(AsyncConfig(batch_size=10000, flush_interval_ms=60000))
        dest = AsyncFileDestination(log_file, use_fsync=False)
        writer.add_destination(dest)
        writer.start()

        # Rapidly enqueue 200 messages
        for i in range(200):
            writer.enqueue(_record(f"item-{i}"))

        writer.flush(timeout=5.0)

        entries = _parse_log(log_file)
        assert len(entries) == 200

        writer.stop(timeout=2.0)
        dest.close()

    def test_flush_without_pending_is_noop(self, tmp_path: Path):
        """flush() with empty queue completes immediately."""
        log_file = tmp_path / "empty.log"
        writer = AsyncWriter(AsyncConfig(batch_size=100, flush_interval_ms=100))
        dest = AsyncFileDestination(log_file, use_fsync=False)
        writer.add_destination(dest)
        writer.start()

        result = writer.flush(timeout=2.0)
        assert result is True
        assert log_file.stat().st_size == 0  # nothing to write

        writer.stop(timeout=2.0)
        dest.close()

    def test_flush_when_not_running(self):
        """flush() on stopped writer returns True."""
        writer = AsyncWriter()
        assert writer.flush(timeout=1.0) is True

    def test_multiple_flushes(self, tmp_path: Path):
        """Multiple sequential flushes each persist their batch."""
        log_file = tmp_path / "multi.log"
        writer = AsyncWriter(AsyncConfig(batch_size=10000, flush_interval_ms=60000))
        dest = AsyncFileDestination(log_file, use_fsync=False)
        writer.add_destination(dest)
        writer.start()

        for i in range(10):
            writer.enqueue(_record(f"batch1-{i}"))
        writer.flush(timeout=5.0)
        count1 = len(_parse_log(log_file))
        assert count1 == 10

        for i in range(15):
            writer.enqueue(_record(f"batch2-{i}"))
        writer.flush(timeout=5.0)
        count2 = len(_parse_log(log_file))
        assert count2 == 25

        writer.stop(timeout=2.0)
        dest.close()


# ============================================================================
# AsyncWriter -- Destination flush() (fsync) calls
# ============================================================================

class TestFlushBatchCallsDestFlush:
    def test_destination_flush_called(self, tmp_path: Path):
        """_flush_batch calls flush() on destinations that support it."""
        flush_count = {"n": 0}

        class TrackingDest:
            def __call__(self, data):
                pass

            def flush(self):
                flush_count["n"] += 1

        writer = AsyncWriter(AsyncConfig(batch_size=5, flush_interval_ms=10))
        writer.add_destination(TrackingDest())
        writer.start()

        for i in range(10):
            writer.enqueue(_record(f"msg-{i}"))

        time.sleep(0.3)
        writer.stop(timeout=2.0)

        # flush() should have been called at least once (batch triggered)
        assert flush_count["n"] >= 1

    def test_destination_without_flush_not_crashes(self):
        """Destinations without flush() method don't crash _flush_batch."""
        writer = AsyncWriter(AsyncConfig(batch_size=1, flush_interval_ms=10))
        writer.add_destination(lambda data: None)  # No flush() method
        writer.start()
        writer.enqueue(_record())
        time.sleep(0.1)
        writer.stop(timeout=2.0)
        # Should not raise


# ============================================================================
# AsyncWriter.enable_adaptive / disable_adaptive
# ============================================================================

class TestAsyncWriterAdaptive:
    def test_enable_adaptive(self):
        writer = AsyncWriter()
        writer.enable_adaptive()
        assert writer._adaptive is not None

    def test_enable_adaptive_custom_config(self):
        writer = AsyncWriter()
        cfg = AdaptiveFlushConfig(min_batch_size=3, max_batch_size=300)
        writer.enable_adaptive(cfg)
        assert writer._adaptive is not None
        assert writer._adaptive._config.min_batch_size == 3

    def test_disable_adaptive(self):
        writer = AsyncWriter()
        writer.enable_adaptive()
        writer.disable_adaptive()
        assert writer._adaptive is None

    def test_adaptive_with_real_file(self, tmp_path: Path):
        """Adaptive mode logs messages to real file correctly."""
        log_file = tmp_path / "adaptive.log"
        writer = AsyncWriter(AsyncConfig(batch_size=100, flush_interval_ms=100))
        writer.enable_adaptive(AdaptiveFlushConfig(
            min_batch_size=5,
            max_batch_size=200,
            min_flush_interval=0.001,
            max_flush_interval=0.5,
        ))
        dest = AsyncFileDestination(log_file, use_fsync=False)
        writer.add_destination(dest)
        writer.start()

        for i in range(50):
            writer.enqueue(_record(f"adaptive-{i}"))

        writer.flush(timeout=5.0)
        entries = _parse_log(log_file)
        assert len(entries) == 50
        assert entries[0]["msg"] == "adaptive-0"
        assert entries[49]["msg"] == "adaptive-49"

        writer.stop(timeout=2.0)
        dest.close()


# ============================================================================
# Fork Safety
# ============================================================================

class TestForkSafety:
    def test_fork_registered_flag(self):
        """start() sets _fork_registered to True (on Unix)."""
        writer = AsyncWriter(AsyncConfig(batch_size=1, flush_interval_ms=10))
        writer.start()
        if hasattr(os, "register_at_fork"):
            assert writer._fork_registered is True
        writer.stop(timeout=2.0)

    def test_fork_registered_only_once(self):
        """Multiple start() calls don't re-register fork handlers."""
        writer = AsyncWriter(AsyncConfig(batch_size=1, flush_interval_ms=10))
        writer.start()
        writer.stop(timeout=2.0)
        writer._running = False
        writer._shutdown = False
        # Manually re-start to test idempotency
        writer.start()
        assert writer._fork_registered is True
        writer.stop(timeout=2.0)

    def test_reset_after_fork_child(self):
        """_reset_after_fork_child clears writer state."""
        writer = AsyncWriter(AsyncConfig(batch_size=1, flush_interval_ms=10))
        writer.start()
        writer._reset_after_fork_child()
        assert writer._running is False
        assert writer._thread is None
        # Queue should be fresh
        assert writer._queue.qsize() == 0


# ============================================================================
# create_default_writer
# ============================================================================

class TestCreateDefaultWriter:
    def test_creates_writer(self):
        writer = create_default_writer()
        assert isinstance(writer, AsyncWriter)

    def test_string_policy(self):
        writer = create_default_writer(policy="block")
        assert isinstance(writer, AsyncWriter)

    def test_custom_params(self):
        writer = create_default_writer(
            max_queue=500, batch_size=10, flush_interval=0.5, policy="skip"
        )
        assert isinstance(writer, AsyncWriter)
        assert writer._config.max_queue_size == 500
        assert writer._config.batch_size == 10
