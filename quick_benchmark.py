#!/usr/bin/env python3
"""
Quick benchmark analysis - measures execution time and identifies bottlenecks
Designed to not hang/freeze on any example
"""

import subprocess
import sys
import time
from pathlib import Path

# Example files to benchmark
EXAMPLES = [
    "01_simple_logging.py",
    "02_decorators.py",
    "03_context_scopes.py",
    "04_async_tasks.py",
    "05_error_handling.py",
    "06_data_types.py",
    "07_generators_iterators.py",
    "08_tracing_opentelemetry.py",
    "09_configuration.py",
    "10_advanced_patterns.py",
    "11_complex_ecommerce.py",
    "12_complex_banking.py",
    "13_complex_data_pipeline.py",
]


def run_benchmark():
    """Run quick benchmark on all examples"""
    print("=" * 70)
    print("QUICK BENCHMARK - Eliot Examples Performance Analysis")
    print("=" * 70)
    print()

    results = []
    examples_dir = Path(__file__).parent / "eliot" / "examples"

    for example in EXAMPLES:
        example_path = examples_dir / example

        if not example_path.exists():
            print(f"✗ {example:30s}  NOT FOUND")
            continue

        print(f"  {example:30s}  ", end="", flush=True)

        try:
            start = time.time()

            result = subprocess.run(
                [sys.executable, str(example_path)],
                env={**subprocess.os.environ, "PYTHONPATH": str(Path(__file__).parent / "eliot")},
                capture_output=True,
                timeout=5,  # 5 second timeout
                text=True,
            )

            elapsed = time.time() - start

            # Count JSON lines
            json_lines = sum(1 for line in result.stdout.split("\n") if line.strip().startswith("{"))
            log_size = len(result.stdout)

            success = result.returncode == 0
            status = "✓" if success else "✗"

            print(f"{status} {elapsed:6.3f}s  {json_lines:4d} logs  {log_size / 1024:7.2f}KB")

            results.append(
                {
                    "name": example,
                    "time": elapsed,
                    "logs": json_lines,
                    "size": log_size,
                    "success": success,
                },
            )

        except subprocess.TimeoutExpired:
            print("✗ TIMEOUT (>5s)")
            results.append(
                {
                    "name": example,
                    "time": 5.0,
                    "logs": 0,
                    "size": 0,
                    "success": False,
                    "error": "timeout",
                },
            )
        except Exception as e:
            print(f"✗ ERROR: {str(e)[:30]}")
            results.append(
                {
                    "name": example,
                    "time": 0,
                    "logs": 0,
                    "size": 0,
                    "success": False,
                    "error": str(e),
                },
            )

    # Analysis
    print()
    print("=" * 70)
    print("ANALYSIS & BOTTLENECKS")
    print("=" * 70)
    print()

    successful = [r for r in results if r["success"]]

    if not successful:
        print("⚠️  NO SUCCESSFUL RUNS")
        return

    avg_time = sum(r["time"] for r in successful) / len(successful)
    total_time = sum(r["time"] for r in successful)
    total_size = sum(r["size"] for r in successful)

    print(f"Success Rate:      {len(successful)}/{len(results)} ({100 * len(successful) / len(results):.0f}%)")
    print(f"Total Time:        {total_time:.3f}s")
    print(f"Average Time:      {avg_time:.3f}s")
    print(f"Total Log Output:  {total_size / 1024:.1f}KB")
    print()

    # Find bottlenecks
    print("BOTTLENECKS:")
    print()

    # Slow examples (>2x average)
    slow = [r for r in successful if r["time"] > avg_time * 2]
    if slow:
        print("🔴 SLOW EXECUTION (>2x average):")
        for r in sorted(slow, key=lambda x: x["time"], reverse=True):
            print(f"   {r['name']:30s}  {r['time']:.3f}s  ({r['time'] / avg_time:.1f}x slower)")
        print()

    # Large logs (>100KB)
    large = [r for r in successful if r["size"] > 100000]
    if large:
        print("🟡 LARGE LOG OUTPUT (>100KB):")
        for r in sorted(large, key=lambda x: x["size"], reverse=True):
            print(f"   {r['name']:30s}  {r['size'] / 1024:.1f}KB")
        print()

    # Failed examples
    failed = [r for r in results if not r["success"]]
    if failed:
        print("🔴 FAILED EXAMPLES:")
        for r in failed:
            error = r.get("error", "unknown")
            print(f"   {r['name']:30s}  {error}")
        print()

    if not slow and not large and not failed:
        print("✅ NO SIGNIFICANT BOTTLENECKS DETECTED")
        print()

    # Top 3 slowest
    print("SLOWEST EXAMPLES:")
    for i, r in enumerate(sorted(successful, key=lambda x: x["time"], reverse=True)[:3], 1):
        print(f"   {i}. {r['name']:30s}  {r['time']:.3f}s")
    print()

    # Top 3 largest logs
    print("LARGEST LOG OUTPUT:")
    for i, r in enumerate(sorted(successful, key=lambda x: x["size"], reverse=True)[:3], 1):
        print(f"   {i}. {r['name']:30s}  {r['size'] / 1024:.1f}KB  ({r['logs']} logs)")
    print()

    print("=" * 70)
    print()


if __name__ == "__main__":
    try:
        run_benchmark()
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        sys.exit(1)
