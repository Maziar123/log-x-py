"""File and Stream Operations - CodeSite-compatible with lazy imports.

All functions use lazy imports to avoid errors when optional dependencies
are not installed. No ImportError is raised - features gracefully degrade.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any, BinaryIO, TextIO

from .loggerx import log


def send_file_as_hex(
    filename: str | Path,
    msg: str = "File Hex",
    max_size: int = 1024,
    offset: int = 0,
) -> None:
    """Send file contents as hex dump (CodeSite SendFileAsHex equivalent).
    
    Args:
        filename: Path to file
        msg: Message prefix
        max_size: Maximum bytes to read
        offset: Starting byte offset
    """
    path = Path(filename)
    
    if not path.exists():
        log.send(msg, {"_error": f"File not found: {path}"})
        return
    
    try:
        with open(path, "rb") as f:
            if offset > 0:
                f.seek(offset)
            data = f.read(max_size)
        
        truncated = path.stat().st_size > max_size
        total_size = path.stat().st_size
        
        # Format hex dump
        hex_lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_part = " ".join(f"{b:02x}" for b in chunk)
            ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            hex_lines.append(f"{offset+i:08x}: {hex_part:<48} {ascii_part}")
        
        info = {
            "filename": str(path),
            "total_size": total_size,
            "dumped_size": len(data),
            "offset": offset,
            "truncated": truncated,
            "hex_dump": "\n".join(hex_lines),
            "hex_string": data.hex(),
        }
        
        log.send(msg, info)
        
    except Exception as e:
        log.send(msg, {"_error": str(e), "filename": str(path)})


def send_text_file(
    filename: str | Path,
    msg: str = "Text File",
    max_lines: int = 100,
    encoding: str = "utf-8",
) -> None:
    """Send text file contents (CodeSite SendTextFile equivalent).
    
    Args:
        filename: Path to file
        msg: Message prefix
        max_lines: Maximum lines to read
        encoding: File encoding
    """
    path = Path(filename)
    
    if not path.exists():
        log.send(msg, {"_error": f"File not found: {path}"})
        return
    
    try:
        with open(path, "r", encoding=encoding, errors="replace") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                lines.append(line.rstrip('\n\r'))
        
        total_lines = sum(1 for _ in open(path, "r", encoding=encoding, errors="replace"))
        
        info = {
            "filename": str(path),
            "total_lines": total_lines,
            "lines_shown": len(lines),
            "truncated": len(lines) < total_lines,
            "encoding": encoding,
            "content": lines,
            "text_preview": "\n".join(lines[:10]),
        }
        
        log.send(msg, info)
        
    except Exception as e:
        log.send(msg, {"_error": str(e), "filename": str(path)})


def send_stream_as_hex(
    stream: BinaryIO,
    msg: str = "Stream Hex",
    max_size: int = 1024,
) -> None:
    """Send binary stream as hex dump (CodeSite SendStreamAsHex equivalent).
    
    Args:
        stream: Binary stream to read
        msg: Message prefix
        max_size: Maximum bytes to read
    """
    try:
        data = stream.read(max_size)
        
        # Format hex dump
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
        
        log.send(msg, info)
        
    except Exception as e:
        log.send(msg, {"_error": str(e)})


def send_stream_as_text(
    stream: TextIO,
    msg: str = "Stream Text",
    max_lines: int = 100,
) -> None:
    """Send text stream contents (CodeSite SendStreamAsText equivalent).
    
    Args:
        stream: Text stream to read
        msg: Message prefix
        max_lines: Maximum lines to read
    """
    try:
        lines = []
        for i, line in enumerate(stream):
            if i >= max_lines:
                break
            lines.append(line.rstrip('\n\r'))
        
        info = {
            "stream_type": type(stream).__name__,
            "lines": len(lines),
            "truncated": i >= max_lines - 1,
            "content": lines,
            "text_preview": "\n".join(lines[:10]),
        }
        
        log.send(msg, info)
        
    except Exception as e:
        log.send(msg, {"_error": str(e)})


# Convenience wrappers for common use cases
def send_bytes(data: bytes, msg: str = "Bytes") -> None:
    """Send bytes data with hex formatting."""
    info = {
        "size": len(data),
        "hex": data.hex()[:200],
        "preview": data[:100].decode('utf-8', errors='replace') if data else "",
    }
    log.send(msg, info)


def send_file_info(filename: str | Path, msg: str = "File Info") -> None:
    """Send file metadata without contents."""
    path = Path(filename)
    
    if not path.exists():
        log.send(msg, {"_error": f"File not found: {path}"})
        return
    
    stat = path.stat()
    info = {
        "filename": str(path),
        "exists": True,
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "created": getattr(stat, 'st_birthtime', stat.st_ctime),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "extension": path.suffix,
        "name": path.name,
        "parent": str(path.parent),
    }
    log.send(msg, info)


# CodeSite-style aliases
SendFileAsHex = send_file_as_hex
SendTextFile = send_text_file
SendStreamAsHex = send_stream_as_hex
SendStreamAsText = send_stream_as_text

# Monkey-patch Logger class for fluent API
from . import loggerx

loggerx.Logger.send_file_as_hex = lambda self, filename, msg="File Hex", max_size=1024, offset=0: (
    send_file_as_hex(filename, msg, max_size, offset), self
)[1]
loggerx.Logger.send_text_file = lambda self, filename, msg="Text File", max_lines=100, encoding="utf-8": (
    send_text_file(filename, msg, max_lines, encoding), self
)[1]
loggerx.Logger.send_stream_as_hex = lambda self, stream, msg="Stream Hex", max_size=1024: (
    send_stream_as_hex(stream, msg, max_size), self
)[1]
loggerx.Logger.send_stream_as_text = lambda self, stream, msg="Stream Text", max_lines=100: (
    send_stream_as_text(stream, msg, max_lines), self
)[1]
loggerx.Logger.send_file_info = lambda self, filename, msg="File Info": (
    send_file_info(filename, msg), self
)[1]

__all__ = [
    "send_file_as_hex",
    "send_text_file",
    "send_stream_as_hex",
    "send_stream_as_text",
    "send_bytes",
    "send_file_info",
    # CodeSite-style aliases
    "SendFileAsHex",
    "SendTextFile",
    "SendStreamAsHex",
    "SendStreamAsText",
]
