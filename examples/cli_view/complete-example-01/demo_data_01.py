#!/usr/bin/env python3
"""Demo data preparation for example_09_comprehensive.py.

This module provides pre-built data objects, sample values, and utilities
for the comprehensive logxpy demonstration. Separating data prep from
logging calls makes the demo code cleaner and more focused on logxpy API usage.
"""
from __future__ import annotations

import asyncio
import tempfile
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from pathlib import Path
from typing import Any


# ============================================================================
# Enums for demo_data_types()
# ============================================================================

class Color(Enum):  # noqa: D101
    RED = auto()
    GREEN = auto()
    BLUE = auto()


class Status(Enum):  # noqa: D101
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"


# ============================================================================
# Sample Objects for demo_component_object()
# ============================================================================

class DemoObject:  # noqa: D101
    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value
        self._private = "hidden"

    def __repr__(self) -> str:
        return f"DemoObject(name='{self.name}', value={self.value})"


@dataclass
class UserProfile:  # noqa: D101
    username: str
    email: str
    score: float
    active: bool = True


# ============================================================================
# Pre-built Data Values
# ============================================================================

# For demo_data_types()
SAMPLE_TAGS = {'python', 'logging', 'structured'}
SAMPLE_IDS = frozenset([1, 2, 3, 4, 5])
SAMPLE_COLOR_RGB = (0, 128, 255)
SAMPLE_COLOR_HEX = '#FF5733'
SAMPLE_CURRENCY_AMOUNT = Decimal('19.99')
SAMPLE_CURRENCY_STRING = '100.00'
SAMPLE_DATETIME = datetime.now()
SAMPLE_POINTER_OBJ = {'key': 'value', 'nested': {'data': 123}}
SAMPLE_VARIANT_LIST = [1, 2, 3, 'mixed', True]
SAMPLE_VARIANT_DICT = {'nested': 'dict', 'count': 42}

# For demo_conditional_formatted()
DEBUG_MODE = True
SAMPLE_COUNT = 42
SAMPLE_USER = "Bob"
SAMPLE_SCORE = 95.5

# For demo_component_object()
SAMPLE_ITEMS = {'a': 1, 'b': 2, 'c': 3}

# For demo_system_memory()
SAMPLE_BINARY_BUFFER = b"Hello, World! This is binary data."


# ============================================================================
# XML Builder for demo_xml_data()
# ============================================================================

def build_sample_xml() -> str:
    """Build a sample XML configuration string."""
    import xml.etree.ElementTree as ET
    root = ET.Element('config')
    database = ET.SubElement(root, 'database')
    ET.SubElement(database, 'host').text = 'localhost'
    ET.SubElement(database, 'port').text = '5432'
    ET.SubElement(database, 'name').text = 'app_db'
    ET.SubElement(database, 'user').text = 'admin'
    return ET.tostring(root, encoding='unicode')


def parse_xml_summary(xml_string: str) -> dict[str, Any]:
    """Parse XML and return summary info."""
    import xml.etree.ElementTree as ET
    parsed = ET.fromstring(xml_string)
    return {'tag': parsed.tag, 'children': len(parsed)}


# ============================================================================
# File Helpers for demo_file_stream()
# ============================================================================

class TempFiles:
    """Context manager for creating and cleaning up temporary files."""

    def __init__(self):
        self.text_path: str = ""
        self.binary_path: str = ""
        self._text_file: Any = None
        self._binary_file: Any = None

    def __enter__(self) -> TempFiles:
        self._text_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        self._text_file.write("Line 1: Hello\nLine 2: World\nLine 3: Test\n")
        self._text_file.close()
        self.text_path = self._text_file.name

        self._binary_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False)
        self._binary_file.write(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f")
        self._binary_file.close()
        self.binary_path = self._binary_file.name

        return self

    def __exit__(self, *args: object) -> None:
        Path(self.text_path).unlink(missing_ok=True)
        Path(self.binary_path).unlink(missing_ok=True)


# ============================================================================
# Stream Helpers for demo_file_stream()
# ============================================================================

import io


def create_binary_stream() -> io.BytesIO:
    """Create a binary stream with sample data."""
    return io.BytesIO(b"Stream binary data \xde\xad\xbe\xef")


def create_text_stream() -> io.StringIO:
    """Create a text stream with sample lines."""
    return io.StringIO("Line A\nLine B\nLine C\nLine D\nLine E")


# ============================================================================
# Async/Decorated Functions for demo_logxpy_specific()
# ============================================================================

async def sample_async_operation() -> str:
    """Sample async operation for aaction demo."""
    await asyncio.sleep(0.01)
    return "async result"


class RetrySimulator:
    """Simulates a flaky operation that fails then succeeds."""

    def __init__(self, fail_count: int = 2):
        self.attempt_count = 0
        self.fail_count = fail_count

    def __call__(self) -> str:
        self.attempt_count += 1
        if self.attempt_count < self.fail_count:
            raise ConnectionError(f"Simulated failure #{self.attempt_count}")
        return "success"


def create_retry_simulator(fail_count: int = 2) -> RetrySimulator:
    """Create a retry simulator instance."""
    return RetrySimulator(fail_count)


# ============================================================================
# Pre-built Object Instances
# ============================================================================

# Demo object instance
DEMO_OBJECT = DemoObject("test_object", 42)

# User profile instance
USER_PROFILE = UserProfile("alice", "alice@example.com", 87.5)

# XML data
SAMPLE_XML_STRING = build_sample_xml()
SAMPLE_XML_SUMMARY = parse_xml_summary(SAMPLE_XML_STRING)
