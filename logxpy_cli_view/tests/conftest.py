"""Pytest configuration and fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_task():
    """Return a sample Eliot task."""
    return {
        "task_uuid": "cdeb220d-7605-4d5f-8341-1a170222e308",
        "error": False,
        "timestamp": 1425356700,
        "message": "Main loop terminated.",
        "task_level": [1],
    }


@pytest.fixture
def sample_action_task():
    """Return a sample Eliot action task."""
    return {
        "timestamp": 1425356800,
        "action_status": "started",
        "task_uuid": "f3a32bb3-ea6b-457c-aa99-08a3d0491ab4",
        "action_type": "app:action",
        "task_level": [1],
    }
