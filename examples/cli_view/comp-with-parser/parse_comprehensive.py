#!/usr/bin/env python3
"""Line-by-line checker for example_09_comprehensive.py log files.

Uses the NEW logxy-log-parser simple API for one-line parsing and validation.

Usage: python parse_comprehensive.py [log_file_path]
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

# Add logxy-log-parser to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "logxy_log_parser"))

# ONE-LINE API: Import simple parsing functions
from logxy_log_parser import (
    parse_log,      # One line to parse
    check_log,      # One line to parse + validate
    analyze_log,    # One line to parse + validate + analyze
    LogXPyEntry,
    CheckResult,
)


def demo_one_line_parsing(log_path: Path) -> None:
    """Demonstrate the one-line parsing API."""
    print("=" * 60)
    print("🚀 ONE-LINE PARSING API DEMO")
    print("=" * 60)
    
    # METHOD 1: One line to parse
    print("\n1️⃣  parse_log() - Parse in one line:")
    print("-" * 40)
    result = parse_log(log_path)
    print(f"   Code: result = parse_log('{log_path.name}')")
    print(f"   Result: {result.parsed_count} entries parsed")
    print(f"   Skipped: {result.skipped_count} lines")
    
    # METHOD 2: One line to parse + validate
    print("\n2️⃣  check_log() - Parse + validate in one line:")
    print("-" * 40)
    checked = check_log(log_path)
    print(f"   Code: checked = check_log('{log_path.name}')")
    print(f"   Valid: {checked.is_valid}")
    print(f"   Entries: {len(checked)}")
    print(f"   Stats: {checked.stats.unique_tasks} tasks, depth {checked.stats.max_depth}")
    
    # METHOD 3: One line to parse + validate + analyze
    print("\n3️⃣  analyze_log() - Full analysis in one line:")
    print("-" * 40)
    report = analyze_log(log_path)
    print(f"   Code: report = analyze_log('{log_path.name}')")
    print(f"   Ready: {len(report.entries)} entries analyzed")
    print(f"   Errors found: {len(report.errors)}")


def detailed_check(log_path: Path) -> CheckResult:
    """Perform detailed line-by-line check using one-line API."""
    print("\n" + "=" * 60)
    print("🔍 DETAILED LINE-BY-LINE CHECK")
    print("=" * 60)
    print(f"\nFile: {log_path}")
    
    # ONE LINE: Parse and validate
    result = check_log(log_path)
    
    # Print statistics
    print(f"\n📊 PARSE STATISTICS")
    print("-" * 40)
    print(f"  Total lines:      {result.total_lines}")
    print(f"  Parsed entries:   {result.parsed_count}")
    print(f"  Skipped/invalid:  {result.skipped_count}")
    
    stats = result.stats
    print(f"\n📈 CONTENT STATISTICS")
    print("-" * 40)
    print(f"  Unique tasks:     {stats.unique_tasks}")
    print(f"  Max depth:        {stats.max_depth}")
    print(f"  With duration:    {stats.entries_with_duration}")
    print(f"  Total fields:     {stats.total_fields}")
    
    print(f"\n⚡ ACTION COUNTS")
    print("-" * 40)
    print(f"  Started:   {stats.actions_started}")
    print(f"  Succeeded: {stats.actions_succeeded}")
    print(f"  Failed:    {stats.actions_failed}")
    
    print(f"\n📋 LEVEL DISTRIBUTION")
    print("-" * 40)
    for level, count in sorted(stats.levels.items(), key=lambda x: -x[1]):
        if count > 0:
            bar = "█" * min(count // 2, 20)
            print(f"  {level:12}: {count:4} {bar}")
    
    print(f"\n🏷️  TOP ACTION TYPES")
    print("-" * 40)
    for action, count in sorted(stats.action_types.items(), key=lambda x: -x[1])[:5]:
        print(f"  {action:40} : {count}")
    
    # Color sections (each unique color = one section)
    print(f"\n🎨 COLOR SECTIONS")
    print("-" * 40)
    sections: dict[str, tuple[int, int, int]] = {}  # color -> (section_num, start, end)
    color_lines: dict[str, list[int]] = {}
    section_counter = 0
    seen_colors: set[str] = set()
    
    for e in result.entries:
        bg = e.fields.get("bg") or e.fields.get("logxpy:background")
        if bg:
            if bg not in seen_colors:
                section_counter += 1
                seen_colors.add(bg)
                sections[bg] = (section_counter, e.line_number, e.line_number)
                color_lines[bg] = [e.line_number]
            else:
                sections[bg] = (sections[bg][0], sections[bg][1], e.line_number)
                color_lines[bg].append(e.line_number)
    
    if sections:
        for color, (num, start, end) in sorted(sections.items(), key=lambda x: x[1][0]):
            count = len(color_lines[color])
            if start == end:
                print(f"  [{num}] {color:12}: line {start} ({count} entry)")
            else:
                print(f"  [{num}] {color:12}: lines {start}-{end} ({count} entries)")
    else:
        print("  No color blocks found")
    
    # Validation results
    print(f"\n✅ VALIDATION")
    print("-" * 40)
    if result.validation_errors:
        print(f"❌ Found {len(result.validation_errors)} issues:")
        for error in result.validation_errors[:10]:
            print(f"    - {error}")
        if len(result.validation_errors) > 10:
            print(f"    ... and {len(result.validation_errors) - 10} more")
    else:
        print("✓ All entries passed validation!")
    
    # Sample entries with line numbers
    print(f"\n🔍 SAMPLE ENTRIES")
    print("-" * 40)
    for i, entry in enumerate(result.entries[:3], 1):
        print(f"\n  [{i}] Line {entry.line_number} | {entry.task_uuid[:8]}... | Depth: {entry.depth}")
        if entry.action_type:
            status = entry.action_status.value if entry.action_status else "?"
            duration = f" ({entry.duration*1000:.3f}ms)" if entry.duration else ""
            print(f"      Action: {entry.action_type} [{status}]{duration}")
        else:
            print(f"      Message: {entry.message_type}")
            if entry.message:
                print(f"      Text: {entry.message[:50]}...")
        if entry.fields:
            keys = list(entry.fields.keys())[:3]
            print(f"      Fields: {', '.join(keys)}...")
    
    # Line number lookup demo
    print(f"\n📍 LINE NUMBER LOOKUP")
    print("-" * 40)
    
    # Create line number index
    line_index = {e.line_number: e for e in result.entries}
    print(f"   Total entries with line numbers: {len(line_index)}")
    
    # Check if specific line exists
    target_line = 5
    if target_line in line_index:
        entry = line_index[target_line]
        print(f"   ✓ Line {target_line}: {entry.message_type} - {entry.message[:40] if entry.message else 'N/A'}...")
    else:
        print(f"   ✗ Line {target_line}: Not found or empty line")
    
    # Find entry by line number
    def find_by_line(entries: list, line_num: int) -> LogXPyEntry | None:
        """Find entry by line number."""
        for entry in entries:
            if entry.line_number == line_num:
                return entry
        return None
    
    found = find_by_line(result.entries, 10)
    if found:
        print(f"   ✓ Line 10 found: {found.message_type}")
    
    # FIND ONE LINE - Rich single entry retrieval
    print(f"\n🔍 FIND ONE LINE (Rich Result)")
    print("-" * 40)
    
    # Build index once: {line_number: entry}
    idx = {e.line_number: e for e in result.entries}
    max_line = max(idx.keys()) if idx else 0
    
    # Example 1: Find existing line with rich details
    target = 5
    entry = idx.get(target)
    print(f"\n   🎯 Target Line: {target}")
    print(f"   {'─'*36}")
    if entry:
        print(f"   ✓ FOUND")
        print(f"   Line Number:  {entry.line_number}")
        print(f"   Task UUID:    {entry.task_uuid}")
        print(f"   Task Level:   {entry.task_level} (depth={entry.depth})")
        print(f"   Message Type: {entry.message_type}")
        print(f"   Message:      {entry.message or 'N/A'}")
        print(f"   Is Action:    {entry.is_action}")
        print(f"   Is Error:     {entry.is_error}")
        print(f"   Fields ({len(entry.fields)}):")
        for k, v in list(entry.fields.items())[:3]:
            print(f"      • {k}: {str(v)[:30]}")
    else:
        print(f"   ✗ NOT FOUND")
    
    # Example 2: One-liner find pattern
    print(f"\n   💡 ONE-LINER: entry = idx.get({target})")
    
    # Example 3: Find with default
    missing_line = 999
    entry_or_none = idx.get(missing_line)
    print(f"\n   🎯 Target Line: {missing_line} (should fail)")
    print(f"   Result: {'✓ Found' if entry_or_none else '✗ Not found (expected)'}")
    
    # 10 Random Line Checks (some exist, some fail)
    import random
    random.seed(42)  # Reproducible
    test_lines = [5, 50, 999, 3, 75, 1000, 25, 88, 200, 1]  # Mix: exist + fail
    
    print(f"\n📋 10 RANDOM LINE CHECKS (Mix of exist/fail)")
    print("-" * 40)
    for i, n in enumerate(test_lines, 1):
        exists = n in idx
        status = "✓" if exists else "✗ FAIL"
        entry_type = idx[n].message_type if exists else "N/A"
        print(f"   {i:2d}. Line {n:3d}: {status:8s} type={entry_type}")
    
    return result


def print_usage_examples() -> None:
    """Print usage examples for the simple API."""
    print("\n" + "=" * 60)
    print("📖 USAGE EXAMPLES")
    print("=" * 60)
    print("""
# Import the simple one-line API
from logxy_log_parser import parse_log, check_log, analyze_log

# 1. ONE LINE - Parse a log file
entries = parse_log("app.log")
print(f"Parsed {len(entries)} entries")

# 2. ONE LINE - Parse with validation
result = check_log("app.log")
if result.is_valid:
    print(f"All {len(result)} entries valid")
else:
    print(f"Found {len(result.validation_errors)} errors")

# 3. ONE LINE - Parse + validate + analyze
report = analyze_log("app.log")
report.print_summary()

# 4. Access statistics
result = check_log("app.log")
print(f"Tasks: {result.stats.unique_tasks}")
print(f"Max depth: {result.stats.max_depth}")
print(f"Errors: {result.stats.error_count}")

# 5. Iterate over entries
for entry in parse_log("app.log"):
    if entry.is_error:
        print(f"ERROR: {entry.message}")

# 6. Filter by level
result = check_log("app.log")
errors = [e for e in result.entries if e.is_error]

# 7. Get slow actions
report = analyze_log("app.log")
for action, duration in report.slowest_actions[:5]:
    print(f"{action}: {duration*1000:.2f}ms")

# 8. Find entry by line number
result = check_log("app.log")
for entry in result.entries:
    if entry.line_number == 42:
        print(f"Line 42: {entry.message}")

# 9. Check if line exists
result = parse_log("app.log")
line_numbers = {e.line_number for e in result.entries}
if 100 in line_numbers:
    print("Line 100 exists in log")
""")


def main() -> int:
    """Main entry point."""
    # Get log file path
    if len(sys.argv) > 1:
        log_path = Path(sys.argv[1])
    else:
        log_path = Path(__file__).parent.parent / "complete-example-01" / "example_09_comprehensive.log"
    
    if not log_path.exists():
        print(f"❌ Log file not found: {log_path}")
        print(f"   Run: cd ../complete-example-01 && python example_09_comprehensive.py")
        return 1
    
    # Run demos
    demo_one_line_parsing(log_path)
    result = detailed_check(log_path)
    print_usage_examples()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    print(f"""
Parsed file: {log_path.name}
Total entries: {len(result)}
Valid: {result.is_valid}

The logxy-log-parser simple API provides:
  • parse_log()   - One line to parse
  • check_log()   - One line to parse + validate  
  • analyze_log() - One line to parse + validate + analyze

Each function returns rich objects with full access to:
  • All log entries
  • Statistics (tasks, depth, levels, actions)
  • Validation results
  • Raw data for custom analysis
""")
    
    return 0 if result.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
