"""Output destinations."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from ._types import Record


class ConsoleDestination:
    def __init__(self, rich: bool = True):
        self._rich = rich
        if rich:
            from rich.console import Console

            self._console = Console()

    async def write(self, record: Record) -> None:
        lvl = record.level.name.ljust(8)
        line = f"[{lvl}] {record.message} {record.fields}"
        if self._rich:
            color = {"ERROR": "red", "WARNING": "yellow", "SUCCESS": "green"}.get(record.level.name, "")
            self._console.print(f"[{color}]{line}[/{color}]" if color else line)
        else:
            print(line)

    async def flush(self) -> None:
        pass

    async def close(self) -> None:
        pass


class FileDestination:
    def __init__(self, path: str | Path, buffer: int = 100):
        self._path = Path(path)
        self._buf: list[str] = []
        self._size = buffer
        self._lock = asyncio.Lock()

    async def write(self, record: Record) -> None:
        import orjson

        line = orjson.dumps(record.to_dict()).decode() + "\n"
        async with self._lock:
            self._buf.append(line)
            if len(self._buf) >= self._size:
                await self.flush()

    async def flush(self) -> None:
        if not self._buf:
            return
        async with self._lock:
            with self._path.open("a") as f:
                f.writelines(self._buf)
            self._buf.clear()

    async def close(self) -> None:
        await self.flush()


class OTelDestination:
    def __init__(self, endpoint: str = "localhost:4317"):
        self._endpoint = endpoint
        self._tracer: Any | None = None

    async def write(self, record: Record) -> None:
        if not self._tracer:
            try:
                from opentelemetry import trace
                from opentelemetry.sdk.trace import TracerProvider

                trace.set_tracer_provider(TracerProvider())
                self._tracer = trace.get_tracer(__name__)
            except ImportError:
                return
        if self._tracer and record.action_type:
            with self._tracer.start_as_current_span(record.action_type) as span:
                for k, v in record.fields.items():
                    span.set_attribute(k, str(v))

    async def flush(self) -> None:
        pass

    async def close(self) -> None:
        pass
