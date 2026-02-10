"""Field masking."""
from __future__ import annotations
import re
from typing import Any

class Masker:
    def __init__(self, fields: list[str], patterns: list[str]):
        self._fields = {f.lower() for f in fields}
        self._patterns = [re.compile(p) for p in patterns]
    
    def mask(self, data: dict[str, Any]) -> dict[str, Any]:
        return {k: self._mask(k, v) for k, v in data.items()}
    
    def _mask(self, key: str, val: Any) -> Any:
        if key.lower() in self._fields: return "***"
        if isinstance(val, str):
            for p in self._patterns:
                val = p.sub("***", val)
        elif isinstance(val, dict):
            return self.mask(val)
        elif isinstance(val, list):
            return [self._mask(key, v) for v in val]
        return val
