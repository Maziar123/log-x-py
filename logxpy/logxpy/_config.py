"""Configuration loading."""
from __future__ import annotations
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ._types import Level

@dataclass
class Config:
    level: Level = Level.INFO
    format: str = "rich"
    destinations: list[str] = field(default_factory=lambda: ["console"])
    mask_fields: list[str] = field(default_factory=lambda: ["password", "token", "secret"])
    mask_patterns: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    file_path: str | None = None
    
    @classmethod
    def load(cls) -> 'Config':
        cfg = cls()
        # 1. pyproject.toml
        pyproject = Path.cwd() / 'pyproject.toml'
        if pyproject.exists():
            data = tomllib.loads(pyproject.read_text()).get('tool', {}).get('loggerx', {})
            if 'level' in data: cfg.level = Level[data['level'].upper()]
            if 'format' in data: cfg.format = data['format']
            if 'destinations' in data: cfg.destinations = data['destinations']
            if m := data.get('mask'):
                cfg.mask_fields = m.get('fields', cfg.mask_fields)
                cfg.mask_patterns = m.get('patterns', cfg.mask_patterns)
        # 2. Environment (overrides)
        if v := os.environ.get('LOGGERX_LEVEL'): cfg.level = Level[v.upper()]
        if v := os.environ.get('LOGGERX_FORMAT'): cfg.format = v
        if v := os.environ.get('LOGGERX_DESTINATIONS'): cfg.destinations = v.split(',')
        return cfg

_cfg: Config | None = None

def get_config() -> Config:
    global _cfg
    if _cfg is None: _cfg = Config.load()
    return _cfg
