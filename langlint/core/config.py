"""
Configuration management for LangLint.

This module provides configuration loading, validation, and management
for the LangLint platform.
"""

import os
import toml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class TranslatorType(Enum):
    """Supported translator types."""
    OPENAI = "openai"
    DEEPL = "deepl"
    GOOGLE = "google"
    AZURE = "azure"
    MOCK = "mock"  # For testing


@dataclass
class TranslatorConfig:
    """Configuration for a specific translator."""
    type: TranslatorType
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None  # For OpenAI translator
    max_retries: int = 3
    timeout: int = 30
    batch_size: int = 10
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PathConfig:
    """Path-specific configuration overrides."""
    pattern: str
    translator: Optional[TranslatorType] = None
    target_lang: Optional[str] = None
    source_lang: Optional[List[str]] = None
    enabled: bool = True
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Config:
    """
    Main configuration class for LangLint.

    This class handles loading, validation, and access to configuration
    from various sources including pyproject.toml, environment variables,
    and command-line arguments.
    """

    # Global settings
    translator: TranslatorType = TranslatorType.GOOGLE
    target_lang: str = "EN-US"
    source_lang: List[str] = field(default_factory=lambda: ["zh", "ja", "ko"])

    # File processing
    exclude: List[str] = field(default_factory=lambda: [
        "**/data/", "**/secrets.yml", "**/node_modules/", "**/__pycache__/"
    ])
    include: List[str] = field(default_factory=list)

    # Translator configurations
    translators: Dict[TranslatorType, TranslatorConfig] = field(default_factory=dict)

    # Path-specific overrides
    path_configs: List[PathConfig] = field(default_factory=list)

    # Performance settings
    max_workers: int = 4
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour

    # Output settings
    verbose: bool = False
    dry_run: bool = False
    backup: bool = True

    def __post_init__(self) -> None:
        """Initialize default translator configurations."""
        if not self.translators:
            self.translators = {
                TranslatorType.OPENAI: TranslatorConfig(
                    type=TranslatorType.OPENAI,
                    model="gpt-3.5-turbo",
                    api_key=os.getenv("OPENAI_API_KEY"),
                ),
                TranslatorType.DEEPL: TranslatorConfig(
                    type=TranslatorType.DEEPL,
                    api_key=os.getenv("DEEPL_API_KEY"),
                ),
                TranslatorType.GOOGLE: TranslatorConfig(
                    type=TranslatorType.GOOGLE,
                    api_key=os.getenv("GOOGLE_API_KEY"),
                ),
                TranslatorType.AZURE: TranslatorConfig(
                    type=TranslatorType.AZURE,
                    api_key=os.getenv("AZURE_API_KEY"),
                    api_url=os.getenv("AZURE_ENDPOINT"),
                ),
                TranslatorType.MOCK: TranslatorConfig(
                    type=TranslatorType.MOCK,
                ),
            }

    @classmethod
    def load(cls, config_path: Optional[Union[str, Path]] = None) -> "Config":
        """
        Load configuration from file and environment.

        Args:
            config_path: Path to configuration file (defaults to pyproject.toml)

        Returns:
            Loaded configuration instance

        Raises:
            ConfigError: If configuration cannot be loaded or is invalid
        """
        if config_path is None:
            # Look for pyproject.toml in current directory and parent directories
            current_dir = Path.cwd()
            for path in [current_dir] + list(current_dir.parents):
                config_file = path / "pyproject.toml"
                if config_file.exists():
                    config_path = config_file
                    break
            else:
                # No config file found, return default config
                return cls()

        config_path = Path(config_path)
        if not config_path.exists():
            raise ConfigError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
        except Exception as e:
            raise ConfigError(f"Failed to load configuration file: {e}") from e

        # Extract langlint configuration
        langlint_config = data.get('tool', {}).get('langlint', {})
        if not langlint_config:
            return cls()

        # Parse configuration
        config = cls()

        # Global settings
        if 'translator' in langlint_config:
            try:
                config.translator = TranslatorType(langlint_config['translator'])
            except ValueError as e:
                raise ConfigError(f"Invalid translator type: {e}") from e

        if 'target_lang' in langlint_config:
            config.target_lang = langlint_config['target_lang']

        if 'source_lang' in langlint_config:
            config.source_lang = langlint_config['source_lang']

        if 'exclude' in langlint_config:
            config.exclude = langlint_config['exclude']

        if 'include' in langlint_config:
            config.include = langlint_config['include']

        # 路径特定配置
        for key, value in langlint_config.items():
            if isinstance(value, dict) and key.startswith("**"):
                pattern = key
                path_config = PathConfig(pattern=pattern)

                if 'translator' in value:
                    try:
                        path_config.translator = TranslatorType(value['translator'])
                    except ValueError as e:
                        raise ConfigError(f"Invalid translator type for {pattern}: {e}") from e

                if 'target_lang' in value:
                    path_config.target_lang = value['target_lang']

                if 'source_lang' in value:
                    path_config.source_lang = value['source_lang']

                if 'enabled' in value:
                    path_config.enabled = value['enabled']

                if 'additional_params' in value:
                    path_config.additional_params = value['additional_params']

                config.path_configs.append(path_config)

        # Load from environment variables
        config._load_from_env()

        return config

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Override with environment variables
        if os.getenv("LANGINT_TRANSLATOR"):
            try:
                self.translator = TranslatorType(os.getenv("LANGINT_TRANSLATOR"))
            except ValueError:
                pass  # Keep default if invalid

        if os.getenv("LANGINT_TARGET_LANG"):
            self.target_lang = os.getenv("LANGINT_TARGET_LANG")

        if os.getenv("LANGINT_SOURCE_LANG"):
            self.source_lang = os.getenv("LANGINT_SOURCE_LANG").split(",")

        if os.getenv("LANGINT_EXCLUDE"):
            self.exclude = os.getenv("LANGINT_EXCLUDE").split(",")

        if os.getenv("LANGINT_MAX_WORKERS"):
            try:
                self.max_workers = int(os.getenv("LANGINT_MAX_WORKERS"))
            except ValueError:
                pass  # Keep default if invalid

        if os.getenv("LANGINT_VERBOSE"):
            self.verbose = os.getenv("LANGINT_VERBOSE").lower() in ("true", "1", "yes")

        if os.getenv("LANGINT_DRY_RUN"):
            self.dry_run = os.getenv("LANGINT_DRY_RUN").lower() in ("true", "1", "yes")

    def get_path_config(self, file_path: str) -> Optional[PathConfig]:
        """
        Get path-specific configuration for a file.

        Args:
            file_path: Path to the file

        Returns:
            PathConfig if found, None otherwise
        """
        for path_config in self.path_configs:
            if path_config.enabled and self._match_pattern(file_path, path_config.pattern):
                return path_config
        return None

    def _match_pattern(self, file_path: str, pattern: str) -> bool:
        """
        Check if a file path matches a pattern.

        Args:
            file_path: Path to check
            pattern: Pattern to match against

        Returns:
            True if the path matches the pattern
        """
        from fnmatch import fnmatch
        return fnmatch(file_path, pattern)

    def get_translator_config(self, translator_type: TranslatorType) -> TranslatorConfig:
        """
        Get configuration for a specific translator.

        Args:
            translator_type: Type of translator

        Returns:
            TranslatorConfig for the translator
        """
        return self.translators.get(translator_type, TranslatorConfig(type=translator_type))

    def validate(self) -> None:
        """
        Validate the configuration.

        Raises:
            ConfigError: If configuration is invalid
        """
        # Validate translator configuration
        translator_config = self.get_translator_config(self.translator)
        if translator_config.api_key is None and self.translator != TranslatorType.MOCK:
            raise ConfigError(f"API key not configured for translator: {self.translator}")

        # Validate language codes
        if not self.target_lang:
            raise ConfigError("target_lang cannot be empty")

        if not self.source_lang:
            raise ConfigError("source_lang cannot be empty")

        # Validate path configurations
        for path_config in self.path_configs:
            if not path_config.pattern:
                raise ConfigError("Path pattern cannot be empty")

            if path_config.translator and path_config.translator not in self.translators:
                raise ConfigError(f"Translator not configured: {path_config.translator}")


class ConfigError(Exception):
    """Exception raised for configuration errors."""
    pass
