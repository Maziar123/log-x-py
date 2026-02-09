#!/usr/bin/env python3
"""
Run All Tutorial Examples
==========================

This script runs all tutorial examples and displays viewing instructions.
"""

import subprocess
import sys
from pathlib import Path


def run_tutorial(script_name: str, description: str):
    """Run a single tutorial script."""
    script_path = Path(__file__).parent / script_name
    
    print("\n" + "=" * 80)
    print(f"Running: {description}")
    print("=" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=False
        )
        print(f"✓ {script_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {script_name} failed with error code {e.returncode}")
        return False


def main():
    """Run all tutorials."""
    tutorials = [
        ("tutorial_01_basic_logging.py", "Tutorial 01: Basic Logging"),
        ("tutorial_02_actions_and_context.py", "Tutorial 02: Actions and Context"),
        ("tutorial_03_decorators.py", "Tutorial 03: Decorators"),
        ("tutorial_04_error_handling.py", "Tutorial 04: Error Handling"),
        ("tutorial_05_real_world_api.py", "Tutorial 05: Real-World API Scenario"),
    ]
    
    print("\n" + "=" * 80)
    print("LogXPY Tutorial Suite")
    print("=" * 80)
    print(f"Running {len(tutorials)} tutorials...")
    
    results = []
    for script, description in tutorials:
        success = run_tutorial(script, description)
        results.append((script, success))
    
    # Summary
    print("\n" + "=" * 80)
    print("Tutorial Execution Summary")
    print("=" * 80)
    
    for script, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status}: {script}")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nTotal: {successful}/{total} tutorials completed successfully")
    
    if successful == total:
        print("\n" + "=" * 80)
        print("All tutorials completed! View the logs:")
        print("=" * 80)
        
        log_files = [
            ("tutorial_01_basic.log", "Basic logging examples"),
            ("tutorial_02_actions.log", "Actions and nested operations"),
            ("tutorial_03_decorators.log", "Decorator examples"),
            ("tutorial_04_errors.log", "Error handling patterns"),
            ("tutorial_05_api.log", "Real-world API scenario"),
        ]
        
        print("\nView individual logs:")
        for log_file, desc in log_files:
            print(f"  logxpy-view {log_file}  # {desc}")
        
        print("\nView all logs together:")
        print("  logxpy-view tutorial_*.log")
        
        print("\nView with filtering:")
        print("  logxpy-view --action-status failed tutorial_*.log")
        print("  logxpy-view --keyword 'error' tutorial_*.log")
        print("  logxpy-view --select 'level == `ERROR`' tutorial_*.log")

        print("\nExport to HTML:")
        print("  logxpy-view export tutorial_*.log -f html -o all_tutorials.html")

        print("\nShow statistics:")
        print("  logxpy-view stats tutorial_*.log")
        
        print("\n" + "=" * 80)
    
    return 0 if successful == total else 1


if __name__ == "__main__":
    sys.exit(main())
