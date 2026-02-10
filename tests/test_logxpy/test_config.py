"""Tests for logxpy/src/_config.py -- Configuration loading."""
from __future__ import annotations

import pytest

import logxpy.src._config as config_module
from logxpy.src._config import Config, get_config
from logxpy.src._types import Level


class TestConfig:
    def test_defaults(self):
        cfg = Config()
        assert cfg.level == Level.INFO
        assert cfg.format == "rich"
        assert "console" in cfg.destinations
        assert "password" in cfg.mask_fields

    def test_custom_level(self):
        cfg = Config(level=Level.DEBUG)
        assert cfg.level == Level.DEBUG

    def test_custom_format(self):
        cfg = Config(format="json")
        assert cfg.format == "json"

    def test_custom_destinations(self):
        cfg = Config(destinations=["file", "syslog"])
        assert cfg.destinations == ["file", "syslog"]

    def test_custom_mask_fields(self):
        cfg = Config(mask_fields=["api_key", "ssn"])
        assert "api_key" in cfg.mask_fields
        assert "ssn" in cfg.mask_fields

    def test_default_mask_patterns(self):
        cfg = Config()
        assert cfg.mask_patterns == []

    def test_default_context(self):
        cfg = Config()
        assert cfg.context == {}

    def test_default_file_path(self):
        cfg = Config()
        assert cfg.file_path is None

    def test_env_level_override(self, monkeypatch):
        monkeypatch.setenv("LOGGERX_LEVEL", "WARNING")
        cfg = Config.load()
        assert cfg.level == Level.WARNING

    def test_env_level_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("LOGGERX_LEVEL", "debug")
        cfg = Config.load()
        assert cfg.level == Level.DEBUG

    def test_env_format_override(self, monkeypatch):
        monkeypatch.setenv("LOGGERX_FORMAT", "json")
        cfg = Config.load()
        assert cfg.format == "json"

    def test_env_destinations_override(self, monkeypatch):
        monkeypatch.setenv("LOGGERX_DESTINATIONS", "file,console")
        cfg = Config.load()
        assert cfg.destinations == ["file", "console"]

    def test_env_destinations_single(self, monkeypatch):
        monkeypatch.setenv("LOGGERX_DESTINATIONS", "syslog")
        cfg = Config.load()
        assert cfg.destinations == ["syslog"]


class TestGetConfig:
    def test_returns_config(self):
        # Reset cached config
        original = config_module._cfg
        config_module._cfg = None
        try:
            cfg = get_config()
            assert isinstance(cfg, Config)
        finally:
            config_module._cfg = original

    def test_caches_config(self):
        original = config_module._cfg
        config_module._cfg = None
        try:
            cfg1 = get_config()
            cfg2 = get_config()
            assert cfg1 is cfg2
        finally:
            config_module._cfg = original
