"""15_task_id_modes.py - Demonstrating Task ID Modes

Shows the two task ID formats:
- sqid: Short hierarchical IDs (4-12 chars, default)
- uuid: Standard UUID4 (36 chars, distributed-safe)

Use sqid for single-process logging (shorter, readable).
Use uuid for distributed tracing across multiple processes/machines.
"""

import json
import os
from logxpy import log


def demo_sqid_mode():
    """SQID mode: Short hierarchical task IDs."""
    print("\n" + "="*60)
    print("SQID MODE (Default - Short Hierarchical IDs)")
    print("="*60)
    
    log_file = "/tmp/demo_sqid.log"
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # SQID mode: Short IDs like "Xa.1", "Xa.1.1", "Xa.2"
    log.init(log_file, task_id_mode="sqid", async_en=False, clean=True)
    
    log.info("Root task - level 1")
    log.info("Child task - level 2")
    log.info("Grandchild - level 3")
    log.info("Back to level 1")
    
    # Read and display
    print("\nLog entries:")
    with open(log_file) as f:
        for line in f:
            entry = json.loads(line.strip())
            tid = entry["tid"]
            msg = entry["msg"]
            lvl = entry["lvl"]
            print(f"  tid={tid:<12} lvl={lvl}  {msg}")
    
    print(f"\nCharacteristics:")
    print(f"  • Length: 4-12 characters")
    print(f"  • Format: PID_PREFIX.COUNTER[.CHILD_INDEX]")
    print(f"  • Human readable: Shows hierarchy in ID")
    print(f"  • Best for: Single-process applications")
    
    os.remove(log_file)


def demo_uuid_mode():
    """UUID mode: Standard UUID4 task IDs."""
    print("\n" + "="*60)
    print("UUID MODE (Standard UUID4)")
    print("="*60)
    
    log_file = "/tmp/demo_uuid.log"
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # UUID mode: Standard UUID4 format
    log.init(log_file, task_id_mode="uuid", async_en=False, clean=True)
    
    log.info("Task 1")
    log.info("Task 2")
    log.info("Task 3")
    
    # Read and display
    print("\nLog entries (truncated):")
    with open(log_file) as f:
        for line in f:
            entry = json.loads(line.strip())
            tid = entry["tid"]
            msg = entry["msg"]
            # Show truncated UUID
            tid_short = tid[:8] + "..." + tid[-4:]
            print(f"  tid={tid_short}  {msg}")
    
    print(f"\nCharacteristics:")
    print(f"  • Length: 36 characters")
    print(f"  • Format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx")
    print(f"  • Globally unique: Safe across distributed systems")
    print(f"  • Best for: Multi-process, multi-machine tracing")
    
    os.remove(log_file)


def demo_comparison():
    """Compare ID formats side by side."""
    print("\n" + "="*60)
    print("SIDE-BY-SIDE COMPARISON")
    print("="*60)
    
    print("\nSame log output, different ID formats:")
    print("\nSQID format:")
    print("  Xa.1       (4 chars)")
    print("  Xa.1.1     (6 chars)")  
    print("  Xa.1.1.2   (8 chars)")
    print("  Xa.2       (4 chars)")
    
    print("\nUUID format:")
    print("  59b00749-eb24-4c5b...  (36 chars)")
    print("  7a8f9c2d-3e4b-5f6a...  (36 chars)")
    print("  9c1b2d3e-4f5a-6b7c...  (36 chars)")
    
    print("\nSize comparison for 1 million logs:")
    print("  SQID:  ~8 MB overhead")
    print("  UUID:  ~36 MB overhead")
    print("  Savings: 28 MB (78% smaller)")


def demo_environment_variable():
    """Show distributed mode via environment variable."""
    print("\n" + "="*60)
    print("DISTRIBUTED MODE (Environment Variable)")
    print("="*60)
    
    print("\nTo force UUID mode for distributed systems:")
    print('  export LOGXPY_DISTRIBUTED=1')
    print()
    print("Or in Python:")
    print('  import os')
    print('  os.environ["LOGXPY_DISTRIBUTED"] = "1"')
    print('  from logxpy import log')
    print('  log.init("app.log")  # Will use UUID mode')


def main():
    print("="*60)
    print("TASK ID MODES DEMONSTRATION")
    print("="*60)
    print("\nThis example shows the two task ID formats:")
    print("  1. sqid - Short hierarchical IDs (default)")
    print("  2. uuid - Standard UUID4 (distributed)")
    
    demo_sqid_mode()
    demo_uuid_mode()
    demo_comparison()
    demo_environment_variable()
    
    print("\n" + "="*60)
    print("Recommendation:")
    print("  • Use sqid (default) for single-process apps")
    print("  • Use uuid for distributed/multi-process apps")
    print("="*60)


if __name__ == "__main__":
    main()
