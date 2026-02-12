"""Pytest configuration."""

import os
import tempfile

import pytest

from writer.base import Q


@pytest.fixture
def temp_file():
    """Provide temporary file path."""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def queue():
    """Provide fresh Q instance."""
    return Q()
