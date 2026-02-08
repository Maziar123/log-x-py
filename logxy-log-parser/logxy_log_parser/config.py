"""
Configuration management for logxy-log-parser.

Provides configuration file support for parser settings.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ParserConfig:
    """Configuration for log parser."""

    # Field mappings (for non-standard log formats)
    field_mappings: dict[str, str] = field(default_factory=dict)

    # Default values for missing fields
    defaults: dict[str, Any] = field(default_factory=dict)

    # Filters to apply automatically
    auto_filters: dict[str, Any] = field(default_factory=dict)

    # Export settings
    export_format: str = "json"
    export_options: dict[str, Any] = field(default_factory=dict)

    # Display settings
    show_timestamps: bool = True
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    show_level: bool = True
    show_task_uuid: bool = False
    show_fields: bool = False

    # Analysis settings
    slow_threshold: float = 1.0  # seconds
    error_levels: list[str] = field(default_factory=lambda: ["error", "critical"])

    # Performance settings
    use_indexing: bool = True
    index_cache_dir: str | None = None
    lazy_load_threshold: int = 10000  # entries

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary.

        Returns:
            dict[str, Any]: Config dictionary.
        """
        return {
            "field_mappings": self.field_mappings,
            "defaults": self.defaults,
            "auto_filters": self.auto_filters,
            "export_format": self.export_format,
            "export_options": self.export_options,
            "show_timestamps": self.show_timestamps,
            "timestamp_format": self.timestamp_format,
            "show_level": self.show_level,
            "show_task_uuid": self.show_task_uuid,
            "show_fields": self.show_fields,
            "slow_threshold": self.slow_threshold,
            "error_levels": self.error_levels,
            "use_indexing": self.use_indexing,
            "index_cache_dir": self.index_cache_dir,
            "lazy_load_threshold": self.lazy_load_threshold,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ParserConfig:
        """Create config from dictionary.

        Args:
            data: Configuration dictionary.

        Returns:
            ParserConfig: Configuration instance.
        """
        return cls(
            field_mappings=data.get("field_mappings", {}),
            defaults=data.get("defaults", {}),
            auto_filters=data.get("auto_filters", {}),
            export_format=data.get("export_format", "json"),
            export_options=data.get("export_options", {}),
            show_timestamps=data.get("show_timestamps", True),
            timestamp_format=data.get("timestamp_format", "%Y-%m-%d %H:%M:%S"),
            show_level=data.get("show_level", True),
            show_task_uuid=data.get("show_task_uuid", False),
            show_fields=data.get("show_fields", False),
            slow_threshold=data.get("slow_threshold", 1.0),
            error_levels=data.get("error_levels", ["error", "critical"]),
            use_indexing=data.get("use_indexing", True),
            index_cache_dir=data.get("index_cache_dir"),
            lazy_load_threshold=data.get("lazy_load_threshold", 10000),
        )

    def save(self, path: str | Path) -> None:
        """Save configuration to file.

        Args:
            path: Path to save configuration.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> ParserConfig:
        """Load configuration from file.

        Args:
            path: Path to configuration file.

        Returns:
            ParserConfig: Loaded configuration.

        Raises:
            FileNotFoundError: If config file doesn't exist.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)


class ConfigManager:
    """Manage configuration with file watching and profiles."""

    DEFAULT_CONFIG_PATHS = [
        Path(".logxyrc"),
        Path(".logxy.json"),
        Path("logxy.config.json"),
        Path("pyproject.toml"),
    ]

    def __init__(self, config_path: str | Path | None = None) -> None:
        """Initialize config manager.

        Args:
            config_path: Optional explicit config path.
        """
        self._config_path = Path(config_path) if config_path else None
        self._config: ParserConfig | None = None
        self._profiles: dict[str, ParserConfig] = {}

    @property
    def config(self) -> ParserConfig:
        """Get current configuration.

        Returns:
            ParserConfig: Current configuration.
        """
        if self._config is None:
            self._config = self._load_default()
        return self._config

    def _load_default(self) -> ParserConfig:
        """Load default configuration from standard locations.

        Returns:
            ParserConfig: Loaded configuration or default.
        """
        # Try explicit path first
        if self._config_path and self._config_path.exists():
            return ParserConfig.load(self._config_path)

        # Try standard locations
        for path in self.DEFAULT_CONFIG_PATHS:
            if path.exists():
                if path.suffix == ".toml":
                    return self._load_from_toml(path)
                else:
                    try:
                        return ParserConfig.load(path)
                    except (json.JSONDecodeError, FileNotFoundError):
                        continue

        # Return default config
        return ParserConfig()

    def _load_from_toml(self, path: Path) -> ParserConfig:
        """Load configuration from pyproject.toml.

        Args:
            path: Path to toml file.

        Returns:
            ParserConfig: Loaded configuration.
        """
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                return ParserConfig()

        with open(path, "rb") as f:
            data = tomllib.load(f)

        # Extract logxy config section
        logxy_config = data.get("tool", {}).get("logxy", {})
        return ParserConfig.from_dict(logxy_config)

    def load_profile(self, name: str, path: str | Path) -> ParserConfig:
        """Load a named configuration profile.

        Args:
            name: Profile name.
            path: Path to profile config file.

        Returns:
            ParserConfig: Loaded profile configuration.
        """
        config = ParserConfig.load(path)
        self._profiles[name] = config
        return config

    def use_profile(self, name: str) -> None:
        """Switch to a named profile.

        Args:
            name: Profile name to use.

        Raises:
            KeyError: If profile doesn't exist.
        """
        if name not in self._profiles:
            raise KeyError(f"Profile not found: {name}")
        self._config = self._profiles[name]

    def save_profile(self, name: str, path: str | Path | None = None) -> None:
        """Save current config as a named profile.

        Args:
            name: Profile name.
            path: Optional path to save to. Defaults to .logxy/profiles/<name>.json.
        """
        if path is None:
            path = Path(".logxy/profiles") / f"{name}.json"
        else:
            path = Path(path)

        self.config.save(path)
        self._profiles[name] = self.config

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Dot-separated key path (e.g., "export_format").
            default: Default value if key not found.

        Returns:
            Any: Configuration value.
        """
        config_dict = self.config.to_dict()
        keys = key.split(".")

        value = config_dict
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Dot-separated key path.
            value: Value to set.
        """
        keys = key.split(".")

        if self._config is None:
            self._config = ParserConfig()

        # For now, only support top-level keys
        if len(keys) == 1 and hasattr(self._config, keys[0]):
            setattr(self._config, keys[0], value)
        else:
            # For nested keys, update the appropriate dict
            if keys[0] == "export_options":
                self._config.export_options[keys[1]] = value
            elif keys[0] == "defaults":
                self._config.defaults[keys[1]] = value
            elif keys[0] == "field_mappings":
                self._config.field_mappings[keys[1]] = value
            elif keys[0] == "auto_filters":
                self._config.auto_filters[keys[1]] = value


# Global config instance
_global_config: ConfigManager | None = None


def get_config(config_path: str | Path | None = None) -> ConfigManager:
    """Get global configuration manager.

    Args:
        config_path: Optional explicit config path.

    Returns:
        ConfigManager: Configuration manager instance.
    """
    global _global_config

    if _global_config is None or config_path is not None:
        _global_config = ConfigManager(config_path)

    return _global_config
