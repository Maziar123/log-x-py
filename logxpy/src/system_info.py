"""System information logging - CodeSite-compatible with lazy imports.

All functions use lazy imports to avoid errors when optional dependencies
are not installed. No ImportError is raised - features gracefully degrade.
"""

from __future__ import annotations

import sys
import warnings
from typing import Any, TYPE_CHECKING

from .logx import log

if TYPE_CHECKING:
    from types import ModuleType


def _lazy_import(module_name: str, package: str | None = None) -> ModuleType | None:
    """Lazy import with silent fallback.
    
    Returns None if module not found, no error raised.
    """
    try:
        return __import__(module_name, fromlist=[""])
    except ImportError:
        return None


def send_system_info(msg: str = "System Info") -> None:
    """Send system information (CodeSite SendSystemInfo equivalent).
    
    Uses platform module (stdlib) - always available.
    
    Args:
        msg: Message prefix
    """
    platform = _lazy_import("platform")
    if platform is None:
        log.warning("platform module not available")
        return
    
    info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "node": platform.node(),
    }
    log.send(msg, info)


def send_memory_status(msg: str = "Memory Status") -> None:
    """Send memory status (CodeSite SendMemoryStatus equivalent).
    
    Uses psutil if available, otherwise basic info from sys.
    
    Args:
        msg: Message prefix
    """
    psutil = _lazy_import("psutil")
    
    if psutil:
        mem = psutil.virtual_memory()
        info = {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "free": mem.free,
            "percent": mem.percent,
            "_source": "psutil",
        }
    else:
        # Fallback to basic Python info
        import sys
        info = {
            "_warning": "psutil not installed: pip install psutil",
            "_fallback": "sys info only",
        }
        # Try to get some basic info
        try:
            import resource
            usage = resource.getrusage(resource.RUSAGE_SELF)
            info["max_rss"] = usage.ru_maxrss  # Max resident set size
        except ImportError:
            pass  # Windows doesn't have resource module
    
    log.send(msg, info)


def send_heap_status(msg: str = "Heap/GC Status") -> None:
    """Send Python heap/GC status (CodeSite SendHeapStatus equivalent).
    
    Python uses garbage collection unlike Delphi's heap.
    
    Args:
        msg: Message prefix
    """
    import gc
    
    gc_counts = gc.get_count()
    thresholds = gc.get_threshold()
    
    info = {
        "gc_counts": {
            "generation_0": gc_counts[0],
            "generation_1": gc_counts[1], 
            "generation_2": gc_counts[2],
        },
        "thresholds": {
            "generation_0": thresholds[0],
            "generation_1": thresholds[1],
            "generation_2": thresholds[2],
        },
        "is_enabled": gc.isenabled(),
        "objects_tracked": len(gc.get_objects()),
        "_note": "Python uses garbage collection, not manual heap",
    }
    
    log.send(msg, info)


def send_memory_manager_status(msg: str = "Memory Manager") -> None:
    """Send memory manager status (CodeSite SendMemoryManagerStatus equivalent).
    
    Uses tracemalloc if available (Python 3.4+), otherwise sys info.
    
    Args:
        msg: Message prefix
    """
    tracemalloc = _lazy_import("tracemalloc")
    
    info: dict[str, Any] = {
        "_note": "Python memory management differs from Delphi",
    }
    
    if tracemalloc:
        # Try to get current memory usage
        try:
            current, peak = tracemalloc.get_traced_memory()
            info["current_bytes"] = current
            info["peak_bytes"] = peak
            info["tracemalloc_tracing"] = True
        except Exception:
            info["tracemalloc_tracing"] = False
            info["_tip"] = "Use tracemalloc.start() to begin tracing"
    else:
        info["_warning"] = "tracemalloc not available (Python 3.4+ required)"
    
    # Add object counts by type (basic)
    try:
        import gc
        by_type: dict[str, int] = {}
        for obj in gc.get_objects():
            typename = type(obj).__name__
            by_type[typename] = by_type.get(typename, 0) + 1
        # Top 10 most common
        top_types = sorted(by_type.items(), key=lambda x: x[1], reverse=True)[:10]
        info["top_object_types"] = {k: v for k, v in top_types}
    except Exception:
        pass
    
    log.send(msg, info)


def send_memory_as_hex(data: bytes, msg: str = "Memory Hex", max_size: int = 256) -> None:
    """Send memory/bytes as hex dump (CodeSite SendMemoryAsHex equivalent).
    
    Args:
        data: Bytes to dump
        msg: Message prefix
        max_size: Maximum bytes to dump
    """
    if not isinstance(data, bytes):
        log.warning("send_memory_as_hex requires bytes, got", type=type(data).__name__)
        return
    
    truncated = len(data) > max_size
    display_data = data[:max_size]
    
    # Format as hex dump with offset
    hex_lines = []
    for i in range(0, len(display_data), 16):
        chunk = display_data[i:i+16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        hex_lines.append(f"{i:04x}: {hex_part:<48} {ascii_part}")
    
    info = {
        "total_size": len(data),
        "dumped_size": len(display_data),
        "truncated": truncated,
        "hex_dump": "\n".join(hex_lines),
        "hex_string": display_data.hex(),
    }
    
    log.send(msg, info)


def send_stack_trace(msg: str = "Stack Trace", limit: int = 10) -> None:
    """Send current stack trace (CodeSite SendStackTrace equivalent).
    
    Args:
        msg: Message prefix
        limit: Maximum stack frames to include
    """
    import traceback
    
    stack = traceback.format_stack(limit=limit)
    
    info = {
        "stack_frames": len(stack),
        "trace": "".join(stack),
        "trace_list": [line.strip() for line in stack if line.strip()],
    }
    
    log.send(msg, info)


def send_exception_trace(msg: str = "Exception Trace") -> None:
    """Send exception traceback if in except block."""
    import sys
    import traceback
    
    exc_info = sys.exc_info()
    if exc_info[0] is None:
        log.send(msg, {"_note": "No active exception"})
        return
    
    tb_str = "".join(traceback.format_exception(*exc_info))
    info = {
        "exception_type": exc_info[0].__name__ if exc_info[0] else None,
        "exception": str(exc_info[1]),
        "traceback": tb_str,
    }
    log.send(msg, info)


# GUI-related functions - toolkit dependent
def send_window_handle(window=None, msg: str = "Window Handle") -> None:
    """Send window handle info (CodeSite SendWindowHandle equivalent).
    
    Args:
        window: Window object (tkinter, Qt, etc). If None, tries to detect.
        msg: Message prefix
    """
    info: dict[str, Any] = {
        "_note": "GUI toolkit dependent",
        "provided_window": window is not None,
    }
    
    if window is None:
        # Try to detect current GUI framework
        tkinter = _lazy_import("tkinter")
        if tkinter:
            try:
                info["tkinter_windows"] = len(tkinter.Tcl().call("winfo", "children", "."))
            except Exception as e:
                info["tkinter_error"] = str(e)
        
        # Try Qt
        PyQt5 = _lazy_import("PyQt5.QtWidgets")
        PyQt6 = _lazy_import("PyQt6.QtWidgets")
        PySide2 = _lazy_import("PySide2.QtWidgets")
        PySide6 = _lazy_import("PySide6.QtWidgets")
        
        qt_module = PyQt5 or PyQt6 or PySide2 or PySide6
        if qt_module:
            try:
                app = qt_module.QApplication.instance()
                if app:
                    info["qt_top_level_windows"] = len(app.topLevelWidgets())
            except Exception as e:
                info["qt_error"] = str(e)
    else:
        # Analyze provided window
        info["window_type"] = type(window).__name__
        info["window_module"] = type(window).__module__
        
        # Try to get common attributes
        for attr in ["winfo_id", "winId", "handle", "hwnd"]:
            if hasattr(window, attr):
                try:
                    val = getattr(window, attr)
                    if callable(val):
                        val = val()
                    info[f"handle_{attr}"] = str(val)
                except Exception as e:
                    info[f"handle_{attr}_error"] = str(e)
    
    log.send(msg, info)


def send_screenshot(msg: str = "Screenshot", save_path: str | None = None) -> None:
    """Send screenshot info (CodeSite SendScreenshot equivalent).
    
    Uses PIL/Pillow if available. Does not fail if not installed.
    
    Args:
        msg: Message prefix
        save_path: Optional path to save screenshot
    """
    PIL = _lazy_import("PIL")
    
    if PIL is None:
        log.send(msg, {
            "_error": "PIL/Pillow not installed",
            "_install": "pip install Pillow",
        })
        return
    
    try:
        from PIL import ImageGrab
        
        img = ImageGrab.grab()
        info = {
            "size": img.size,
            "mode": img.mode,
            "format": img.format,
        }
        
        if save_path:
            img.save(save_path)
            info["saved_to"] = save_path
        
        # Add thumbnail info (small base64)
        import io
        import base64
        thumb = img.copy()
        thumb.thumbnail((64, 64))
        buf = io.BytesIO()
        thumb.save(buf, format="PNG")
        info["thumbnail_b64"] = base64.b64encode(buf.getvalue()).decode()[:100] + "..."
        
        log.send(msg, info)
        
    except Exception as e:
        log.send(msg, {"_error": str(e)})


def send_parents(obj, msg: str = "Parent Hierarchy") -> None:
    """Send parent hierarchy (CodeSite SendParents equivalent).
    
    Works with GUI widgets or any object with __parent__ or parent() attributes.
    
    Args:
        obj: Object to trace parents of
        msg: Message prefix
    """
    if obj is None:
        log.send(msg, {"_error": "Object is None"})
        return
    
    parents = []
    current = obj
    max_depth = 20
    depth = 0
    
    while current and depth < max_depth:
        info = {
            "type": type(current).__name__,
            "module": type(current).__module__,
            "repr": repr(current)[:100],
        }
        parents.append(info)
        
        # Try to get parent
        parent = None
        for attr in ["parent", "_parent", "__parent__", "master"]:
            if hasattr(current, attr):
                try:
                    val = getattr(current, attr)
                    if callable(val):
                        val = val()
                    if val is not None and val is not current:
                        parent = val
                        break
                except Exception:
                    pass
        
        current = parent
        depth += 1
    
    log.send(msg, {
        "hierarchy_depth": len(parents),
        "parents": parents,
        "truncated": depth >= max_depth,
    })


# Aliases for CodeSite compatibility
SendSystemInfo = send_system_info
SendMemoryStatus = send_memory_status
SendHeapStatus = send_heap_status
SendMemoryManagerStatus = send_memory_manager_status
SendMemoryAsHex = send_memory_as_hex
SendStackTrace = send_stack_trace
SendWindowHandle = send_window_handle
SendScreenshot = send_screenshot
SendParents = send_parents

# Also add to Logger class
from . import logx

# Monkey-patch Logger class for fluent API
logx.Logger.send_system_info = lambda self, msg="System Info": (send_system_info(msg), self)[1]
logx.Logger.send_memory_status = lambda self, msg="Memory Status": (send_memory_status(msg), self)[1]
logx.Logger.send_heap_status = lambda self, msg="Heap/GC Status": (send_heap_status(msg), self)[1]
logx.Logger.send_memory_manager_status = lambda self, msg="Memory Manager": (send_memory_manager_status(msg), self)[1]
logx.Logger.send_memory_as_hex = lambda self, data, msg="Memory Hex", max_size=256: (send_memory_as_hex(data, msg, max_size), self)[1]
logx.Logger.send_stack_trace = lambda self, msg="Stack Trace", limit=10: (send_stack_trace(msg, limit), self)[1]
logx.Logger.send_window_handle = lambda self, window=None, msg="Window Handle": (send_window_handle(window, msg), self)[1]
logx.Logger.send_screenshot = lambda self, msg="Screenshot", save_path=None: (send_screenshot(msg, save_path), self)[1]
logx.Logger.send_parents = lambda self, obj, msg="Parent Hierarchy": (send_parents(obj, msg), self)[1]

__all__ = [
    "send_system_info",
    "send_memory_status",
    "send_heap_status",
    "send_memory_manager_status",
    "send_memory_as_hex",
    "send_stack_trace",
    "send_exception_trace",
    "send_window_handle",
    "send_screenshot",
    "send_parents",
    # CodeSite-style aliases
    "SendSystemInfo",
    "SendMemoryStatus",
    "SendHeapStatus",
    "SendMemoryManagerStatus",
    "SendMemoryAsHex",
    "SendStackTrace",
    "SendWindowHandle",
    "SendScreenshot",
    "SendParents",
]
