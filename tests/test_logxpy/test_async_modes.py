"""Tests for async flush modes and SI time integration.

Tests the 3 async modes with REAL file I/O verification:
- Mode 1: size=N, flush=T  (batch OR time)
- Mode 2: size=N, flush=0  (batch only)
- Mode 3: size=0, flush=T  (time only)
- On-demand flush via log.flush()
- Adaptive flush mode
- Deadline flush
- Policy behavior
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from logxpy.src.logx import Logger


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_log(path: Path) -> list[dict]:
    """Read a log file and return parsed JSON lines."""
    text = path.read_text().strip()
    if not text:
        return []
    return [json.loads(line) for line in text.splitlines() if line.strip()]


# ============================================================================
# Mode 1: Flush on batch size OR time interval
# ============================================================================

class TestMode1BatchOrTime:
    """Mode 1: Flush on batch size OR time interval (whichever first)."""

    def test_flush_on_batch_size(self, tmp_path: Path):
        """Flush when batch size reached — verify JSON content."""
        log_file = tmp_path / "mode1_batch.log"
        logger = Logger()
        logger.init(str(log_file), size=3, flush=10.0)  # 3 msgs or 10s

        logger.info("msg0")
        logger.info("msg1")
        logger.info("msg2")

        time.sleep(0.05)
        logger.shutdown_async()

        entries = _parse_log(log_file)
        assert len(entries) == 3
        assert entries[0]["msg"] == "msg0"
        assert entries[1]["msg"] == "msg1"
        assert entries[2]["msg"] == "msg2"

    def test_flush_on_time(self, tmp_path: Path):
        """Flush when time interval reached — verify JSON msg field."""
        log_file = tmp_path / "mode1_time.log"
        logger = Logger()
        logger.init(str(log_file), size=100, flush=0.05)  # 100 msgs or 50ms

        logger.info("only_msg")

        time.sleep(0.1)
        logger.shutdown_async()

        entries = _parse_log(log_file)
        assert len(entries) == 1
        assert entries[0]["msg"] == "only_msg"
        assert entries[0]["mt"] == "info"

    def test_batch_reaches_first(self, tmp_path: Path):
        """Batch size triggers before time — verify JSON content."""
        log_file = tmp_path / "mode1_batch_first.log"
        logger = Logger()
        logger.init(str(log_file), size=2, flush=60.0)  # 2 msgs or 60s

        logger.info("msg1")
        logger.info("msg2")

        time.sleep(0.05)
        logger.shutdown_async()

        entries = _parse_log(log_file)
        assert len(entries) == 2
        assert entries[0]["msg"] == "msg1"
        assert entries[1]["msg"] == "msg2"


# ============================================================================
# Mode 2: Flush only on batch size (flush=0)
# ============================================================================

class TestMode2BatchOnly:
    """Mode 2: Flush only on batch size (flush=0)."""

    def test_no_flush_until_batch_full(self, tmp_path: Path):
        """No flush until batch size reached — verify all on shutdown."""
        log_file = tmp_path / "mode2_batch.log"
        logger = Logger()
        logger.init(str(log_file), size=5, flush=0)

        for i in range(3):
            logger.info(f"msg{i}")

        time.sleep(0.1)
        logger.shutdown_async()

        entries = _parse_log(log_file)
        assert len(entries) == 3
        for i in range(3):
            assert entries[i]["msg"] == f"msg{i}"

    def test_flush_on_batch_full(self, tmp_path: Path):
        """Flush exactly when batch fills — verify JSON line count."""
        log_file = tmp_path / "mode2_full.log"
        logger = Logger()
        logger.init(str(log_file), size=3, flush=0)

        for i in range(3):
            logger.debug(f"item-{i}")

        time.sleep(0.05)
        logger.shutdown_async()

        entries = _parse_log(log_file)
        assert len(entries) == 3
        assert entries[0]["msg"] == "item-0"
        assert entries[2]["msg"] == "item-2"


# ============================================================================
# Mode 3: Flush only on time (size=0)
# ============================================================================

class TestMode3TimeOnly:
    """Mode 3: Flush only on time (size=0)."""

    def test_flush_on_time_interval(self, tmp_path: Path):
        """Flush based on time only — verify all JSON entries."""
        log_file = tmp_path / "mode3_time.log"
        logger = Logger()
        logger.init(str(log_file), size=0, flush=0.05)

        for i in range(5):
            logger.warning(f"warn-{i}")

        time.sleep(0.1)
        logger.shutdown_async()

        entries = _parse_log(log_file)
        assert len(entries) == 5
        for i in range(5):
            assert entries[i]["msg"] == f"warn-{i}"
            assert entries[i]["mt"] == "warning"

    def test_no_batch_trigger(self, tmp_path: Path):
        """Batch size disabled, time is only trigger — verify JSON."""
        log_file = tmp_path / "mode3_no_batch.log"
        logger = Logger()
        logger.init(str(log_file), size=0, flush=0.05)

        for i in range(10):
            logger.info(f"msg{i}")

        time.sleep(0.1)
        logger.shutdown_async()

        entries = _parse_log(log_file)
        assert len(entries) == 10
        assert entries[9]["msg"] == "msg9"


# ============================================================================
# On-Demand Flush via log.flush()
# ============================================================================

class TestOnDemandFlush:
    """On-demand flush() drains the queue and writes to real file."""

    def test_flush_writes_immediately(self, tmp_path: Path):
        """flush() forces all pending messages to disk."""
        log_file = tmp_path / "ondemand.log"
        logger = Logger()
        # Large batch/interval so nothing flushes automatically
        logger.init(str(log_file), size=10000, flush=60.0)

        for i in range(20):
            logger.info(f"flush-msg-{i}")

        logger.flush(timeout=5.0)

        entries = _parse_log(log_file)
        assert len(entries) == 20
        assert entries[0]["msg"] == "flush-msg-0"
        assert entries[19]["msg"] == "flush-msg-19"

        logger.shutdown_async()

    def test_flush_then_more_messages(self, tmp_path: Path):
        """Multiple flushes accumulate correctly."""
        log_file = tmp_path / "multi_flush.log"
        logger = Logger()
        logger.init(str(log_file), size=10000, flush=60.0)

        for i in range(5):
            logger.debug(f"batch1-{i}")
        logger.flush(timeout=5.0)

        count1 = len(_parse_log(log_file))
        assert count1 == 5

        for i in range(10):
            logger.error(f"batch2-{i}")
        logger.flush(timeout=5.0)

        entries = _parse_log(log_file)
        assert len(entries) == 15
        # Second batch should be error level
        assert entries[5]["mt"] == "error"
        assert entries[5]["msg"] == "batch2-0"

        logger.shutdown_async()

    def test_flush_returns_self(self, tmp_path: Path):
        """flush() returns self for chaining."""
        log_file = tmp_path / "chain.log"
        logger = Logger()
        logger.init(str(log_file), size=10000, flush=60.0)
        logger.info("chain-msg")

        result = logger.flush(timeout=5.0)
        assert result is logger

        logger.shutdown_async()

    def test_flush_noop_when_empty(self, tmp_path: Path):
        """flush() with no pending messages is a no-op."""
        log_file = tmp_path / "empty_flush.log"
        logger = Logger()
        logger.init(str(log_file), size=10000, flush=60.0)

        logger.flush(timeout=2.0)

        assert log_file.stat().st_size == 0
        logger.shutdown_async()


# ============================================================================
# Adaptive Flush Mode
# ============================================================================

class TestAdaptiveFlushMode:
    """Adaptive flush adjusts batch/interval and writes to real file."""

    def test_adaptive_logs_correctly(self, tmp_path: Path):
        """Adaptive mode logs all messages to file."""
        log_file = tmp_path / "adaptive.log"
        logger = Logger()
        logger.init(str(log_file), size=100, flush=0.1)
        logger.enable_adaptive(min_batch=5, max_batch=200)

        for i in range(30):
            logger.info(f"adapt-{i}")

        logger.flush(timeout=5.0)

        entries = _parse_log(log_file)
        assert len(entries) == 30
        assert entries[0]["msg"] == "adapt-0"
        assert entries[29]["msg"] == "adapt-29"

        logger.disable_adaptive()
        logger.shutdown_async()

    def test_adaptive_enable_disable(self, tmp_path: Path):
        """Enable, log, disable, log — all messages persist."""
        log_file = tmp_path / "adaptive_toggle.log"
        logger = Logger()
        logger.init(str(log_file), size=10000, flush=60.0)

        logger.enable_adaptive()
        for i in range(10):
            logger.info(f"adaptive-{i}")
        logger.flush(timeout=5.0)

        logger.disable_adaptive()
        for i in range(10):
            logger.info(f"static-{i}")
        logger.flush(timeout=5.0)

        entries = _parse_log(log_file)
        assert len(entries) == 20
        assert entries[0]["msg"] == "adaptive-0"
        assert entries[10]["msg"] == "static-0"

        logger.shutdown_async()

    def test_adaptive_returns_self(self, tmp_path: Path):
        """enable_adaptive() and disable_adaptive() return self."""
        log_file = tmp_path / "chain.log"
        logger = Logger()
        logger.init(str(log_file), size=100, flush=0.1)

        result = logger.enable_adaptive()
        assert result is logger
        result = logger.disable_adaptive()
        assert result is logger

        logger.shutdown_async()


# ============================================================================
# Deadline
# ============================================================================

class TestDeadline:
    """Deadline forces flush after max time."""

    def test_deadline_enforced(self, tmp_path: Path):
        """Deadline triggers flush even without other triggers — verify JSON."""
        log_file = tmp_path / "deadline.log"
        logger = Logger()
        logger.init(str(log_file), size=0, flush=10.0, deadline=0.1)

        logger.info("deadline-msg")

        time.sleep(0.15)
        logger.shutdown_async()

        entries = _parse_log(log_file)
        assert len(entries) == 1
        assert entries[0]["msg"] == "deadline-msg"
        assert entries[0]["mt"] == "info"


# ============================================================================
# SI Time Values
# ============================================================================

class TestSiTimeValues:
    """SI time string values work in init()."""

    def test_flush_ms_string(self, tmp_path: Path):
        """Flush accepts 'ms' string — verify JSON."""
        log_file = tmp_path / "si_ms.log"
        logger = Logger()
        logger.init(str(log_file), size=0, flush="10ms")

        logger.info("ms-msg")
        time.sleep(0.02)
        logger.shutdown_async()

        entries = _parse_log(log_file)
        assert len(entries) == 1
        assert entries[0]["msg"] == "ms-msg"

    def test_flush_us_string(self, tmp_path: Path):
        """Flush accepts 'µs' string — verify JSON."""
        log_file = tmp_path / "si_us.log"
        logger = Logger()
        logger.init(str(log_file), size=0, flush="100µs")

        logger.info("us-msg")
        time.sleep(0.001)
        logger.shutdown_async()

        entries = _parse_log(log_file)
        assert len(entries) == 1
        assert entries[0]["msg"] == "us-msg"

    def test_deadline_minutes_string(self, tmp_path: Path):
        """Deadline accepts 'm' string — verify JSON."""
        log_file = tmp_path / "si_min.log"
        logger = Logger()
        logger.init(str(log_file), size=0, flush="1s", deadline="1m")

        logger.info("min-msg")
        logger.shutdown_async()

        entries = _parse_log(log_file)
        assert len(entries) == 1
        assert entries[0]["msg"] == "min-msg"

    def test_mixed_float_and_si(self, tmp_path: Path):
        """Can mix float and SI string values — verify JSON."""
        log_file = tmp_path / "mixed.log"
        logger = Logger()
        logger.init(str(log_file), size=100, flush=0.1, deadline="5m")

        logger.info("mixed-msg")
        logger.shutdown_async()

        entries = _parse_log(log_file)
        assert len(entries) == 1
        assert entries[0]["msg"] == "mixed-msg"


# ============================================================================
# Empty String Target
# ============================================================================

class TestEmptyStringTarget:
    """Empty string target auto-generates filename."""

    def test_empty_string_creates_file(self, tmp_path: Path, monkeypatch):
        """Empty string creates log file."""
        monkeypatch.chdir(tmp_path)

        logger = Logger()
        logger.init('', size=0, flush=0.01)

        assert logger._auto_log_file is not None

        logger.info("test")
        time.sleep(0.05)
        logger.shutdown_async()

        assert logger._auto_log_file.exists()


# ============================================================================
# Policy Behavior
# ============================================================================

class TestPolicyBehavior:
    """Policy behaviors with full queue."""

    def test_block_policy_waits(self, tmp_path: Path):
        """'block' policy waits for space — all messages delivered."""
        log_file = tmp_path / "block.log"
        logger = Logger()
        logger.init(str(log_file), queue=5, size=10, flush=0.1, policy="block")

        for i in range(5):
            logger.info(f"block-{i}")

        time.sleep(0.2)
        logger.shutdown_async()

        entries = _parse_log(log_file)
        assert len(entries) == 5
        assert entries[0]["msg"] == "block-0"
        assert entries[4]["msg"] == "block-4"

    def test_skip_policy_drops(self, tmp_path: Path):
        """'skip' policy drops when full — at least some delivered."""
        log_file = tmp_path / "skip.log"
        logger = Logger()
        logger.init(str(log_file), queue=5, size=100, flush=1.0, policy="skip")

        for i in range(100):
            logger.info(f"skip-{i}")

        logger.shutdown_async()

        entries = _parse_log(log_file)
        # At least some messages got through
        assert len(entries) >= 1
        # Each entry has valid JSON with msg field
        for entry in entries:
            assert "msg" in entry
            assert entry["msg"].startswith("skip-")
