#!/usr/bin/env python3
"""Run all examples and verify log output."""
import json
import subprocess
import sys
from pathlib import Path

EXAMPLES_DIR = Path("logxpy/examples")
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
    "xx_Color_Methods1.py",
]

def patch_example_to_use_logfile(example_path: Path) -> None:
    """Patch example to write to log file instead of stdout."""
    content = example_path.read_text()
    original = content

    # Skip if already patched or uses special patterns
    if "LOG_FILE = " in content or example_path.name in ["xx_Color_Methods1.py"]:
        return

    # Find the to_file or log.configure line and patch it
    lines = content.split('\n')
    new_lines = []
    patched = False

    for i, line in enumerate(lines):
        new_lines.append(line)

        # After imports, add log file setup
        if not patched and line.strip() and not line.startswith('#') and line.startswith('from ') or line.startswith('import '):
            continue
        if not patched and ('def main()' in line or 'if __name__' in line):
            # Insert before main or before if __name__
            log_file_name = example_path.stem + ".log"
            new_lines.pop()  # Remove the line we just added
            new_lines.append(f'\n# Setup log file output')
            new_lines.append(f'LOG_FILE = Path(__file__).with_suffix(".log")')
            new_lines.append(f'to_file(open(LOG_FILE, "w"))')
            new_lines.append('')
            new_lines.append(line)  # Add back main/if line
            patched = True

    if patched:
        example_path.write_text('\n'.join(new_lines))
        print(f"  Patched {example_path.name}")

def run_example(example_name: str) -> tuple[bool, str]:
    """Run an example and return success status and output."""
    example_path = EXAMPLES_DIR / example_name
    log_path = EXAMPLES_DIR / (example_path.stem + ".log")

    # Delete old log if exists
    if log_path.exists():
        log_path.unlink()

    # Run the example
    result = subprocess.run(
        [sys.executable, str(example_path)],
        capture_output=True,
        text=True,
        cwd="logxpy"
    )

    if result.returncode != 0:
        return False, result.stderr

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
        "invalid": invalid
    }

def main():
    print("=" * 60)
    print("Running LogXPy Examples and Verifying Logs")
    print("=" * 60)

    results = []

    for example in EXAMPLES:
        example_path = EXAMPLES_DIR / example
        log_path = EXAMPLES_DIR / (example_path.stem + ".log")

        print(f"\n{example}:")

        # Patch example to use log file
        patch_example_to_use_logfile(example_path)

        # Run example
        success, output = run_example(example)

        if not success:
            print(f"  ❌ Failed: {output}")
            results.append((example, False, "Execution failed"))
            continue

        # Verify log file
        verify = verify_log_file(log_path)

        if not verify["exists"]:
            print(f"  ⚠ No log file created")
            results.append((example, True, "No log file"))
            continue

        if verify["invalid"]:
            print(f"  ❌ Log has {len(verify['invalid'])} invalid JSON lines")
            for err in verify["invalid"][:3]:
                print(f"     {err}")
            results.append((example, True, f"Invalid JSON: {verify['valid']}/{verify['lines']}"))
        else:
            print(f"  ✅ {verify['valid']} valid JSON lines")
            results.append((example, True, f"{verify['valid']} lines"))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    print(f"\nPassed: {passed}/{total}")

    for example, success, status in results:
        icon = "✅" if success else "❌"
        print(f"  {icon} {example}: {status}")

if __name__ == "__main__":
    main()
