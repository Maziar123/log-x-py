"""
Comprehensive benchmark analysis for all Eliot examples.

Measures:
- Execution time
- Memory usage
- Log output size
- Messages per second
- CPU usage
- Identifies bottlenecks
"""

import json
import os
import sys
import time
import tracemalloc
from pathlib import Path

import psutil

# Add logxpy to path
sys.path.insert(0, str(Path(__file__).parent / "eliot"))

EXAMPLES = [
    ("01_simple_logging.py", "Simple Logging"),
    ("02_decorators.py", "Decorators"),
    ("03_context_scopes.py", "Context Scopes"),
    ("04_async_tasks.py", "Async Tasks"),
    ("05_error_handling.py", "Error Handling"),
    ("06_data_types.py", "Data Types"),
    ("07_generators_iterators.py", "Generators/Iterators"),
    ("08_tracing_opentelemetry.py", "OpenTelemetry"),
    ("09_configuration.py", "Configuration"),
    ("10_advanced_patterns.py", "Advanced Patterns"),
    ("11_complex_ecommerce.py", "Complex E-Commerce"),
    ("12_complex_banking.py", "Complex Banking"),
    ("13_complex_data_pipeline.py", "Complex Data Pipeline"),
]


class BenchmarkResult:
    """Stores benchmark results"""

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.execution_time = 0
        self.memory_peak = 0
        self.memory_current = 0
        self.log_entries = 0
        self.log_size = 0
        self.cpu_percent = 0
        self.messages_per_sec = 0
        self.success = False
        self.error = None


def benchmark_example(example_path, name, description):
    """Benchmark a single example"""
    result = BenchmarkResult(name, description)

    print(f"  Benchmarking {name}...", end=" ", flush=True)

    try:
        # Start memory tracking
        tracemalloc.start()
        process = psutil.Process()
        cpu_start = process.cpu_percent()

        # Start timing
        start_time = time.time()

        # Run example and capture output
        import subprocess

        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent / "eliot")

        proc = subprocess.Popen(
            [sys.executable, example_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=Path(__file__).parent,
        )

        output, _ = proc.communicate(timeout=30)

        # Stop timing
        end_time = time.time()
        result.execution_time = end_time - start_time

        # Memory metrics
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        result.memory_current = current / 1024 / 1024  # MB
        result.memory_peak = peak / 1024 / 1024  # MB

        # CPU metrics
        result.cpu_percent = process.cpu_percent() - cpu_start

        # Parse log output
        result.log_size = len(output)
        result.log_entries = output.decode("utf-8", errors="ignore").count("\n")

        # Count JSON messages
        json_count = 0
        for line in output.decode("utf-8", errors="ignore").split("\n"):
            if line.strip().startswith("{"):
                json_count += 1

        result.messages_per_sec = json_count / result.execution_time if result.execution_time > 0 else 0

        result.success = proc.returncode == 0

        print(f"✓ {result.execution_time:.3f}s")

    except subprocess.TimeoutExpired:
        result.error = "Timeout (>30s)"
        print("✗ TIMEOUT")
        tracemalloc.stop()
    except Exception as e:
        result.error = str(e)
        print(f"✗ ERROR: {e}")
        tracemalloc.stop()

    return result


def analyze_bottlenecks(results):
    """Analyze results to identify bottlenecks"""
    print("\n" + "=" * 80)
    print("BOTTLENECK ANALYSIS")
    print("=" * 80)

    bottlenecks = []

    # Execution time bottlenecks
    avg_time = sum(r.execution_time for r in results) / len(results)
    slow_examples = [r for r in results if r.execution_time > avg_time * 2]

    if slow_examples:
        bottlenecks.append(
            {
                "type": "Execution Time",
                "severity": "HIGH" if len(slow_examples) > 3 else "MEDIUM",
                "affected": [r.name for r in slow_examples],
                "details": f"Avg: {avg_time:.3f}s, Slow: {[f'{r.name} ({r.execution_time:.3f}s)' for r in slow_examples]}",
            },
        )

    # Memory bottlenecks
    avg_memory = sum(r.memory_peak for r in results) / len(results)
    memory_heavy = [r for r in results if r.memory_peak > avg_memory * 2]

    if memory_heavy:
        bottlenecks.append(
            {
                "type": "Memory Usage",
                "severity": "HIGH" if any(r.memory_peak > 100 for r in memory_heavy) else "MEDIUM",
                "affected": [r.name for r in memory_heavy],
                "details": f"Avg: {avg_memory:.2f}MB, Heavy: {[f'{r.name} ({r.memory_peak:.2f}MB)' for r in memory_heavy]}",
            },
        )

    # Log size bottlenecks
    avg_size = sum(r.log_size for r in results) / len(results)
    large_logs = [r for r in results if r.log_size > avg_size * 5]

    if large_logs:
        bottlenecks.append(
            {
                "type": "Log Size",
                "severity": "MEDIUM",
                "affected": [r.name for r in large_logs],
                "details": f"Avg: {avg_size / 1024:.2f}KB, Large: {[f'{r.name} ({r.log_size / 1024:.2f}KB)' for r in large_logs]}",
            },
        )

    # Performance bottlenecks (messages/sec)
    avg_msg_rate = sum(r.messages_per_sec for r in results) / len(results)
    slow_rate = [r for r in results if r.messages_per_sec < avg_msg_rate * 0.5 and r.messages_per_sec > 0]

    if slow_rate:
        bottlenecks.append(
            {
                "type": "Message Rate",
                "severity": "LOW",
                "affected": [r.name for r in slow_rate],
                "details": f"Avg: {avg_msg_rate:.1f} msg/s, Slow: {[f'{r.name} ({r.messages_per_sec:.1f} msg/s)' for r in slow_rate]}",
            },
        )

    return bottlenecks


def print_results(results, bottlenecks):
    """Print formatted results"""
    print("\n" + "=" * 80)
    print("BENCHMARK RESULTS")
    print("=" * 80)
    print()

    # Summary table
    print(f"{'Example':<30} {'Time':<10} {'Memory':<12} {'Log Size':<12} {'Msg/sec':<10}")
    print("-" * 80)

    for r in results:
        status = "✓" if r.success else "✗"
        print(
            f"{status} {r.name:<28} {r.execution_time:>7.3f}s  {r.memory_peak:>8.2f}MB  {r.log_size / 1024:>8.2f}KB  {r.messages_per_sec:>8.1f}",
        )

    print("-" * 80)

    # Totals
    total_time = sum(r.execution_time for r in results)
    total_memory = max(r.memory_peak for r in results)
    total_logs = sum(r.log_size for r in results)
    avg_msg_rate = sum(r.messages_per_sec for r in results) / len(results)

    print(
        f"{'TOTAL/MAX':<30} {total_time:>7.3f}s  {total_memory:>8.2f}MB  {total_logs / 1024:>8.2f}KB  {avg_msg_rate:>8.1f}",
    )
    print()

    # Statistics
    print("=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print()
    print(f"Total Examples:        {len(results)}")
    print(
        f"Success Rate:          {sum(1 for r in results if r.success)}/{len(results)} ({100 * sum(1 for r in results if r.success) / len(results):.1f}%)",
    )
    print(f"Total Execution Time:  {total_time:.3f}s")
    print(f"Average Execution:     {total_time / len(results):.3f}s")
    print(
        f"Fastest:               {min(r.execution_time for r in results):.3f}s ({min(results, key=lambda r: r.execution_time).name})",
    )
    print(
        f"Slowest:               {max(r.execution_time for r in results):.3f}s ({max(results, key=lambda r: r.execution_time).name})",
    )
    print()
    print(f"Average Memory:        {sum(r.memory_peak for r in results) / len(results):.2f}MB")
    print(
        f"Peak Memory:           {max(r.memory_peak for r in results):.2f}MB ({max(results, key=lambda r: r.memory_peak).name})",
    )
    print()
    print(f"Total Log Output:      {total_logs / 1024:.2f}KB")
    print(f"Average Log Size:      {total_logs / len(results) / 1024:.2f}KB")
    print(
        f"Largest Log:           {max(r.log_size for r in results) / 1024:.2f}KB ({max(results, key=lambda r: r.log_size).name})",
    )
    print()
    print(f"Avg Messages/Second:   {avg_msg_rate:.1f}")
    print(
        f"Fastest Rate:          {max(r.messages_per_sec for r in results):.1f} msg/s ({max(results, key=lambda r: r.messages_per_sec).name})",
    )
    print()

    # Bottlenecks
    if bottlenecks:
        print("=" * 80)
        print("BOTTLENECKS DETECTED")
        print("=" * 80)
        print()

        for i, b in enumerate(bottlenecks, 1):
            severity_color = {
                "HIGH": "🔴",
                "MEDIUM": "🟡",
                "LOW": "🟢",
            }

            print(f"{severity_color.get(b['severity'], '⚪')} {i}. {b['type']} - Severity: {b['severity']}")
            print(f"   Affected: {', '.join(b['affected'])}")
            print(f"   Details: {b['details']}")
            print()
    else:
        print("=" * 80)
        print("✅ NO SIGNIFICANT BOTTLENECKS DETECTED")
        print("=" * 80)
        print()

    # Recommendations
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()

    recommendations = []

    # Check for slow examples
    slow = [r for r in results if r.execution_time > 0.5]
    if slow:
        recommendations.append(f"⚠️  Slow Examples: {', '.join(r.name for r in slow)}")
        recommendations.append("   → Consider optimizing or reducing complexity")

    # Check for large logs
    large = [r for r in results if r.log_size > 100000]  # >100KB
    if large:
        recommendations.append(f"⚠️  Large Log Output: {', '.join(r.name for r in large)}")
        recommendations.append("   → Consider reducing log verbosity or using sampling")

    # Check for high memory
    memory_high = [r for r in results if r.memory_peak > 50]  # >50MB
    if memory_high:
        recommendations.append(f"⚠️  High Memory Usage: {', '.join(r.name for r in memory_high)}")
        recommendations.append("   → Review data structures and implement streaming where possible")

    if not recommendations:
        print("✅ All examples perform within acceptable ranges!")
    else:
        for rec in recommendations:
            print(rec)

    print()


def main():
    """Main benchmark runner"""
    print("=" * 80)
    print("ELIOT EXAMPLES - COMPREHENSIVE BENCHMARK ANALYSIS")
    print("=" * 80)
    print()
    print(f"Python:  {sys.version.split()[0]}")
    print(f"System:  {psutil.virtual_memory().total / 1024**3:.1f}GB RAM, {psutil.cpu_count()} CPUs")
    print()

    results = []
    examples_dir = Path(__file__).parent / "eliot" / "examples"

    for filename, description in EXAMPLES:
        example_path = examples_dir / filename
        if example_path.exists():
            result = benchmark_example(example_path, filename, description)
            results.append(result)
        else:
            print(f"  ✗ {filename} not found")

    # Analyze bottlenecks
    bottlenecks = analyze_bottlenecks(results)

    # Print results
    print_results(results, bottlenecks)

    # Save results to JSON
    output_file = Path(__file__).parent / "benchmark_results.json"
    with open(output_file, "w") as f:
        json.dump(
            [
                {
                    "name": r.name,
                    "description": r.description,
                    "execution_time": r.execution_time,
                    "memory_peak_mb": r.memory_peak,
                    "log_size_bytes": r.log_size,
                    "messages_per_sec": r.messages_per_sec,
                    "success": r.success,
                    "error": r.error,
                }
                for r in results
            ],
            f,
            indent=2,
        )

    print(f"📊 Results saved to: {output_file}")
    print()


if __name__ == "__main__":
    main()
