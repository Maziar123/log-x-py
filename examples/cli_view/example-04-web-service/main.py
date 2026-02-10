#!/usr/bin/env python3
"""
Example 04: Web Service Logging

This example shows HTTP request/response logging with pattern extraction
and filtering by action type.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "../../src")

from logxpy_cli_view import (
    combine_filters_and,
    create_common_classifier,
    extract_ips,
    extract_urls,
    filter_by_action_type,
    filter_by_duration,
    render_tasks,
    tasks_from_iterable,
)


def main() -> None:
    log_file = Path("web_service.log")

    with open(log_file) as f:
        log_entries = [line.strip() for line in f if line.strip()]

    parsed_logs = [json.loads(line) for line in log_entries]

    print("=" * 70)
    print("Example 04: Web Service Request Flow (All)")
    print("=" * 70)
    tasks = tasks_from_iterable(parsed_logs)
    import sys
    render_tasks(write=sys.stdout.write, tasks=tasks, field_limit=50, human_readable=True)

    # NEW: Pattern extraction
    print("\n" + "=" * 70)
    print("🔍 Pattern Extraction")
    print("=" * 70)

    all_text = json.dumps(parsed_logs)

    urls = extract_urls(all_text)
    if urls:
        print(f"\nFound {len(urls)} URLs:")
        for url in set(urls[:5]):  # Show unique URLs, max 5
            print(f"  - {url}")

    ips = extract_ips(all_text)
    if ips:
        print(f"\nFound {len(ips)} IP addresses:")
        for ip in set(ips[:5]):
            print(f"  - {ip}")

    # NEW: Log classification
    print("\n" + "=" * 70)
    print("🏷️  Log Classification")
    print("=" * 70)

    classifier = create_common_classifier()
    categories_found: dict[str, int] = {}

    for log in parsed_logs:
        text = json.dumps(log)
        categories = classifier.classify(text)
        for cat in categories:
            categories_found[cat] = categories_found.get(cat, 0) + 1

    print("\nCategories found:")
    for cat, count in sorted(categories_found.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    # NEW: Filter HTTP requests
    print("\n" + "=" * 70)
    print("🔍 HTTP Requests Only")
    print("=" * 70)

    http_tasks = list(filter(
        filter_by_action_type(r"http:.*", regex=True),
        parsed_logs
    ))
    if http_tasks:
        tasks = tasks_from_iterable(http_tasks)
        render_tasks(tasks, field_limit=50)
        print(f"\nFound {len(http_tasks)} HTTP tasks")

    # NEW: Filter slow requests (> 1 second)
    print("\n" + "=" * 70)
    print("🔍 Slow Requests (> 1s)")
    print("=" * 70)

    slow_tasks = list(filter(
        combine_filters_and(
            filter_by_action_type(r"http:.*", regex=True),
            filter_by_duration(min_seconds=1.0),
        ),
        parsed_logs
    ))
    if slow_tasks:
        tasks = tasks_from_iterable(slow_tasks)
        render_tasks(tasks, field_limit=50)
        print(f"\nFound {len(slow_tasks)} slow requests")
    else:
        print("No slow requests found")


if __name__ == "__main__":
    main()
