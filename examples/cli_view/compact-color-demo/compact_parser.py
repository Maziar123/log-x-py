#!/usr/bin/env python3
"""Compact log parser - show color sections using logxy-log-parser simple API.

Usage: python compact_parser.py [log_file_path]
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add logxy_log_parser to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "logxy_log_parser"))

from logxy_log_parser import check_log


def main() -> int:
    """Parse log and show color sections (same color = same section)."""
    log_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("compact_color.log")
    
    if not log_path.exists():
        print(f"Error: {log_path} not found")
        return 1
    
    # One-line parse + validate
    result = check_log(log_path)
    stats = result.stats
    
    print(f"Entries: {len(result)} | Tasks: {stats.unique_tasks} | Max depth: {stats.max_depth}")
    print(f"Actions: started={stats.actions_started}, succeeded={stats.actions_succeeded}, failed={stats.actions_failed}")
    
    # Track color sections by color name
    # Each unique color gets one section (first occurrence to last occurrence)
    sections: dict[str, tuple[int, int, int]] = {}  # color -> (section_num, start_line, end_line)
    color_lines: dict[str, list[int]] = {}  # color -> [line_numbers]
    section_counter = 0
    seen_colors: set[str] = set()
    
    for e in result.entries:
        bg = e.fields.get("logxpy:background")
        line_num = e.line_number
        
        if bg:
            # First time seeing this color = new section
            if bg not in seen_colors:
                section_counter += 1
                seen_colors.add(bg)
                sections[bg] = (section_counter, line_num, line_num)
                color_lines[bg] = [line_num]
            else:
                # Same color - extend section end
                sections[bg] = (sections[bg][0], sections[bg][1], line_num)
                color_lines[bg].append(line_num)
    
    if sections:
        # Sort by section number
        sorted_sections = sorted(sections.items(), key=lambda x: x[1][0])
        print("\nColor sections:")
        for color, (num, start, end) in sorted_sections:
            count = len(color_lines[color])
            if start == end:
                print(f"  [{num}] {color}: line {start} ({count} entry)")
            else:
                print(f"  [{num}] {color}: lines {start}-{end} ({count} entries)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
