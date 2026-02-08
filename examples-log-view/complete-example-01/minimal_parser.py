#!/usr/bin/env python3
"""Minimal parser - shows categories from log entries."""
import json
import sys
from pathlib import Path
from collections import Counter

log_path = Path(sys.argv[1] if len(sys.argv) > 1 else "minimal_color.log")
if not log_path.exists():
    print(f"✗ File not found: {log_path}")
    sys.exit(1)

entries = []
categories = Counter()
colored = 0

for line in open(log_path):
    entry = json.loads(line.strip())
    entries.append(entry)
    
    # Detect category by message content
    msg = entry.get("message", "")
    action_type = entry.get("action_type", "")
    msg_type = entry.get("message_type", "")
    
    if msg == "System Info":
        categories["System Info"] += 1
    elif msg == "Memory Status":
        categories["Memory"] += 1
    elif "Color" in msg:
        categories["Data Types"] += 1
    elif "Time" in msg or msg == "CurrentTime":
        categories["Data Types"] += 1
    elif "Enum" in msg or "Status" in msg:
        categories["Data Types"] += 1
    elif "Price" in msg or "currency" in msg_type.lower():
        categories["Data Types"] += 1
    elif "📍" in msg or "checkpoint" in msg_type.lower():
        categories["Checkpoints"] += 1
    elif "Stack Trace" in msg or "stack_trace" in msg_type.lower():
        categories["Error Handling"] += 1
    elif action_type:
        categories["Actions"] += 1
    else:
        categories["Messages"] += 1
    
    if entry.get("logxpy:foreground") or entry.get("logxpy:background"):
        colored += 1

print(f"✓ Parsed: {len(entries)} entries, {colored} colored")
print(f"  Categories: {dict(categories)}")
print("")
print("  Preview (first 10):")
for i, e in enumerate(entries[:10], 1):
    fg = e.get("logxpy:foreground", "-")
    bg = e.get("logxpy:background", "-")
    msg = e.get("message", "")[:25]
    action = e.get("action_type", "")
    status = e.get("action_status", "")
    
    if action:
        display = f"[{status or 'msg'}] {action[:20]}"
    else:
        display = msg
    
    marker = "🎨" if fg != "-" or bg != "-" else "  "
    print(f"  {marker} [{i:2}] {fg:10} {bg:10} | {display}")

if len(entries) > 10:
    print(f"  ... and {len(entries) - 10} more entries")
