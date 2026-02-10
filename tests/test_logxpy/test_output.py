"""Tests for logxpy/src/_output.py -- Output destinations and Logger."""
from __future__ import annotations

import json
import pytest

from logxpy.src._output import (
    BufferingDestination,
    Destinations,
    FileDestination,
    Logger,
    MemoryLogger,
    to_file,
    init_file_destination,
    DESTINATION_FAILURE,
)
from logxpy.src._message import MESSAGE_TYPE_FIELD, REASON_FIELD


# ============================================================================
# BufferingDestination
# ============================================================================

class TestBufferingDestination:
    def test_stores_messages(self):
        buf = BufferingDestination()
        buf({"msg": "hello"})
        assert len(buf.messages) == 1
        assert buf.messages[0]["msg"] == "hello"

    def test_caps_at_1000(self):
        buf = BufferingDestination()
        for i in range(1100):
            buf({"i": i})
        assert len(buf.messages) == 1000


# ============================================================================
# Destinations
# ============================================================================

class TestDestinations:
    def test_initial_has_buffering(self):
        d = Destinations()
        assert len(d._destinations) == 1
        assert isinstance(d._destinations[0], BufferingDestination)

    def test_add_clears_buffer(self):
        d = Destinations()
        d.send({"pre": True})
        received = []
        d.add(lambda m: received.append(m))
        # Buffered message should be re-delivered
        assert any(m.get("pre") for m in received)

    def test_send_to_all_destinations(self):
        d = Destinations()
        r1, r2 = [], []
        d.add(lambda m: r1.append(m))
        d.add(lambda m: r2.append(m))
        d.send({"x": 1})
        assert len(r1) == 1
        assert len(r2) == 1

    def test_remove_destination(self):
        d = Destinations()
        fn = lambda m: None
        d.add(fn)
        d.remove(fn)
        assert fn not in d._destinations

    def test_remove_unknown_raises_valueerror(self):
        d = Destinations()
        with pytest.raises(ValueError):
            d.remove(lambda m: None)

    def test_global_fields_added(self):
        d = Destinations()
        received = []
        d.add(lambda m: received.append(m))
        d.addGlobalFields(env="test")
        d.send({"msg": "hi"})
        assert received[0]["env"] == "test"

    def test_broken_destination_does_not_raise(self):
        d = Destinations()
        d.add(lambda m: None)  # Good destination first

        def bad(m):
            raise RuntimeError("broken")

        d.add(bad)
        # Should not raise
        d.send({"mt": "test"})


# ============================================================================
# Logger
# ============================================================================

class TestLogger:
    def test_write_sends_to_destinations(self, captured_messages):
        logger = Logger()
        logger.write({"msg": "test"})
        assert len(captured_messages) == 1
        assert captured_messages[0]["msg"] == "test"

    def test_write_copies_dict(self, captured_messages):
        logger = Logger()
        original = {"msg": "original"}
        logger.write(original)
        # Modifying original should not affect captured
        original["msg"] = "modified"
        assert captured_messages[0]["msg"] == "original"


# ============================================================================
# MemoryLogger
# ============================================================================

class TestMemoryLogger:
    def test_write_stores_messages(self):
        ml = MemoryLogger()
        ml.write({"msg": "hello"})
        assert len(ml.messages) == 1

    def test_reset_clears_all(self):
        ml = MemoryLogger()
        ml.write({"msg": "hello"})
        ml.reset()
        assert len(ml.messages) == 0
        assert len(ml.serializers) == 0
        assert len(ml.tracebackMessages) == 0

    def test_validate_fails_non_unicode_key(self):
        ml = MemoryLogger()
        ml.write({123: "value"})
        with pytest.raises(TypeError):
            ml.validate()

    def test_flush_tracebacks(self):
        from logxpy.src._traceback import TRACEBACK_MESSAGE
        ml = MemoryLogger()
        msg = {
            MESSAGE_TYPE_FIELD: "eliot:traceback",
            REASON_FIELD: ValueError("test"),
            "traceback": "...",
        }
        ml.write(msg, TRACEBACK_MESSAGE._serializer)
        assert len(ml.tracebackMessages) == 1
        flushed = ml.flushTracebacks(ValueError)
        assert len(flushed) == 1
        assert len(ml.tracebackMessages) == 0


# ============================================================================
# FileDestination
# ============================================================================

class TestFileDestination:
    def test_write_json_to_text_file(self, tmp_path):
        f = open(tmp_path / "out.log", "w")
        dest = FileDestination(file=f)
        dest({"msg": "hello"})
        f.close()
        content = (tmp_path / "out.log").read_text()
        data = json.loads(content.strip())
        assert data["msg"] == "hello"

    def test_write_json_to_binary_file(self, tmp_path):
        f = open(tmp_path / "out.log", "wb")
        dest = FileDestination(file=f)
        dest({"msg": "binary"})
        f.close()
        content = (tmp_path / "out.log").read_bytes()
        data = json.loads(content.strip())
        assert data["msg"] == "binary"


# ============================================================================
# to_file
# ============================================================================

class TestToFile:
    def test_messages_written_to_file(self, tmp_path, fresh_destinations):
        f = open(tmp_path / "test.log", "w")
        to_file(f)
        Logger().write({"msg": "via_to_file"})
        f.close()
        content = (tmp_path / "test.log").read_text()
        assert "via_to_file" in content


# ============================================================================
# init_file_destination
# ============================================================================

class TestInitFileDestination:
    def test_creates_file(self, tmp_path, fresh_destinations):
        path = tmp_path / "app.log"
        init_file_destination(path)
        Logger().write({"msg": "init_test"})
        assert path.exists()
        assert "init_test" in path.read_text()

    def test_creates_parent_dirs(self, tmp_path, fresh_destinations):
        path = tmp_path / "nested" / "deep" / "app.log"
        init_file_destination(path)
        Logger().write({"msg": "nested"})
        assert path.exists()
