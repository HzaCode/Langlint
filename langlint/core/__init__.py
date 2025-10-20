"""
Core functionality for LangLint.

This package contains the core components including the dispatcher,
configuration management, and caching system.
"""

from .dispatcher import Dispatcher
from .config import Config, ConfigError
from .cache import Cache, CacheError

__all__ = [
    "Dispatcher",
    "Config",
    "ConfigError",
    "Cache",
    "CacheError",
]
