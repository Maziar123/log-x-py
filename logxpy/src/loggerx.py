"""Main Logger facade - LoggerX API.

LoggerX provides a modern, fluent API for structured logging.
Part of the logxpy library - a fork of Eliot.
"""

from __future__ import annotations

import traceback
from contextlib import contextmanager
from typing import Any

from . import decorators
from ._action import current_action
from ._async import _emit, current_scope, scope
from ._base import now, uuid
from ._fmt import format_value
from ._output import to_file
from ._types import Level, Record


class Logger:
    """LoggerX-compatible logger with fluent API."""

    __slots__ = ("_context", "_initialized", "_level", "_masker", "_name", "_auto_log_file")

    def __init__(self, name: str = "root", context: dict[str, Any] | None = None):
        self._level = Level.DEBUG
        self._name = name
        self._context = context or {}
        self._masker = None
        self._auto_log_file = None
        self._initialized = False

    # === Level Methods (fluent - return self) ===
    def debug(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.DEBUG, msg, **f)

    def info(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.INFO, msg, **f)

    def success(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.SUCCESS, msg, **f)

    def note(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.NOTE, msg, **f)

    def warning(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.WARNING, msg, **f)

    def error(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.ERROR, msg, **f)

    def critical(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.CRITICAL, msg, **f)

    def checkpoint(self, msg: str, **f: Any) -> Logger:
        return self._log(Level.INFO, f"📍 {msg}", **f)

    def exception(self, msg: str, **f: Any) -> Logger:
        f["logxpy:traceback"] = traceback.format_exc()
        return self._log(Level.ERROR, msg, **f)

    def __call__(self, first: Any = None, second: Any = None, **f: Any) -> Logger:
        """Flexible shortcut:
        - log("msg") == log.info("msg")
        - log("title", data) == log.send("title", data)
        - log(data) == log.send("Data", data)  # auto-title
        """
        if first is None:
            return self
        
        # log("title", data) or log("title", **fields)
        if second is not None:
            # If second is a simple type, treat as log.info with extra field
            if isinstance(second, (str, int, float, bool)):
                return self.info(str(first), value=second, **f)
            # Otherwise treat as send
            return self.send(str(first), second, **f)
        
        # log("message") - simple string message
        if isinstance(first, str):
            return self.info(first, **f)
        
        # log(data) - auto-title based on type
        title = f"Data:{type(first).__name__}"
        return self.send(title, first, **f)

    # === Universal Send ===
    def send(self, msg: str, data: Any, **f: Any) -> Logger:
        return self._log(Level.INFO, msg, data=format_value(data), **f)

    # === Type Methods ===
    def df(self, data: Any, title: str | None = None, **opts: Any) -> Logger:
        return self.send(title or "DataFrame", data, **opts)

    def tensor(self, data: Any, title: str | None = None) -> Logger:
        return self.send(title or "Tensor", data)

    def json(self, data: dict, title: str | None = None) -> Logger:
        import json as _json

        return self._log(Level.INFO, title or "JSON", content=_json.dumps(data, indent=2, default=str)[:5000])

    def img(self, data: Any, title: str | None = None, **opts: Any) -> Logger:
        return self.send(title or "Image", data, **opts)

    def plot(self, fig: Any, title: str | None = None) -> Logger:
        return self.send(title or "Plot", fig)  # Basic support via repr/str for now

    def tree(self, data: Any, title: str | None = None) -> Logger:
        return self.send(title or "Tree", data)  # Basic support

    def table(self, data: list[dict], title: str | None = None) -> Logger:
        return self.send(title or "Table", data)  # Basic support

    # === Data Type Methods (Clean API - no 'send_' prefix) ===
    def color(self, value: Any, title: str | None = None, as_hex: bool = True) -> Logger:
        """Log color value with RGB/hex formatting."""
        info: dict[str, Any] = {"original_type": type(value).__name__}
        if isinstance(value, (tuple, list)) and len(value) >= 3:
            r, g, b = int(value[0]), int(value[1]), int(value[2])
            a = int(value[3]) if len(value) > 3 else None
            info["rgb"] = {"r": r, "g": g, "b": b}
            if a is not None:
                info["rgba"] = {"r": r, "g": g, "b": b, "a": a}
            info["hex"] = f"#{r:02x}{g:02x}{b:02x}"
        elif isinstance(value, int):
            r, g, b = (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF
            info["rgb"] = {"r": r, "g": g, "b": b}
            info["hex"] = f"#{r:02x}{g:02x}{b:02x}"
        elif isinstance(value, str) and value.startswith('#'):
            info["hex"] = value.lower()
            try:
                h = value.lstrip('#')
                if len(h) == 6:
                    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
                    info["rgb"] = {"r": r, "g": g, "b": b}
            except ValueError:
                pass
        else:
            info["value"] = repr(value)
        return self.send(title or "Color", info)

    def currency(self, value: Any, currency_code: str = "USD", title: str | None = None) -> Logger:
        """Log currency value with proper precision."""
        from decimal import Decimal
        dec_value = Decimal(str(value)) if not isinstance(value, Decimal) else value
        info = {
            "amount": str(dec_value),
            "amount_float": float(dec_value),
            "currency": currency_code.upper(),
            "formatted": f"{currency_code.upper()} {dec_value}",
        }
        return self.send(title or "Currency", info)

    def datetime(self, dt: Any = None, title: str | None = None) -> Logger:
        """Log datetime with multiple formats."""
        import datetime as _dt
        if dt is None:
            dt = _dt.datetime.now()
        elif isinstance(dt, (int, float)):
            dt = _dt.datetime.fromtimestamp(dt)
        elif isinstance(dt, str):
            dt = _dt.datetime.fromisoformat(dt.replace('Z', '+00:00'))
        
        info = {
            "iso": dt.isoformat(),
            "timestamp": dt.timestamp(),
            "year": dt.year, "month": dt.month, "day": dt.day,
            "hour": dt.hour, "minute": dt.minute, "second": dt.second,
            "microsecond": dt.microsecond,
            "timezone": str(dt.tzinfo) if dt.tzinfo else None,
            "formatted": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M:%S"),
        }
        return self.send(title or "DateTime", info)

    def enum(self, value: Any, title: str | None = None) -> Logger:
        """Log enum value with name and value."""
        from enum import Enum
        if not isinstance(value, Enum):
            return self.send(title or "Enum", {"value": value, "_warning": "Not an Enum"})
        info = {
            "name": value.name,
            "value": value.value,
            "class": type(value).__name__,
            "module": type(value).__module__,
        }
        return self.send(title or type(value).__name__, info)

    def ptr(self, obj: Any, title: str | None = None) -> Logger:
        """Log object identity/pointer."""
        info = {
            "id": id(obj),
            "hex_id": hex(id(obj)),
            "type": type(obj).__name__,
            "module": type(obj).__module__,
            "repr": repr(obj)[:200],
        }
        return self.send(title or "Pointer", info)

    def variant(self, value: Any, title: str | None = None) -> Logger:
        """Log any value with type information."""
        info: dict[str, Any] = {
            "value": value,
            "type": type(value).__name__,
            "module": type(value).__module__,
            "is_none": value is None,
            "is_callable": callable(value),
        }
        if isinstance(value, (int, float, complex)):
            info["numeric"] = True
        elif isinstance(value, str):
            info["length"] = len(value)
            info["is_empty"] = len(value) == 0
        elif isinstance(value, (list, tuple)):
            info["length"] = len(value)
            info["item_types"] = list(set(type(item).__name__ for item in value[:10]))
        elif isinstance(value, dict):
            info["keys"] = list(value.keys())[:20]
            info["length"] = len(value)
        return self.send(title or "Variant", info)

    def sset(self, s: set | frozenset, title: str | None = None, max_items: int = 100) -> Logger:
        """Log set/frozenset."""
        items = list(s)[:max_items]
        info = {
            "type": type(s).__name__,
            "total_items": len(s),
            "items_shown": len(items),
            "truncated": len(s) > max_items,
            "items": items,
        }
        return self.send(title or "Set", info)

    # === System & Memory Methods ===
    def system_info(self, title: str | None = None) -> Logger:
        """Log system information."""
        import platform
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
        return self.send(title or "System Info", info)

    def memory_status(self, title: str | None = None) -> Logger:
        """Log memory status."""
        try:
            import psutil
            mem = psutil.virtual_memory()
            info = {
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "free": mem.free,
                "percent": mem.percent,
                "_source": "psutil",
            }
        except ImportError:
            import sys
            info = {"_warning": "psutil not installed", "_fallback": "sys info only"}
            try:
                import resource
                usage = resource.getrusage(resource.RUSAGE_SELF)
                info["max_rss"] = usage.ru_maxrss
            except ImportError:
                pass
        return self.send(title or "Memory Status", info)

    def memory_hex(self, data: bytes, title: str | None = None, max_size: int = 256) -> Logger:
        """Log bytes as hex dump."""
        if not isinstance(data, bytes):
            return self.warning("memory_hex requires bytes", type=type(data).__name__)
        truncated = len(data) > max_size
        display = data[:max_size]
        hex_lines = []
        for i in range(0, len(display), 16):
            chunk = display[i:i+16]
            hex_part = " ".join(f"{b:02x}" for b in chunk)
            ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            hex_lines.append(f"{i:04x}: {hex_part:<48} {ascii_part}")
        info = {
            "total_size": len(data),
            "dumped_size": len(display),
            "truncated": truncated,
            "hex_dump": "\n".join(hex_lines),
            "hex_string": display.hex(),
        }
        return self.send(title or "Memory Hex", info)

    def stack_trace(self, title: str | None = None, limit: int = 10) -> Logger:
        """Log current stack trace."""
        import traceback
        stack = traceback.format_stack(limit=limit)
        info = {
            "stack_frames": len(stack),
            "trace": "".join(stack),
            "trace_list": [line.strip() for line in stack if line.strip()],
        }
        return self.send(title or "Stack Trace", info)

    # === File & Stream Methods ===
    def file_hex(self, path: Any, title: str | None = None, max_size: int = 1024) -> Logger:
        """Log file contents as hex dump."""
        from pathlib import Path
        p = Path(path)
        if not p.exists():
            return self.send(title or "File Hex", {"_error": f"File not found: {p}"})
        try:
            with open(p, "rb") as f:
                data = f.read(max_size)
            hex_lines = []
            for i in range(0, len(data), 16):
                chunk = data[i:i+16]
                hex_part = " ".join(f"{b:02x}" for b in chunk)
                ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
                hex_lines.append(f"{i:08x}: {hex_part:<48} {ascii_part}")
            info = {
                "filename": str(p),
                "total_size": p.stat().st_size,
                "dumped_size": len(data),
                "truncated": p.stat().st_size > max_size,
                "hex_dump": "\n".join(hex_lines),
                "hex_string": data.hex(),
            }
            return self.send(title or "File Hex", info)
        except Exception as e:
            return self.send(title or "File Hex", {"_error": str(e), "filename": str(p)})

    def file_text(self, path: Any, title: str | None = None, max_lines: int = 100, encoding: str = "utf-8") -> Logger:
        """Log text file contents."""
        from pathlib import Path
        p = Path(path)
        if not p.exists():
            return self.send(title or "Text File", {"_error": f"File not found: {p}"})
        try:
            with open(p, "r", encoding=encoding, errors="replace") as f:
                lines = [line.rstrip('\n\r') for i, line in enumerate(f) if i < max_lines]
            total_lines = sum(1 for _ in open(p, "r", encoding=encoding, errors="replace"))
            info = {
                "filename": str(p),
                "total_lines": total_lines,
                "lines_shown": len(lines),
                "truncated": len(lines) < total_lines,
                "encoding": encoding,
                "content": lines,
                "text_preview": "\n".join(lines[:10]),
            }
            return self.send(title or "Text File", info)
        except Exception as e:
            return self.send(title or "Text File", {"_error": str(e), "filename": str(p)})

    def stream_hex(self, stream: Any, title: str | None = None, max_size: int = 1024) -> Logger:
        """Log binary stream as hex dump."""
        try:
            data = stream.read(max_size)
            hex_lines = []
            for i in range(0, len(data), 16):
                chunk = data[i:i+16]
                hex_part = " ".join(f"{b:02x}" for b in chunk)
                ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
                hex_lines.append(f"{i:08x}: {hex_part:<48} {ascii_part}")
            info = {
                "stream_type": type(stream).__name__,
                "dumped_size": len(data),
                "hex_dump": "\n".join(hex_lines),
                "hex_string": data.hex(),
            }
            return self.send(title or "Stream Hex", info)
        except Exception as e:
            return self.send(title or "Stream Hex", {"_error": str(e)})

    def stream_text(self, stream: Any, title: str | None = None, max_lines: int = 100) -> Logger:
        """Log text stream contents."""
        try:
            lines = [line.rstrip('\n\r') for i, line in enumerate(stream) if i < max_lines]
            info = {
                "stream_type": type(stream).__name__,
                "lines": len(lines),
                "truncated": len(lines) >= max_lines - 1,
                "content": lines,
                "text_preview": "\n".join(lines[:10]),
            }
            return self.send(title or "Stream Text", info)
        except Exception as e:
            return self.send(title or "Stream Text", {"_error": str(e)})

    # === Context (LoggerX features) ===
    def scope(self, **ctx: Any):
        """Create nested scope: `with log.scope(user_id=123):`"""
        return scope(**ctx)

    def ctx(self, **ctx: Any) -> Logger:
        """Fluent interface to add context to a new logger instance."""
        new_ctx = self._context.copy()
        new_ctx.update(ctx)
        child = Logger(self._name, new_ctx)
        child._level = self._level
        return child

    def new(self, name: str | None = None) -> Logger:
        """Create child logger with name."""
        new_name = f"{self._name}.{name}" if name else self._name
        child = Logger(new_name, self._context.copy())
        child._level = self._level
        return child

    @contextmanager
    def span(self, name: str, **attributes: Any):
        """OpenTelemetry span context manager."""
        try:
            from opentelemetry import trace as otel

            tracer = otel.get_tracer(__name__)
            with tracer.start_as_current_span(name, attributes=attributes) as span:
                yield span
        except ImportError:

            class MockSpan:
                def set_attribute(self, k, v):
                    pass

                def add_event(self, n, a=None):
                    pass

                def __enter__(self):
                    return self

                def __exit__(self, *a):
                    pass

            yield MockSpan()

    # === Decorators (exposed as methods) ===
    logged = staticmethod(decorators.logged)
    timed = staticmethod(decorators.timed)
    retry = staticmethod(decorators.retry)
    generator = staticmethod(decorators.generator)
    aiterator = staticmethod(decorators.aiterator)
    trace = staticmethod(decorators.trace)

    # === Config ===
    def configure(
        self,
        level: str = "DEBUG",
        destinations: list[str] | None = None,
        format: str = "rich",
        context: dict[str, Any] | None = None,
        mask_fields: list[str] | None = None,
        **_: Any,
    ) -> Logger:
        self._level = Level[level.upper()]

        if context:
            self._context.update(context)

        if mask_fields:
            from ._mask import Masker

            self._masker = Masker(mask_fields, [])
            set_global_masker(self._masker)

        if destinations:
            # Clear existing destinations if possible, or we just add new ones?
            # Simple implementation: Add what's requested.
            for dest in destinations:
                if dest == "console":
                    # Console destination setup
                    if format == "rich":
                        # We can't easily plug async destination into sync logxpy pipeline yet
                        # For now, we assume standard logxpy setup + our extensions.
                        pass

                elif dest.startswith("file://"):
                    path = dest.replace("file://", "")
                    # Store file handle to keep it open
                    if self._auto_log_file:
                        self._auto_log_file.close()
                    self._auto_log_file = open(path, "a")
                    to_file(self._auto_log_file)

                elif dest.startswith("otel"):
                    # Setup OTel
                    pass

        return self

    def init(
        self,
        target: str | Path | None = None,
        *,
        level: str = "DEBUG",
        mode: str = "w",
        clean: bool = False,
    ) -> Logger:
        """Simplified logging initialization.
        
        Usage:
            log.init()                    # Auto-generate .log from __file__
            log.init(clean=True)          # Fresh log (delete old first)
            log.init("app.log")           # Custom file path
            log.init(level="INFO")        # With log level
            log.init("app.log", mode="a") # Append mode (default is 'w')
        
        Args:
            target: File path, None for auto filename from caller's __file__
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            mode: File mode - 'w' write (default) or 'a' append
            clean: Delete existing log file before opening (default: False)
        
        Returns:
            self for chaining
        """
        from pathlib import Path
        import sys
        from inspect import stack
        from ._output import FileDestination, Logger as OutputLogger

        # Set level
        self._level = Level[level.upper()]

        if target is None:
            # Try to auto-detect if called from __main__
            caller_frame = stack()[1]
            caller_file = caller_frame.filename
            if caller_file == '<stdin>':
                # Interactive - use stdout
                OutputLogger._destinations.add(FileDestination(file=sys.stdout))
            else:
                # Auto-generate log filename from caller script
                log_path = Path(caller_file).with_suffix('.log')
                log_path.parent.mkdir(parents=True, exist_ok=True)
                # Clean old log if requested
                if clean and log_path.exists():
                    log_path.unlink()
                f = open(log_path, mode, encoding='utf-8', buffering=1)
                OutputLogger._destinations.add(FileDestination(file=f))
                self._auto_log_file = log_path  # Store for reference
        else:
            # File logging
            path = Path(target)
            path.parent.mkdir(parents=True, exist_ok=True)
            # Clean old log if requested
            if clean and path.exists():
                path.unlink()
            f = open(path, mode, encoding='utf-8', buffering=1)
            OutputLogger._destinations.add(FileDestination(file=f))
            self._auto_log_file = path  # Store for reference
        
        return self

    def clean(self) -> Logger:
        """Delete the auto-generated log file if it exists.
        
        Useful for ensuring fresh logs on each run. Works with auto-generated
        log files from `log.init()` or when a path was provided to `init()`.
        
        Example:
            log.init("app.log").clean()  # Delete old log, then start fresh
            log.info("Starting fresh")
        
        Returns:
            self for chaining
        """
        from pathlib import Path
        
        if self._auto_log_file:
            path = Path(self._auto_log_file)
            if path.exists():
                path.unlink()
        return self

    # === Color Methods (for CLI viewer) ===
    def set_foreground(self, color: str) -> Logger:
        """Set foreground color for subsequent log entries (viewer hint).
        
        Args:
            color: Color name (red, green, blue, yellow, magenta, cyan, white, black)
        
        Example:
            log.set_foreground("red")
            log.error("This is red")
            log.reset_foreground()
        """
        self._context["fg"] = color
        return self
    
    def set_background(self, color: str) -> Logger:
        """Set background color for subsequent log entries (viewer hint).
        
        Args:
            color: Color name (red, green, blue, yellow, magenta, cyan, white, black)
        
        Example:
            log.set_background("yellow")
            log.warning("This has yellow background")
            log.reset_background()
        """
        self._context["bg"] = color
        return self
    
    def reset_foreground(self) -> Logger:
        """Reset foreground color to default."""
        self._context.pop("fg", None)
        return self
    
    def reset_background(self) -> Logger:
        """Reset background color to default."""
        self._context.pop("bg", None)
        return self
    
    def colored(self, msg: str, foreground: str | None = None, background: str | None = None, **fields: Any) -> Logger:
        """Log a message with specific foreground/background colors (one-shot).
        
        Args:
            msg: Message to log
            foreground: Foreground color name
            background: Background color name
            **fields: Additional fields
        
        Example:
            log.colored("Important!", foreground="red", background="yellow", priority="high")
        """
        # Add color fields temporarily
        if foreground:
            fields["fg"] = foreground
        if background:
            fields["bg"] = background
        return self._log(Level.INFO, msg, **fields)

    # === Internal ===
    def _log(self, level: Level, msg: str, **fields: Any) -> Logger:
        if level.value < self._level.value:
            return self
        act = current_action()
        task_uuid, task_level = _get_task_info(act)

        # Merge context: global scope + logger instance context
        ctx = current_scope()
        if self._context:
            ctx = {**ctx, **self._context}

        record = Record(
            timestamp=now(),
            level=level,
            message=msg,
            message_type=level.name.lower(),  # "info", "success", "error", etc.
            fields=fields,
            context=ctx,
            task_uuid=task_uuid,
            task_level=task_level,
        )
        _emit(record)  # Goes to destinations + any registered handlers
        return self


def _get_task_info(act) -> tuple[str, tuple[int, ...]]:
    """Extract task info from Action or AsyncAction."""
    if act is None:
        return uuid(), (1,)
    task_uuid = act.task_uuid
    # Action uses _task_level (TaskLevel), AsyncAction uses task_level (tuple)
    if hasattr(act, "task_level"):  # AsyncAction
        return task_uuid, act.task_level
    if hasattr(act, "_task_level"):  # Action
        return task_uuid, tuple(act._task_level.as_list())
    return task_uuid, (1,)


# === Global masker ===
_global_masker = None


def set_global_masker(masker):
    global _global_masker
    _global_masker = masker


def get_global_masker():
    return _global_masker


# === Global instance ===
log = Logger()
