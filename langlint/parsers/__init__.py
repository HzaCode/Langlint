"""
Parser modules for different file types.

This package contains parsers for various file formats that can extract
translatable text units while preserving the original structure.
"""

from .base import Parser, TranslatableUnit, ParseResult
from .python_parser import PythonParser
# from .markdown_parser import MarkdownParser  # Not exported - focus on code comments only
from .notebook_parser import NotebookParser
from .generic_code_parser import GenericCodeParser
from .config_parser import ConfigParser

__all__ = [
    "Parser",
    "TranslatableUnit",
    "ParseResult",
    "PythonParser",
    # "MarkdownParser",  # Not exported - focus on code comments only
    "NotebookParser",
    "GenericCodeParser",
    "ConfigParser",
]
