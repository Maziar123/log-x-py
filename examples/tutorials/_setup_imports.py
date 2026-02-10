"""
Helper module to set up imports for tutorial scripts.
This handles the sys.path manipulation to import logxpy from the parent directory.
"""
import sys
from pathlib import Path

# Add logxpy to path
logxpy_path = str(Path(__file__).parent.parent / "logxpy")
if logxpy_path not in sys.path:
    sys.path.insert(0, logxpy_path)

# Now import and expose the needed components
try:
    import logxpy
    from logxpy import log, to_file, start_action, write_traceback
    __all__ = ['log', 'to_file', 'start_action', 'write_traceback', 'logxpy']
except ImportError as e:
    # If logxpy isn't available, provide a helpful error message
    print(f"Error importing logxpy: {e}")
    print("\nPlease ensure logxpy is available:")
    print(f"  PYTHONPATH should include: {logxpy_path}")
    raise
