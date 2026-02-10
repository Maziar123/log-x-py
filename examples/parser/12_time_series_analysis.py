#!/usr/bin/env python3
"""
12_time_series_analysis.py - Time Series Analysis Feature

Demonstrates time-series analysis capabilities:
- Anomaly detection
- Heatmaps
- Burst detection
- Error rate trends
"""
from __future__ import annotations

import tempfile
from pathlib import Path

# Create sample log first
from logxpy import log, to_file, start_action
import time as time_module


def create_sample_log() -> Path:
    """Create a sample log file with time-series patterns."""
    log_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log")
    log_path = Path(log_file.name)

    if log_path.exists():
        log_path.unlink()
    with open(log_path, "w", encoding="utf-8") as f:
        to_file(f)

    # Simulate time-series data with bursts
    base_time = time_module.time()

    # Normal period
    for i in range(5):
        log.info(f"Normal operation {i}", iteration=i)

    # Burst period (high activity)
    log.warning("Burst detected - high traffic")
    for i in range(10):
        log.info(f"High traffic request {i}", request_id=i)

    # Error spike
    log.error("Database timeout", timeout_seconds=30)
    log.error("Connection refused", host="db-server")
    log.error("Query failed", sql="SELECT * FROM users")

    # Recovery period
    log.info("Recovery started")
    for i in range(3):
        log.success(f"System stabilized {i}")

    # Another burst
    log.warning("Second burst detected")
    for i in range(8):
        log.info(f"Burst request {i}", request_id=i)

    return log_path


def main():
    """Demonstrate time series analysis functionality."""
    from logxy_log_parser import parse_log, TimeSeriesAnalyzer

    # Create sample log
    log_path = create_sample_log()
    print(f"Created sample log: {log_path}")

    # Parse entries
    entries = parse_log(log_path)

    # ========================================
    # 1. TIME SERIES ANALYZER
    # ========================================
    print("\n" + "=" * 60)
    print("1. TIME SERIES ANALYZER - Bucket by Interval")
    print("=" * 60)

    analyzer = TimeSeriesAnalyzer(entries)

    # Bucket by 1-second intervals
    buckets = analyzer.bucket_by_interval(interval_seconds=1)
    print(f"Time buckets (1s intervals): {len(buckets)}")
    for bucket in buckets[:5]:
        print(f"  {bucket.start:.2f}: {bucket.count} entries, "
              f"{bucket.error_count} errors")

    # ========================================
    # 2. ANOMALY DETECTION
    # ========================================
    print("\n" + "=" * 60)
    print("2. ANOMALY DETECTION - Find Unusual Patterns")
    print("=" * 60)

    anomalies = analyzer.detect_anomalies(window_size=3, threshold=1.5)
    print(f"Anomalies detected: {len(anomalies)}")
    for anomaly in anomalies:
        anomaly_type = anomaly["type"]  # "spike" or "drop"
        print(f"  - {anomaly_type} at {anomaly['timestamp']:.2f}: "
              f"{anomaly['count']} entries (expected: {anomaly['expected']:.1f})")

    # ========================================
    # 3. ERROR RATE TREND
    # ========================================
    print("\n" + "=" * 60)
    print("3. ERROR RATE TREND - Track Error Rate Over Time")
    print("=" * 60)

    error_trend = analyzer.error_rate_trend(interval_seconds=1)
    print(f"Error rate data points: {len(error_trend)}")
    for data_point in error_trend[:5]:
        print(f"  {data_point['timestamp']:.2f}: "
              f"error_rate={data_point['error_rate']:.2%}, "
              f"errors={data_point['error_count']}/{data_point['total_count']}")

    # ========================================
    # 4. ACTIVITY HEATMAP
    # ========================================
    print("\n" + "=" * 60)
    print("4. ACTIVITY HEATMAP - Activity by Time Period")
    print("=" * 60)

    # Heatmap by hour (aggregates across all data)
    heatmap = analyzer.activity_heatmap(hour_granularity=False)
    print(f"Heatmap categories: {len(heatmap)}")
    for period, counts in list(heatmap.items())[:3]:
        print(f"  {period}: {len(counts)} activity types")

    # ========================================
    # 5. BURST DETECTION
    # ========================================
    print("\n" + "=" * 60)
    print("5. BURST DETECTION - Find High Activity Periods")
    print("=" * 60)

    bursts = analyzer.burst_detection(threshold=1.5, min_interval=0.5)
    print(f"Bursts detected: {len(bursts)}")
    for burst in bursts:
        print(f"  - Burst: {burst['start']:.2f} to {burst['end']:.2f}")
        print(f"    Peak count: {burst['peak_count']}, threshold: {burst['threshold']:.1f}")

    # ========================================
    # 6. LEVEL DISTRIBUTION OVER TIME
    # ========================================
    print("\n" + "=" * 60)
    print("6. LEVEL DISTRIBUTION - Log Levels Over Time")
    print("=" * 60)

    level_dist = analyzer.level_distribution_over_time(interval_seconds=2)
    for level, points in list(level_dist.items())[:3]:
        print(f"  {level}: {len(points)} data points")
        if points:
            timestamps, counts = zip(*points)
            print(f"    Range: {min(timestamps):.2f} to {max(timestamps):.2f}")

    # Cleanup
    log_path.unlink()

    print("\n" + "=" * 60)
    print("Time series analysis demonstration complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
