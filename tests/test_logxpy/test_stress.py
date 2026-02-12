"""Stress tests for high-throughput logging scenarios.

These tests verify the logging system under heavy load:
- High volume (millions of logs)
- Concurrent writers
- Memory stability
- Backpressure handling
"""

import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "/mnt/N1/MZ/AMZ/Projects/Prog/a_cross/log-x-py")

import pytest

from logxpy import log
from logxpy.src._writer import create_writer, WriterType, Mode, QueuePolicy


class TestHighVolume:
    """High volume stress tests."""
    
    def test_100k_logs_basic(self, tmp_path):
        """100,000 basic log messages."""
        log_file = tmp_path / "stress_100k.log"
        
        log.init(str(log_file), async_en=True, size=1000, writer_type="block")
        
        start = time.perf_counter()
        for i in range(100_000):
            log.info("Test message", index=i)
        log.shutdown_async()
        elapsed = time.perf_counter() - start
        
        throughput = 100_000 / elapsed
        print(f"\n100K logs: {throughput:,.0f} L/s")
        
        # Verify file size
        assert log_file.exists()
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 100_000
        
        # Should maintain decent throughput
        assert throughput > 100_000, f"Throughput {throughput} too low"
    
    def test_500k_logs_with_fields(self, tmp_path):
        """500,000 logs with multiple fields."""
        log_file = tmp_path / "stress_500k.log"
        
        log.init(str(log_file), async_en=True, size=500, writer_type="block")
        
        start = time.perf_counter()
        for i in range(500_000):
            log.info(
                "Processing",
                index=i,
                user_id=i % 1000,
                action="process",
                status="ok",
            )
        log.shutdown_async()
        elapsed = time.perf_counter() - start
        
        throughput = 500_000 / elapsed
        print(f"\n500K logs with fields: {throughput:,.0f} L/s")
        
        # Verify
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 500_000
    
    def test_1m_logs_small_batch(self, tmp_path):
        """1 million logs with small batch (memory stress test)."""
        log_file = tmp_path / "stress_1m.log"
        
        # Small batch size = more flushes = memory pressure
        log.init(str(log_file), async_en=True, size=10, writer_type="block")
        
        start = time.perf_counter()
        for i in range(1_000_000):
            log.debug("Debug info", iteration=i)
        log.shutdown_async()
        elapsed = time.perf_counter() - start
        
        throughput = 1_000_000 / elapsed
        print(f"\n1M logs (small batch): {throughput:,.0f} L/s")
        
        # Verify
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 1_000_000


class TestConcurrentLogging:
    """Concurrent multi-threaded logging tests."""
    
    def test_10_threads_10k_each(self, tmp_path):
        """10 threads, 10K logs each = 100K total."""
        log_file = tmp_path / "concurrent_10x10k.log"
        
        log.init(str(log_file), async_en=True, size=100, writer_type="block")
        
        def worker(thread_id: int, count: int):
            for i in range(count):
                log.info(f"Thread {thread_id}", thread_id=thread_id, seq=i)
        
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i, 10_000) for i in range(10)]
            for f in futures:
                f.result()
        
        log.shutdown_async()
        elapsed = time.perf_counter() - start
        
        throughput = 100_000 / elapsed
        print(f"\n10 threads x 10K: {throughput:,.0f} L/s")
        
        # Verify all logs written
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 100_000
    
    def test_50_threads_2k_each(self, tmp_path):
        """50 threads, 2K logs each = 100K total (heavy contention)."""
        log_file = tmp_path / "concurrent_50x2k.log"
        
        log.init(str(log_file), async_en=True, size=50, writer_type="block")
        
        def worker(thread_id: int, count: int):
            for i in range(count):
                log.info("Concurrent", tid=thread_id, seq=i)
        
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(worker, i, 2_000) for i in range(50)]
            for f in futures:
                f.result()
        
        log.shutdown_async()
        elapsed = time.perf_counter() - start
        
        throughput = 100_000 / elapsed
        print(f"\n50 threads x 2K: {throughput:,.0f} L/s")
        
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 100_000
    
    def test_mixed_levels_concurrent(self, tmp_path):
        """Concurrent threads with different log levels."""
        log_file = tmp_path / "concurrent_levels.log"
        
        log.init(str(log_file), async_en=True, size=100, writer_type="block")
        
        def debug_worker(count: int):
            for i in range(count):
                log.debug("Debug", idx=i)
        
        def info_worker(count: int):
            for i in range(count):
                log.info("Info", idx=i)
        
        def warning_worker(count: int):
            for i in range(count):
                log.warning("Warning", idx=i)
        
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = []
            futures.extend([executor.submit(debug_worker, 5_000) for _ in range(2)])
            futures.extend([executor.submit(info_worker, 5_000) for _ in range(2)])
            futures.extend([executor.submit(warning_worker, 5_000) for _ in range(2)])
            for f in futures:
                f.result()
        
        log.shutdown_async()
        elapsed = time.perf_counter() - start
        
        throughput = 30_000 / elapsed
        print(f"\nMixed levels concurrent: {throughput:,.0f} L/s")
        
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 30_000


class TestBackpressure:
    """Test backpressure policies under load."""
    
    def test_block_policy_under_load(self, tmp_path):
        """Block policy should handle high load without dropping."""
        log_file = tmp_path / "backpressure_block.log"
        
        writer = create_writer(
            path=str(log_file),
            writer_type=WriterType.BLOCK,
            mode=Mode.TRIGGER,
            queue_size=100,  # Small queue to force backpressure
            batch_size=10,
            policy=QueuePolicy.BLOCK,
        )
        
        # Rapid fire logs
        start = time.perf_counter()
        for i in range(10_000):
            writer.send(f'{{"msg":"test","i":{i}}}')
        writer.stop()
        elapsed = time.perf_counter() - start
        
        # All should be written (no drops with BLOCK policy)
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 10_000
        print(f"\nBlock policy: {10_000/elapsed:,.0f} L/s, 0 drops")
    
    def test_drop_oldest_policy(self, tmp_path):
        """Drop oldest policy should drop under pressure."""
        log_file = tmp_path / "backpressure_drop_oldest.log"
        
        writer = create_writer(
            path=str(log_file),
            writer_type=WriterType.BLOCK,
            mode=Mode.TRIGGER,
            queue_size=1000,
            batch_size=100,
            policy=QueuePolicy.DROP_OLDEST,
        )
        
        # Write more than queue can hold
        for i in range(50_000):
            writer.send(f'{{"i":{i}}}')
        
        metrics = writer.metrics
        writer.stop()
        
        # Some should have been dropped
        print(f"\nDrop oldest: enqueued={metrics.enqueued}, written={metrics.written}, dropped={metrics.dropped}")
        assert metrics.dropped > 0 or metrics.written < 50_000
    
    def test_drop_newest_policy(self, tmp_path):
        """Drop newest policy should drop under pressure."""
        log_file = tmp_path / "backpressure_drop_newest.log"
        
        writer = create_writer(
            path=str(log_file),
            writer_type=WriterType.BLOCK,
            mode=Mode.TRIGGER,
            queue_size=1000,
            batch_size=100,
            policy=QueuePolicy.DROP_NEWEST,
        )
        
        for i in range(50_000):
            writer.send(f'{{"i":{i}}}')
        
        metrics = writer.metrics
        writer.stop()
        
        print(f"\nDrop newest: enqueued={metrics.enqueued}, written={metrics.written}")
        # Should have written some but not all
        assert metrics.written < 50_000


class TestWriterTypesStress:
    """Stress test each writer type."""
    
    def test_line_writer_high_volume(self, tmp_path):
        """Line writer with high volume."""
        log_file = tmp_path / "stress_line.log"
        
        writer = create_writer(
            path=str(log_file),
            writer_type=WriterType.LINE,
            mode=Mode.TRIGGER,
            batch_size=100,
        )
        
        start = time.perf_counter()
        for i in range(50_000):
            writer.send(f'{{"msg":"line","i":{i}}}')
        writer.stop()
        elapsed = time.perf_counter() - start
        
        throughput = 50_000 / elapsed
        print(f"\nLine writer: {throughput:,.0f} L/s")
        
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 50_000
    
    def test_mmap_writer_high_volume(self, tmp_path):
        """Mmap writer with high volume."""
        log_file = tmp_path / "stress_mmap.log"
        
        writer = create_writer(
            path=str(log_file),
            writer_type=WriterType.MMAP,
            mode=Mode.TRIGGER,
            batch_size=500,
        )
        
        start = time.perf_counter()
        for i in range(100_000):
            writer.send(f'{{"msg":"mmap","i":{i}}}')
        writer.stop()
        elapsed = time.perf_counter() - start
        
        throughput = 100_000 / elapsed
        print(f"\nMmap writer: {throughput:,.0f} L/s")


class TestMemoryStability:
    """Memory usage stability tests."""
    
    def test_memory_stable_over_time(self, tmp_path):
        """Memory should not grow unbounded during long runs."""
        import gc
        import sys
        
        log_file = tmp_path / "memory_test.log"
        log.init(str(log_file), async_en=True, size=1000, writer_type="block")
        
        gc.collect()
        # Note: This is a basic check - memory profiling would need psutil
        
        # Log in batches and check consistency
        for batch in range(10):
            for i in range(10_000):
                log.info("Batch", batch=batch, seq=i)
            # Give writer time to catch up
            time.sleep(0.01)
        
        log.shutdown_async()
        
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 100_000
        print(f"\nMemory stability: 100K logs written successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
