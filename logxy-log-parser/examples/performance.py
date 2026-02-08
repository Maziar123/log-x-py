"""
Performance Analysis Examples for logxy-log-parser.

This script demonstrates performance analysis capabilities:
1. Find slowest and fastest actions
2. Get duration statistics by action type
3. Calculate percentiles
4. Analyze task durations
5. Timeline analysis
"""

from logxy_log_parser import LogParser, LogAnalyzer, format_timestamp


def example_slowest_actions():
    """Find the slowest actions in the log."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("=== Slowest Actions ===")

    # Get 10 slowest actions
    slowest = analyzer.slowest_actions(n=10)
    print(f"Top {len(slowest)} slowest actions:")
    for i, stat in enumerate(slowest, 1):
        print(f"  {i}. {stat.action_type}: {stat.mean_duration:.3f}s (count: {stat.count})")


def example_fastest_actions():
    """Find the fastest actions in the log."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Fastest Actions ===")

    # Get 10 fastest actions
    fastest = analyzer.fastest_actions(n=10)
    print(f"Top {len(fastest)} fastest actions:")
    for i, stat in enumerate(fastest, 1):
        print(f"  {i}. {stat.action_type}: {stat.mean_duration:.3f}s (count: {stat.count})")


def example_duration_by_action():
    """Get duration statistics grouped by action type."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Duration by Action Type ===")

    stats = analyzer.duration_by_action()
    for action_type, duration_stats in stats.items():
        print(f"\n{action_type}:")
        print(f"  Count: {duration_stats.count}")
        print(f"  Mean: {duration_stats.mean:.3f}s")
        print(f"  Median: {duration_stats.median:.3f}s")
        print(f"  Min: {duration_stats.min:.3f}s")
        print(f"  Max: {duration_stats.max:.3f}s")
        print(f"  Std: {duration_stats.std:.3f}s")


def example_percentile_durations():
    """Get actions at a specific percentile."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Percentile Durations ===")

    # Get 95th percentile actions
    p95 = analyzer.percentile_durations(percentile=95)
    print("95th percentile actions:")
    for stat in p95[:5]:
        print(f"  {stat.action_type}: {stat.mean_duration:.3f}s")

    # Get 99th percentile actions
    p99 = analyzer.percentile_durations(percentile=99)
    print("\n99th percentile actions:")
    for stat in p99[:5]:
        print(f"  {stat.action_type}: {stat.mean_duration:.3f}s")


def example_task_duration_stats():
    """Get duration statistics for each task."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Task Duration Stats ===")

    stats = analyzer.task_duration_stats()
    for task_uuid, duration_stats in stats.items():
        print(f"\nTask: {task_uuid[:8]}...")
        print(f"  Count: {duration_stats.count}")
        print(f"  Total: {duration_stats.total:.3f}s")
        print(f"  Mean: {duration_stats.mean:.3f}s")
        print(f"  Min: {duration_stats.min:.3f}s")
        print(f"  Max: {duration_stats.max:.3f}s")


def example_deepest_nesting():
    """Find the deepest nesting level in the logs."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Deepest Nesting ===")

    depth = analyzer.deepest_nesting()
    print(f"Deepest nesting level: {depth}")


def example_widest_tasks():
    """Find tasks with the most child actions."""
    parser = LogParser("tests/fixtures/sample.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Widest Tasks ===")

    widest = analyzer.widest_tasks()
    print(f"Top {len(widest)} widest tasks:")
    for task_uuid, child_count in widest:
        print(f"  {task_uuid[:8]}...: {child_count} children")


def example_timeline():
    """Get timeline of log activity."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Timeline (1-minute intervals) ===")

    timeline = analyzer.timeline(interval="1min")
    print(f"Timeline spans {len(timeline.intervals)} intervals:")
    for period in timeline.intervals[:5]:
        start_str = format_timestamp(period.start)
        end_str = format_timestamp(period.end)
        print(f"  {start_str} - {end_str}: {period.entry_count} entries")


def example_peak_periods():
    """Find periods with highest activity."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Peak Periods ===")

    peaks = analyzer.peak_periods(n=3)
    print(f"Top {len(peaks)} peak periods:")
    for i, period in enumerate(peaks, 1):
        start_str = format_timestamp(period.start)
        end_str = format_timestamp(period.end)
        print(f"  {i}. {start_str} - {end_str}: {period.entry_count} entries")


def example_quiet_periods():
    """Find periods with lowest activity."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Quiet Periods ===")

    quiet = analyzer.quiet_periods(n=3)
    print(f"Top {len(quiet)} quiet periods:")
    for i, period in enumerate(quiet, 1):
        start_str = format_timestamp(period.start)
        end_str = format_timestamp(period.end)
        print(f"  {i}. {start_str} - {end_str}: {period.entry_count} entries")


def example_generate_report():
    """Generate an HTML performance report."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Generate Performance Report ===")

    # Generate HTML report
    html_report = analyzer.generate_report(report_format="html")
    print(f"HTML report length: {len(html_report)} characters")

    # Save to file
    with open("performance_report.html", "w", encoding="utf-8") as f:
        f.write(html_report)
    print("Report saved to performance_report.html")

    # Generate text report
    text_report = analyzer.generate_report(report_format="text")
    print(f"\nText report:\n{text_report[:500]}...")

    # Generate JSON report
    json_report = analyzer.generate_report(report_format="json")
    print(f"\nJSON report length: {len(json_report)} characters")


def example_combined_analysis():
    """Combine multiple analysis methods."""
    parser = LogParser("tests/fixtures/complex.log")
    logs = parser.parse()
    analyzer = LogAnalyzer(logs)

    print("\n=== Combined Performance Analysis ===")

    # Get slowest actions
    slowest = analyzer.slowest_actions(n=3)
    print("Slowest actions:")
    for stat in slowest:
        print(f"  - {stat.action_type}: {stat.mean_duration:.3f}s")

    # Get duration stats for slowest action
    stats = analyzer.duration_by_action()
    if slowest:
        action = slowest[0].action_type
        if action in stats:
            print(f"\nDetailed stats for {action}:")
            ds = stats[action]
            print(f"  Count: {ds.count}")
            print(f"  Mean: {ds.mean:.3f}s")
            print(f"  P95: {ds.p95:.3f}s")
            print(f"  P99: {ds.p99:.3f}s")


def main():
    """Run all examples."""
    example_slowest_actions()
    example_fastest_actions()
    example_duration_by_action()
    example_percentile_durations()
    example_task_duration_stats()
    example_deepest_nesting()
    example_widest_tasks()
    example_timeline()
    example_peak_periods()
    example_quiet_periods()
    example_generate_report()
    example_combined_analysis()


if __name__ == "__main__":
    main()
