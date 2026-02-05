"""Tests for eliot._pool."""
from unittest import TestCase
import asyncio
from logxpy._pool import Channel, Pool

class ChannelTests(TestCase):
    def test_send_recv(self):
        """Channel sends and receives items."""
        async def run():
            c = Channel(size=10)
            await c.send(1)
            await c.send(2)
            self.assertEqual(await c.recv(), 1)
            self.assertEqual(await c.recv(), 2)
        asyncio.run(run())

    def test_close(self):
        """Closed channel returns None."""
        async def run():
            c = Channel()
            await c.send(1)
            c.close()
            self.assertEqual(await c.recv(), 1)
            self.assertEqual(await c.recv(), None)
        asyncio.run(run())

    def test_drop_oldest(self):
        """Channel drops oldest when full if requested."""
        async def run():
            c = Channel(size=2, drop_oldest=True)
            await c.send(1)
            await c.send(2)
            await c.send(3) # Should drop 1
            
            self.assertEqual(c.stats.dropped, 1)
            self.assertEqual(await c.recv(), 2)
            self.assertEqual(await c.recv(), 3)
        asyncio.run(run())

class PoolTests(TestCase):
    def test_cpu_pool(self):
        """CPU pool executes function."""
        async def run():
            pool = Pool()
            res = await pool.cpu(sum, [1, 2, 3])
            self.assertEqual(res, 6)
        asyncio.run(run())

    def test_io_pool(self):
        """IO pool executes function."""
        async def run():
            pool = Pool()
            res = await pool.io(str, 123)
            self.assertEqual(res, "123")
        asyncio.run(run())
