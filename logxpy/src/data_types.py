"""Data Type Specific Logging - CodeSite-compatible with lazy imports.

All functions use lazy imports to avoid errors when optional dependencies
are not installed. No ImportError is raised - features gracefully degrade.
"""

from __future__ import annotations

import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from .logx import log


def _lazy_import(module_name: str) -> Any | None:
    """Lazy import with silent fallback."""
    try:
        return __import__(module_name, fromlist=[""])
    except ImportError:
        return None


def send_color(
    color: Any,
    msg: str = "Color",
    as_hex: bool = True,
) -> None:
    """Send color value (CodeSite SendColor equivalent).
    
    Accepts various color formats and converts to standard representation.
    
    Args:
        color: Color value (tuple, int, hex string, or color object)
        msg: Message prefix
        as_hex: Prefer hex representation
    """
    info: dict[str, Any] = {"original_type": type(color).__name__}
    
    # Handle different color formats
    if isinstance(color, (tuple, list)) and len(color) >= 3:
        # RGB/RGBA tuple
        r, g, b = int(color[0]), int(color[1]), int(color[2])
        a = int(color[3]) if len(color) > 3 else None
        
        info["rgb"] = {"r": r, "g": g, "b": b}
        if a is not None:
            info["rgba"] = {"r": r, "g": g, "b": b, "a": a}
        info["hex"] = f"#{r:02x}{g:02x}{b:02x}"
        if a is not None:
            info["hex_with_alpha"] = f"#{r:02x}{g:02x}{b:02x}{a:02x}"
            
    elif isinstance(color, int):
        # Assume 0xRRGGBB format
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        info["rgb"] = {"r": r, "g": g, "b": b}
        info["hex"] = f"#{r:02x}{g:02x}{b:02x}"
        info["integer"] = color
        
    elif isinstance(color, str):
        # Hex string or name
        if color.startswith('#'):
            info["hex"] = color.lower()
            # Parse RGB
            try:
                h = color.lstrip('#')
                if len(h) == 6:
                    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
                    info["rgb"] = {"r": r, "g": g, "b": b}
            except ValueError:
                pass
        else:
            info["name"] = color
            # Try to resolve color name
            try:
                # Check if PIL is available for color resolution
                PIL = _lazy_import("PIL.ImageColor")
                if PIL:
                    rgb = PIL.getrgb(color)
                    info["rgb"] = {"r": rgb[0], "g": rgb[1], "b": rgb[2]}
                    info["hex"] = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            except Exception:
                pass
    
    else:
        # Try to get common attributes
        for attr in ["r", "g", "b", "red", "green", "blue", "hue", "saturation", "value"]:
            if hasattr(color, attr):
                try:
                    info[attr] = getattr(color, attr)
                except Exception:
                    pass
    
    log.send(msg, info)


def send_currency(
    value: Decimal | float | str | int,
    currency: str = "USD",
    msg: str = "Currency",
) -> None:
    """Send currency value with proper precision (CodeSite SendCurrency equivalent).
    
    Args:
        value: Currency amount (use Decimal for precision)
        currency: Currency code (USD, EUR, etc.)
        msg: Message prefix
    """
    # Convert to Decimal for precision
    if isinstance(value, Decimal):
        dec_value = value
    elif isinstance(value, (int, str)):
        dec_value = Decimal(str(value))
    else:
        dec_value = Decimal(str(value))
    
    info = {
        "amount": str(dec_value),  # String to preserve precision
        "amount_float": float(dec_value),
        "currency": currency.upper(),
        "formatted": f"{currency.upper()} {dec_value}",
    }
    
    log.send(msg, info)


def send_datetime(
    dt: datetime.datetime | float | str | None = None,
    msg: str = "DateTime",
) -> None:
    """Send datetime value (CodeSite SendDateTime equivalent).
    
    Args:
        dt: Datetime value (datetime object, Unix timestamp, or ISO string)
        msg: Message prefix
    """
    if dt is None:
        dt = datetime.datetime.now()
    
    if isinstance(dt, (int, float)):
        # Unix timestamp
        dt = datetime.datetime.fromtimestamp(dt)
    elif isinstance(dt, str):
        # ISO string
        dt = datetime.datetime.fromisoformat(dt.replace('Z', '+00:00'))
    
    info = {
        "iso": dt.isoformat(),
        "timestamp": dt.timestamp(),
        "year": dt.year,
        "month": dt.month,
        "day": dt.day,
        "hour": dt.hour,
        "minute": dt.minute,
        "second": dt.second,
        "microsecond": dt.microsecond,
        "timezone": str(dt.tzinfo) if dt.tzinfo else None,
        "formatted": dt.strftime("%Y-%m-%d %H:%M:%S"),
        "date": dt.strftime("%Y-%m-%d"),
        "time": dt.strftime("%H:%M:%S"),
    }
    
    log.send(msg, info)


def send_datetime_if(
    condition: bool,
    dt: datetime.datetime | float | str | None = None,
    msg: str = "DateTime",
) -> None:
    """Send datetime only if condition is true (CodeSite SendDateTimeIf equivalent).
    
    Args:
        condition: Condition to check
        dt: Datetime value
        msg: Message prefix
    """
    if condition:
        send_datetime(dt, msg)


def send_enum(
    enum_value: Enum,
    msg: str | None = None,
) -> None:
    """Send enumeration value (CodeSite SendEnum equivalent).
    
    Args:
        enum_value: Enum member
        msg: Message prefix (defaults to enum class name)
    """
    if msg is None:
        msg = type(enum_value).__name__
    
    info = {
        "name": enum_value.name,
        "value": enum_value.value,
        "class": type(enum_value).__name__,
        "module": type(enum_value).__module__,
    }
    
    log.send(msg, info)


def send_set(
    s: set | frozenset,
    msg: str = "Set",
    max_items: int = 100,
) -> None:
    """Send set value (CodeSite SendSet equivalent).
    
    Args:
        s: Set or frozenset
        msg: Message prefix
        max_items: Maximum items to include
    """
    items = list(s)[:max_items]
    
    info = {
        "type": type(s).__name__,
        "total_items": len(s),
        "items_shown": len(items),
        "truncated": len(s) > max_items,
        "items": items,
        "as_list": items,  # JSON-compatible
    }
    
    log.send(msg, info)


def send_pointer(
    obj: Any,
    msg: str = "Pointer",
) -> None:
    """Send object identity/pointer (CodeSite SendPointer equivalent).
    
    Args:
        obj: Object to get identity for
        msg: Message prefix
    """
    info = {
        "id": id(obj),
        "hex_id": hex(id(obj)),
        "type": type(obj).__name__,
        "module": type(obj).__module__,
        "repr": repr(obj)[:200],
    }
    
    log.send(msg, info)


def send_variant(
    value: Any,
    msg: str = "Variant",
) -> None:
    """Send any value with type information (CodeSite SendVariant equivalent).
    
    Python is dynamically typed, so this provides comprehensive type info.
    
    Args:
        value: Any Python value
        msg: Message prefix
    """
    info: dict[str, Any] = {
        "value": value,
        "type": type(value).__name__,
        "module": type(value).__module__,
        "is_none": value is None,
        "is_callable": callable(value),
    }
    
    # Add type-specific info
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
    
    # Try to get docstring for callables
    if callable(value) and hasattr(value, "__doc__"):
        doc = value.__doc__
        if doc:
            info["doc"] = doc[:200]
    
    log.send(msg, info)


# =============================================================================
# Conditional & Formatted Sending (CodeSite-compatible)
# =============================================================================

def send_if(
    condition: bool,
    msg: str,
    **fields: Any,
) -> None:
    """Send log message only if condition is true (CodeSite SendIf equivalent).
    
    This is a convenience wrapper around Python's standard if statement.
    In Python, you can also simply use: if condition: log.send(msg, **fields)
    
    Args:
        condition: Condition to check
        msg: Message to log
        **fields: Additional fields to log
    """
    if condition:
        log.send(msg, fields)


def send_assigned(
    value: Any,
    msg: str | None = None,
    **extra_fields: Any,
) -> bool:
    """Send log message only if value is not None (CodeSite SendAssigned equivalent).
    
    This is Python's equivalent of Delphi's Assigned() check.
    
    Args:
        value: Value to check
        msg: Message to log (defaults to "Assigned: {type}")
        **extra_fields: Additional fields to log
        
    Returns:
        True if value was logged (not None), False otherwise
    """
    if value is not None:
        if msg is None:
            msg = f"Assigned: {type(value).__name__}"
        
        info = {
            "value": value,
            "type": type(value).__name__,
            **extra_fields,
        }
        log.send(msg, info)
        return True
    return False


def send_fmt_msg(
    fmt: str,
    *args: Any,
    msg: str = "Formatted",
    **fields: Any,
) -> None:
    """Send formatted message (CodeSite SendFmtMsg equivalent).
    
    Uses Python's f-string style formatting or .format() style.
    
    Args:
        fmt: Format string
        *args: Positional arguments for format
        msg: Message prefix
        **fields: Additional fields to log
        
    Examples:
        >>> send_fmt_msg("User {} has {} messages", username, count)
        >>> send_fmt_msg("Value: {value:.2f}", value=3.14159)
    """
    try:
        # Try .format() style first
        formatted = fmt.format(*args, **fields)
    except (IndexError, KeyError):
        # Fall back to % formatting
        try:
            formatted = fmt % args
        except TypeError:
            # Last resort: just concatenate
            formatted = fmt + " " + " ".join(str(a) for a in args)
    
    # Filter out 'msg' from fields if present
    extra_fields = {k: v for k, v in fields.items() if k not in ("formatted", "format", "args")}
    
    info = {
        "formatted": formatted,
        "format": fmt,
        "args": [str(a) for a in args[:10]],  # Limit args
        **extra_fields,
    }
    
    log.send(msg, info)


# Alternative name for send_fmt_msg
SendFmtMsg = send_fmt_msg


# CodeSite-style aliases
SendColor = send_color
SendCurrency = send_currency
SendDateTime = send_datetime
SendDateTimeIf = send_datetime_if
SendEnum = send_enum
SendSet = send_set
SendPointer = send_pointer
SendVariant = send_variant
SendIf = send_if
SendAssigned = send_assigned
SendFmtMsg = send_fmt_msg

# Monkey-patch Logger class for fluent API
from . import logx

logx.Logger.send_color = lambda self, color, msg="Color", as_hex=True: (
    send_color(color, msg, as_hex), self
)[1]
logx.Logger.send_currency = lambda self, value, currency="USD", msg="Currency": (
    send_currency(value, currency, msg), self
)[1]
logx.Logger.send_datetime = lambda self, dt=None, msg="DateTime": (
    send_datetime(dt, msg), self
)[1]
logx.Logger.send_datetime_if = lambda self, condition, dt=None, msg="DateTime": (
    send_datetime_if(condition, dt, msg), self
)[1]
logx.Logger.send_enum = lambda self, enum_value, msg=None: (
    send_enum(enum_value, msg), self
)[1]
logx.Logger.send_set = lambda self, s, msg="Set", max_items=100: (
    send_set(s, msg, max_items), self
)[1]
logx.Logger.send_pointer = lambda self, obj, msg="Pointer": (
    send_pointer(obj, msg), self
)[1]
logx.Logger.send_variant = lambda self, value, msg="Variant": (
    send_variant(value, msg), self
)[1]

# Conditional & Formatted Sending fluent API
logx.Logger.send_if = lambda self, condition, msg, **fields: (
    send_if(condition, msg, **fields), self
)[1] if condition else self

logx.Logger.send_assigned = lambda self, value, msg=None, **extra_fields: (
    send_assigned(value, msg, **extra_fields), self
)[1] if value is not None else self

logx.Logger.send_fmt_msg = lambda self, fmt, *args, msg="Formatted", **fields: (
    send_fmt_msg(fmt, *args, msg=msg, **fields), self
)[1]

__all__ = [
    "send_color",
    "send_currency",
    "send_datetime",
    "send_datetime_if",
    "send_enum",
    "send_set",
    "send_pointer",
    "send_variant",
    # Conditional & Formatted
    "send_if",
    "send_assigned",
    "send_fmt_msg",
    # CodeSite-style aliases
    "SendColor",
    "SendCurrency",
    "SendDateTime",
    "SendDateTimeIf",
    "SendEnum",
    "SendSet",
    "SendPointer",
    "SendVariant",
    "SendIf",
    "SendAssigned",
    "SendFmtMsg",
]
