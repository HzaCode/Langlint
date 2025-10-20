"""
LangLint: A scalable, domain-agnostic platform for automated translation
and standardization of structured text in scientific collaboration.

This package provides a pluggable parser architecture for detecting,
translating, and standardizing text in various file types including
source code, documentation, configuration files, and Jupyter Notebooks.
"""

__version__ = "1.0.0"
__author__ = "LangLint Team"
__email__ = "langlint@example.com"
__license__ = "MIT"

from .core.dispatcher import Dispatcher
from .parsers.base import Parser, TranslatableUnit
from .translators.base import Translator
from .cli import main

__all__ = [
    "Dispatcher",
    "Parser",
    "TranslatableUnit",
    "Translator",
    "main",
    "version",
    "scan",
    "translate",
]


def version() -> str:
    """Get the version of LangLint."""
    return __version__


def scan(path: str, **kwargs) -> dict:
    """Scan files for translatable content."""
    try:
        # Try to use Rust module if available
        import langlint_py
        return langlint_py.scan(path, **kwargs)
    except ImportError:
        # Fallback to Python implementation
        import warnings
        warnings.warn("Failed to import Rust module, using Python fallback", UserWarning)
        raise RuntimeError("Rust module not built")


def translate(path: str, source_lang: str, target_lang: str, **kwargs) -> dict:
    """Translate files."""
    try:
        # Try to use Rust module if available
        import langlint_py
        return langlint_py.translate(path, source_lang, target_lang, **kwargs)
    except ImportError:
        # Fallback to Python implementation
        import warnings
        warnings.warn("Failed to import Rust module, using Python fallback", UserWarning)
        raise RuntimeError("Rust module not built")
