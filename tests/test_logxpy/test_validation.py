"""Tests for logxpy/src/_validation.py -- Message validation."""
from __future__ import annotations

import warnings

import pytest

from logxpy.src._validation import (
    RESERVED_FIELDS,
    ActionType,
    Field,
    MessageType,
    ValidationError,
    _MessageSerializer,
    fields,
)


class TestField:
    def test_creation(self):
        f = Field("key", lambda x: x, "description")
        assert f.key == "key"
        assert f.description == "description"

    def test_serialize(self):
        f = Field("key", lambda x: x * 2, "desc")
        assert f.serialize(5) == 10

    def test_validate_passes(self):
        f = Field("key", lambda x: x, "desc")
        f.validate(42)  # Should not raise

    def test_validate_extra_validator(self):
        def check(v):
            if v < 0:
                raise ValidationError(v, "Must be positive")

        f = Field("key", lambda x: x, "desc", extraValidator=check)
        f.validate(1)  # OK
        with pytest.raises(ValidationError):
            f.validate(-1)

    def test_for_value(self):
        f = Field.forValue("status", "ok", "Status field")
        # Serializer always returns the fixed value
        assert f.serialize("anything") == "ok"
        f.validate("ok")
        with pytest.raises(ValidationError):
            f.validate("bad")

    def test_for_types(self):
        f = Field.forTypes("count", [int], "A count")
        f.validate(42)
        with pytest.raises(ValidationError):
            f.validate("not an int")

    def test_for_types_none(self):
        f = Field.forTypes("opt", [int, None], "Optional int")
        f.validate(None)
        f.validate(42)

    def test_for_types_invalid_class(self):
        with pytest.raises(TypeError, match="not JSON-encodeable"):
            Field.forTypes("x", [object], "desc")

    def test_pep8_aliases(self):
        """PEP 8 aliases produce the same results as the camelCase originals."""
        f1 = Field.for_value("k", "v", "d")
        f2 = Field.forValue("k", "v", "d")
        assert f1.key == f2.key
        assert f1.serialize("x") == f2.serialize("x")

        f3 = Field.for_types("k", [int], "d")
        f4 = Field.forTypes("k", [int], "d")
        assert f3.key == f4.key

    def test_serialize_identity(self):
        """Identity serializer returns value unchanged."""
        f = Field("x", lambda x: x, "")
        assert f.serialize("hello") == "hello"
        assert f.serialize(42) == 42

    def test_for_types_multiple(self):
        """Field accepting multiple types validates correctly."""
        f = Field.forTypes("multi", [int, str], "Multi-type field")
        f.validate(42)
        f.validate("hello")
        with pytest.raises(ValidationError):
            f.validate(3.14)


class TestFields:
    def test_creates_field_list(self):
        result = fields(Field("a", lambda x: x, ""), name=str)
        assert len(result) == 2
        assert result[0].key == "a"
        assert result[1].key == "name"

    def test_empty_fields(self):
        result = fields()
        assert result == []

    def test_kwargs_only(self):
        result = fields(count=int)
        assert len(result) == 1
        assert result[0].key == "count"


class TestMessageSerializer:
    def _make_serializer(self, extra_fields=None, allow_additional=False):
        """Helper to create a serializer with message_type field."""
        flds = list(extra_fields or [])
        flds.append(Field.forValue("mt", "test", ""))
        return _MessageSerializer(flds, allow_additional_fields=allow_additional)

    def test_serialize(self, captured_messages):
        f = Field("x", lambda v: v * 2, "")
        s = self._make_serializer([f])
        msg = {"x": 5, "mt": "test"}
        s.serialize(msg)
        assert msg["x"] == 10

    def test_validate_missing_field(self, captured_messages):
        f = Field.forTypes("x", [int], "")
        s = self._make_serializer([f])
        with pytest.raises(ValidationError, match="missing"):
            s.validate({"mt": "test"})

    def test_validate_unexpected_field(self, captured_messages):
        s = self._make_serializer()
        with pytest.raises(ValidationError, match="Unexpected"):
            s.validate({"mt": "test", "extra": 1})

    def test_allow_additional_fields(self, captured_messages):
        s = self._make_serializer(allow_additional=True)
        s.validate({"mt": "test", "extra": 1})  # Should not raise

    def test_duplicate_field_names(self):
        f1 = Field("x", lambda x: x, "")
        f2 = Field("x", lambda x: x, "")
        mt = Field.forValue("mt", "test", "")
        with pytest.raises(ValueError, match="Duplicate"):
            _MessageSerializer([f1, f2, mt])

    def test_reserved_field_names(self):
        for reserved in RESERVED_FIELDS:
            f = Field(reserved, lambda x: x, "")
            mt = Field.forValue("mt", "test", "")
            with pytest.raises(ValueError, match="reserved"):
                _MessageSerializer([f, mt])

    def test_underscore_field_names(self):
        mt = Field.forValue("mt", "test", "")
        f = Field("_private", lambda x: x, "")
        with pytest.raises(ValueError, match="must not start with"):
            _MessageSerializer([f, mt])

    def test_non_field_instance_rejected(self):
        """Passing a non-Field object raises TypeError."""
        with pytest.raises(TypeError, match="Expected a Field"):
            _MessageSerializer(["not a field"])


class TestMessageType:
    def test_log(self, captured_messages):
        mt = MessageType("test:type", [Field.forTypes("x", [int], "")])
        mt.log(x=42)
        assert len(captured_messages) >= 1

    def test_call_deprecated(self, captured_messages):
        mt = MessageType("test:type", [Field.forTypes("x", [int], "")])
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            msg = mt(x=42)
            assert len(w) == 1
            assert "deprecated" in str(w[0].message).lower()

    def test_message_type_attribute(self):
        mt = MessageType("test:my_type", [])
        assert mt.message_type == "test:my_type"

    def test_description(self):
        mt = MessageType("test:desc", [], description="A test message")
        assert mt.description == "A test message"


class TestActionType:
    def test_call_creates_action(self, captured_messages):
        at = ActionType("test:action", [Field.forTypes("x", [int], "")], [])
        with at(x=42):
            pass
        # Should have start + end messages
        assert len(captured_messages) >= 2

    def test_as_task(self, captured_messages):
        at = ActionType("test:task", [], [])
        with at.as_task():
            pass
        assert len(captured_messages) >= 2

    def test_pep8_alias(self):
        """asTask is the backwards-compatible alias for as_task."""
        at = ActionType("test:task", [], [])
        # Both should be callable and produce the same behavior
        assert callable(at.asTask)
        assert callable(at.as_task)

    def test_action_type_attribute(self):
        at = ActionType("test:myaction", [], [])
        assert at.action_type == "test:myaction"

    def test_description(self):
        at = ActionType("test:desc", [], [], description="A test action")
        assert at.description == "A test action"
