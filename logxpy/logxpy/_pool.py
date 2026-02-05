"""Thread pool and async channels."""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


# === Thread Pool ===
class Pool:
    """Shared thread pools for CPU and I/O work."""

    _instance: Pool | None = None

    def __new__(cls) -> Pool:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            n = os.cpu_count() or 4
            cls._instance._cpu = ThreadPoolExecutor(n, thread_name_prefix="lx-cpu-")
            cls._instance._io = ThreadPoolExecutor(n * 2, thread_name_prefix="lx-io-")
        return cls._instance

    async def cpu(self, fn: Callable[..., T], *args: Any, **kw: Any) -> T:
        return await asyncio.get_event_loop().run_in_executor(self._cpu, lambda: fn(*args, **kw))

    async def io(self, fn: Callable[..., T], *args: Any, **kw: Any) -> T:
        return await asyncio.get_event_loop().run_in_executor(self._io, lambda: fn(*args, **kw))

    def shutdown(self) -> None:
        self._cpu.shutdown(wait=False)
        self._io.shutdown(wait=False)


pool = Pool()


# === Channel ===
@dataclass
class ChannelStats:
    sent: int = 0
    recv: int = 0
    dropped: int = 0


class Channel(Generic[T]):
    """Bounded async channel with backpressure."""

    __slots__ = ("_closed", "_drop", "_q", "stats")

    def __init__(self, size: int = 1000, drop_oldest: bool = False):
        self._q: asyncio.Queue[T | None] = asyncio.Queue(maxsize=size)
        self._closed = False
        self._drop = drop_oldest
        self.stats = ChannelStats()

    async def send(self, item: T) -> bool:
        if self._closed:
            return False
        try:
            self._q.put_nowait(item)
        except asyncio.QueueFull:
            if self._drop:
                try:
                    self._q.get_nowait()
                    self.stats.dropped += 1
                except asyncio.QueueEmpty:
                    pass
            await self._q.put(item)
        self.stats.sent += 1
        return True

    async def recv(self) -> T | None:
        item = await self._q.get()
        if item is not None:
            self.stats.recv += 1
        return item

    def close(self) -> None:
        self._closed = True
        try:
            self._q.put_nowait(None)
        except asyncio.QueueFull:
            pass

    async def __aiter__(self) -> AsyncIterator[T]:
        while (item := await self.recv()) is not None:
            yield item
