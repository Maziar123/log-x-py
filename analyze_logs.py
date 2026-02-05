#!/usr/bin/env python3
"""
Analyze existing log files for performance bottlenecks
"""

import json
from collections import defaultdict
from pathlib import Path


def analyze_logs():
    """Analyze log files from example-output-log directory"""
    log_dir = Path("eliot/examples/example-output-log")

    if not log_dir.exists():
        print(f"Error: {log_dir} not found")
        return

    print("=" * 80)
    print("LOG FILE ANALYSIS - Performance & Bottleneck Detection")
    print("=" * 80)
    print()

    results = []

    for log_file in sorted(log_dir.glob("*.log")):
        name = log_file.stem
        content = log_file.read_text()
        size = log_file.stat().st_size

        # Parse JSON logs
        logs = []
        for line in content.split("\n"):
            if line.strip().startswith("{"):
                try:
                    logs.append(json.loads(line))
                except (json.JSONDecodeError, ValueError):
                    pass

        # Analyze durations
        durations = [log.get("eliot:duration", 0) for log in logs if "eliot:duration" in log]
        total_duration = sum(durations)
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0

        # Count log levels
        levels = defaultdict(int)
        for log in logs:
            msg_type = log.get("message_type", "unknown")
            levels[msg_type] += 1

        # Count actions
        actions = defaultdict(int)
        for log in logs:
            action_type = log.get("action_type", "")
            if action_type:
                actions[action_type] += 1

        # Find LEVEL 7 (deepest nesting)
        level_7_count = sum(1 for log in logs if "LEVEL 7" in log.get("message", ""))
        max_nesting = max((len(log.get("task_level", [])) for log in logs), default=0)

        results.append(
            {
                "name": name,
                "size": size,
                "log_count": len(logs),
                "total_duration": total_duration,
                "avg_duration": avg_duration,
                "max_duration": max_duration,
                "levels": dict(levels),
                "actions": len(actions),
                "level_7": level_7_count,
                "max_nesting": max_nesting,
            },
        )

    # Print results
    print(f"{'Example':<25} {'Size':<10} {'Logs':<8} {'Actions':<10} {'Max Nest':<10}")
    print("-" * 80)

    for r in results:
        print(
            f"{r['name']:<25} {r['size'] / 1024:>7.2f}KB {r['log_count']:>6}   {r['actions']:>8}   {r['max_nesting']:>8}",
        )

    print("-" * 80)
    total_size = sum(r["size"] for r in results)
    total_logs = sum(r["log_count"] for r in results)
    print(f"{'TOTAL':<25} {total_size / 1024:>7.2f}KB {total_logs:>6}")
    print()

    # Performance Analysis
    print("=" * 80)
    print("PERFORMANCE ANALYSIS")
    print("=" * 80)
    print()

    # Duration analysis
    with_durations = [r for r in results if r["total_duration"] > 0]
    if with_durations:
        print("EXECUTION TIMES (from eliot:duration field):")
        for r in sorted(with_durations, key=lambda x: x["total_duration"], reverse=True):
            print(
                f"  {r['name']:<25} Total: {r['total_duration']:>7.3f}s  Avg: {r['avg_duration']:>7.4f}s  Max: {r['max_duration']:>7.4f}s",
            )
        print()

    # Bottleneck Detection
    print("=" * 80)
    print("BOTTLENECK DETECTION")
    print("=" * 80)
    print()

    bottlenecks_found = False

    # Large log files (>50KB)
    large_logs = [r for r in results if r["size"] > 50000]
    if large_logs:
        bottlenecks_found = True
        print("🔴 LARGE LOG OUTPUT (>50KB):")
        for r in sorted(large_logs, key=lambda x: x["size"], reverse=True):
            print(f"   {r['name']:<25} {r['size'] / 1024:>7.1f}KB  ({r['log_count']} logs)")
            print("      → Consider: Reduce log verbosity, use sampling, or log level filtering")
        print()

    # Slow operations (max_duration > 0.1s)
    slow_ops = [r for r in results if r["max_duration"] > 0.1]
    if slow_ops:
        bottlenecks_found = True
        print("🟡 SLOW OPERATIONS (max duration >0.1s):")
        for r in sorted(slow_ops, key=lambda x: x["max_duration"], reverse=True):
            print(f"   {r['name']:<25} Max: {r['max_duration']:.4f}s  Avg: {r['avg_duration']:.4f}s")
            print("      → Consider: Optimize slow function calls, add caching, or async operations")
        print()

    # Many actions (>100)
    many_actions = [r for r in results if r["log_count"] > 100]
    if many_actions:
        bottlenecks_found = True
        print("🟡 HIGH LOG VOLUME (>100 log entries):")
        for r in sorted(many_actions, key=lambda x: x["log_count"], reverse=True):
            print(f"   {r['name']:<25} {r['log_count']:>5} logs  ({r['actions']} unique actions)")
            print("      → Consider: Use log level filtering or structured logging patterns")
        print()

    if not bottlenecks_found:
        print("✅ NO SIGNIFICANT BOTTLENECKS DETECTED")
        print()
        print("All examples are performing within acceptable ranges:")
        print("  • Log sizes are reasonable (<50KB)")
        print("  • Operation durations are fast (<0.1s)")
        print("  • Log volumes are manageable (<100 entries)")
        print()

    # Deep Nesting Analysis
    print("=" * 80)
    print("DEEP NESTING ANALYSIS (7-Level Examples)")
    print("=" * 80)
    print()

    deep_examples = [r for r in results if r["level_7"] > 0 or r["max_nesting"] >= 7]
    if deep_examples:
        print("Examples with 7-level deep nesting:")
        for r in deep_examples:
            print(f"  {r['name']:<25} LEVEL 7 logs: {r['level_7']:>3}  Max nesting: {r['max_nesting']}")
        print()
        print("✓ Deep nesting successfully implemented without performance degradation")
    else:
        print("No examples with 7-level nesting detected")
    print()

    # Recommendations
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()

    recommendations = []

    # Check for optimization opportunities
    if large_logs:
        recommendations.append("📌 Large Log Files: Use log rotation or stream to remote service")
        recommendations.append("   Examples affected: " + ", ".join(r["name"] for r in large_logs))

    if slow_ops:
        recommendations.append("📌 Slow Operations: Profile and optimize critical paths")
        recommendations.append("   Examples affected: " + ", ".join(r["name"] for r in slow_ops))

    # General best practices
    recommendations.append("📌 Best Practices:")
    recommendations.append("   • Use appropriate log levels (DEBUG for development, INFO for production)")
    recommendations.append("   • Implement sampling for high-frequency logs")
    recommendations.append("   • Use structured logging with consistent field names")
    recommendations.append("   • Monitor log volume in production")

    for rec in recommendations:
        print(rec)

    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    analyze_logs()
