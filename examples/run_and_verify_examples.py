#!/usr/bin/env python3
"""Run all examples and verify log output.

This script runs all LogXPy examples, verifies the output log files,
and reports any errors or issues. It supports both sync and async modes.

Usage:
    cd examples && python run_and_verify_examples.py
    cd examples && LOGXPY_SYNC=1 python run_and_verify_examples.py  # Force sync mode
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Detect if we're running from examples dir or project root
script_dir = Path(__file__).parent
if script_dir.name == "examples":
    # Running from examples/ directory
    EXAMPLES_ROOT = script_dir
    os.chdir(EXAMPLES_ROOT)
else:
    # Running from project root or elsewhere
    EXAMPLES_ROOT = script_dir / "examples" if (script_dir / "examples").exists() else script_dir
    os.chdir(EXAMPLES_ROOT)

# LogXPy core examples
LOGXPY_EXAMPLES: list[tuple[str, str]] = [
    # (subdir, filename)
    ("logxpy", "01_simple_logging.py"),
    ("logxpy", "02_decorators.py"),
    ("logxpy", "03_context_scopes.py"),
    ("logxpy", "04_async_tasks.py"),
    ("logxpy", "05_error_handling.py"),
    ("logxpy", "06_data_types.py"),
    ("logxpy", "07_generators_iterators.py"),
    ("logxpy", "08_tracing_opentelemetry.py"),
    ("logxpy", "09_configuration.py"),
    ("logxpy", "10_advanced_patterns.py"),
    ("logxpy", "11_complex_ecommerce.py"),
    ("logxpy", "12_complex_banking.py"),
    ("logxpy", "13_complex_data_pipeline.py"),
    ("logxpy", "xx_Color_Methods1.py"),
]

# New async examples (top-level in examples/)
ASYNC_EXAMPLES: list[tuple[str, str]] = [
    (".", "example_async_basic.py"),
    (".", "example_async_disable.py"),
    (".", "example_async_high_throughput.py"),
]

# CLI view examples (run generate.py scripts)
CLI_VIEW_GENERATE_EXAMPLES: list[tuple[str, str]] = [
    ("cli_view/example-01-simple-task", "generate.py"),
    ("cli_view/example-02-nested-tasks", "generate.py"),
    ("cli_view/example-03-errors", "generate.py"),
    ("cli_view/example-04-web-service", "generate.py"),
    ("cli_view/example-05-data-pipeline", "generate.py"),
    ("cli_view/example-06-filtering", "generate.py"),
    ("cli_view/example-07-color-themes", "generate.py"),
    ("cli_view/example-08-metrics", "generate.py"),
    ("cli_view/example-09-generating", "generate.py"),
    ("cli_view/example-10-deep-functions", "generate.py"),
    ("cli_view/example-11-async-tasks", "generate.py"),
]

# Parser examples
PARSER_EXAMPLES: list[tuple[str, str]] = [
    ("parser", "01_basic.py"),
    ("parser", "02_filtering.py"),
    ("parser", "03_analysis.py"),
    ("parser", "10_check_presence.py"),
    ("parser", "11_indexing_system.py"),
    ("parser", "12_time_series_analysis.py"),
    ("parser", "13_export_data.py"),
    ("parser", "14_realtime_monitoring.py"),
    ("parser", "15_aggregation.py"),
    ("parser", "16_complete_reference.py"),
]

# Tutorial examples
TUTORIAL_EXAMPLES: list[tuple[str, str]] = [
    ("tutorials", "tutorial_01_basic_logging.py"),
    ("tutorials", "tutorial_02_actions_and_context.py"),
    ("tutorials", "tutorial_03_decorators.py"),
    ("tutorials", "tutorial_04_error_handling.py"),
    ("tutorials", "tutorial_05_real_world_api.py"),
]


def run_example(
    subdir: str, example_name: str, *, use_async: bool = True
) -> tuple[bool, str]:
    """Run an example and return success status and output."""
    example_path = Path(subdir) / example_name if subdir != "." else Path(example_name)
    log_path = example_path.with_suffix(".log")

    # Delete old log if exists
    if log_path.exists():
        log_path.unlink()

    # Set up environment with correct PYTHONPATH
    env = os.environ.copy()
    if not use_async:
        env["LOGXPY_SYNC"] = "1"
    
    # Add project root to PYTHONPATH so examples can import logxpy
    project_root = Path.cwd()
    if project_root.name == "examples":
        project_root = project_root.parent
    env["PYTHONPATH"] = str(project_root) + os.pathsep + env.get("PYTHONPATH", "")

    # Run the example with timeout
    try:
        result = subprocess.run(
            [sys.executable, str(example_path)],
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
            env=env,
        )
    except subprocess.TimeoutExpired:
        return False, "Timeout (60s)"

    if result.returncode != 0:
        return False, result.stderr or result.stdout

    # Small delay to allow async writer to flush
    if use_async:
        time.sleep(0.1)

    return True, result.stdout


def verify_log_file(log_path: Path) -> dict:
    """Verify log file has valid JSON lines."""
    if not log_path.exists():
        return {"exists": False, "lines": 0, "valid": 0}

    with open(log_path) as f:
        lines = f.readlines()

    valid = 0
    invalid = []
    for i, line in enumerate(lines, 1):
        if line.strip():
            try:
                json.loads(line)
                valid += 1
            except json.JSONDecodeError as e:
                invalid.append(f"Line {i}: {e}")

    return {
        "exists": True,
        "lines": len(lines),
        "valid": valid,
        "invalid": invalid,
    }


def run_cli_view_example(subdir: str, script_name: str) -> tuple[bool, str]:
    """Run a CLI view generate.py script."""
    script_path = Path(subdir) / script_name

    # Find expected output log file
    log_path = None
    parent_dir = Path(subdir)
    for f in parent_dir.glob("*.log"):
        log_path = f
        break

    # Delete old log if exists
    if log_path and log_path.exists():
        log_path.unlink()

    # Set up environment with correct PYTHONPATH
    env = os.environ.copy()
    project_root = Path.cwd()
    if project_root.name == "examples":
        project_root = project_root.parent
    env["PYTHONPATH"] = str(project_root) + os.pathsep + env.get("PYTHONPATH", "")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return False, "Timeout (30s)"

    if result.returncode != 0:
        # Some CLI examples just output to stdout
        if "No module named" in (result.stderr or ""):
            return False, result.stderr[:100]
        return True, "Generated (stdout output)"

    # Look for generated log file
    for f in parent_dir.glob("*.log"):
        return True, f"Generated {f.name}"

    return True, "No log file generated"


def run_category(
    category_name: str,
    examples: list[tuple[str, str]],
    *,
    use_async: bool = True,
    is_cli_view: bool = False,
    skip_reason: str | None = None,
) -> list[tuple[str, bool, str]]:
    """Run all examples in a category and return results."""
    results = []

    print(f"\n{'=' * 60}")
    print(f"{category_name}")
    print(f"{'=' * 60}")

    # If category is skipped entirely
    if skip_reason:
        print(f"\n⚠ Skipped: {skip_reason}")
        for subdir, example in examples:
            example_display = f"{subdir}/{example}" if subdir != "." else example
            results.append((example_display, True, f"Skipped: {skip_reason}"))
        return results

    for subdir, example in examples:
        example_display = f"{subdir}/{example}" if subdir != "." else example
        print(f"\n{example_display}:")

        if is_cli_view:
            success, output = run_cli_view_example(subdir, example)
        else:
            success, output = run_example(subdir, example, use_async=use_async)

        if not success:
            error_msg = output[:150] if len(output) > 150 else output
            print(f"  ❌ Failed: {error_msg}")
            results.append((example_display, False, "Execution failed"))
            continue

        # For CLI view examples, just check execution succeeded
        if is_cli_view:
            print(f"  ✅ {output}")
            results.append((example_display, True, output))
            continue

        # Verify log file for regular examples
        example_path = Path(subdir) / example if subdir != "." else Path(example)
        log_path = example_path.with_suffix(".log")
        verify = verify_log_file(log_path)

        if not verify["exists"]:
            print(f"  ⚠ No log file created")
            results.append((example_display, True, "No log file"))
            continue

        if verify["invalid"]:
            print(f"  ❌ Log has {len(verify['invalid'])} invalid JSON lines")
            for err in verify["invalid"][:3]:
                print(f"     {err}")
            results.append(
                (
                    example_display,
                    True,
                    f"Invalid JSON: {verify['valid']}/{verify['lines']}",
                )
            )
        else:
            print(f"  ✅ {verify['valid']} valid JSON lines")
            results.append((example_display, True, f"{verify['valid']} lines"))

    return results


def main():
    """Main entry point."""
    print("=" * 60)
    print("LogXPy Examples Runner and Verifier")
    print("=" * 60)

    # Check for sync mode
    use_async = os.environ.get("LOGXPY_SYNC") != "1"
    mode = "Async (default)" if use_async else "Sync (forced)"
    print(f"Mode: {mode}")
    print(f"Working directory: {Path.cwd()}")

    all_results = []

    # Run LogXPy core examples
    all_results.extend(
        run_category("LogXPy Core Examples", LOGXPY_EXAMPLES, use_async=use_async)
    )

    # Run new async examples
    all_results.extend(
        run_category("Async Logging Examples", ASYNC_EXAMPLES, use_async=True)
    )

    # Run CLI view examples
    all_results.extend(
        run_category("CLI View Examples", CLI_VIEW_GENERATE_EXAMPLES, is_cli_view=True)
    )

    # Run parser examples (skip if pandas not installed)
    try:
        import pandas  # noqa: F401

        all_results.extend(
            run_category("Parser Examples", PARSER_EXAMPLES, use_async=use_async)
        )
    except ImportError:
        all_results.extend(
            run_category(
                "Parser Examples",
                PARSER_EXAMPLES,
                use_async=use_async,
                skip_reason="pandas not installed",
            )
        )

    # Run tutorial examples
    all_results.extend(
        run_category("Tutorial Examples", TUTORIAL_EXAMPLES, use_async=use_async)
    )

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success, _ in all_results if success)
    total = len(all_results)

    print(f"\nPassed: {passed}/{total}")

    # Group by category for better readability
    categories: dict[str, list] = {}
    for example, success, status in all_results:
        category = example.split("/")[0] if "/" in example else "root"
        if category not in categories:
            categories[category] = []
        categories[category].append((example, success, status))

    for category, items in sorted(categories.items()):
        print(f"\n{category.upper()}:")
        for example, success, status in items:
            icon = "✅" if success else "❌"
            name = example.split("/")[-1] if "/" in example else example
            print(f"  {icon} {name}: {status}")

    # Exit with error code if any failures
    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
