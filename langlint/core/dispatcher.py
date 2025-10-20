"""
Parser dispatcher for routing files to appropriate parsers.

This module provides the core dispatcher that determines which parser
should handle a given file based on file extension, MIME type, and content.
"""

import os
import mimetypes
from pathlib import Path
from typing import List, Optional, Dict, Any, Type
from dataclasses import dataclass

from .config import Config
from .cache import Cache
from ..parsers.base import Parser, ParseResult, ParseError
from ..parsers.python_parser import PythonParser
# from ..parsers.markdown_parser import MarkdownParser  # Not registered - focus on code comments only
from ..parsers.notebook_parser import NotebookParser
from ..parsers.generic_code_parser import GenericCodeParser
from ..parsers.config_parser import ConfigParser


@dataclass
class DispatchResult:
    """
    Result of dispatching a file to a parser.

    Attributes:
        parser: The parser instance used
        parse_result: The result of parsing the file
        cache_hit: Whether the result was served from cache
    """
    parser: Parser
    parse_result: ParseResult
    cache_hit: bool = False


class Dispatcher:
    """
    Dispatcher for routing files to appropriate parsers.

    The dispatcher maintains a registry of available parsers and uses
    file extension, MIME type, and content analysis to determine which
    parser should handle a given file.
    """

    def __init__(self, config: Optional[Config] = None, cache: Optional[Cache] = None):
        """
        Initialize the dispatcher.

        Args:
            config: Configuration instance
            cache: Cache instance for storing parse results
        """
        self.config = config or Config()
        self.cache = cache or Cache()
        self._parsers: Dict[str, Parser] = {}
        self._register_default_parsers()

    def _register_default_parsers(self) -> None:
        """Register the default set of parsers."""
        parsers = [
            PythonParser(),
            # MarkdownParser() - Removed: focus on code comments only
            NotebookParser(),  # Still includes MarkdownParser internally for notebook markdown cells
            GenericCodeParser(),
            ConfigParser(),
        ]

        for parser in parsers:
            self.register_parser(parser)

    def register_parser(self, parser: Parser) -> None:
        """
        Register a new parser.

        Args:
            parser: Parser instance to register
        """
        for extension in parser.supported_extensions:
            self._parsers[extension.lower()] = parser

    def get_parser(self, file_path: str, content: Optional[str] = None) -> Optional[Parser]:
        """
        Get the appropriate parser for a file.

        Args:
            file_path: Path to the file
            content: Optional file content (if already loaded)

        Returns:
            Parser instance if found, None otherwise
        """
        file_path = str(file_path)

        # First, try to match by file extension
        extension = Path(file_path).suffix.lower()
        if extension in self._parsers:
            parser = self._parsers[extension]
            if parser.can_parse(file_path, content):
                return parser

        # If no extension match, try MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            for parser in self._parsers.values():
                if mime_type in parser.supported_mime_types and parser.can_parse(file_path, content):
                    return parser

        # If still no match, try content-based detection
        if content is not None:
            for parser in self._parsers.values():
                if parser.can_parse(file_path, content):
                    return parser

        return None

    def parse_file(self, file_path: str, content: Optional[str] = None) -> DispatchResult:
        """
        Parse a file and return the result.

        Args:
            file_path: Path to the file to parse
            content: Optional file content (if already loaded)

        Returns:
            DispatchResult containing the parser and parse result

        Raises:
            ParseError: If no suitable parser is found or parsing fails
            FileNotFoundError: If the file doesn't exist and content is not provided
        """
        file_path = str(file_path)

        # Load content if not provided
        if content is None:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ParseError(f"Could not decode file: {file_path}")

        # Check cache first
        cache_key = self._get_cache_key(file_path, content)
        if self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return DispatchResult(
                    parser=cached_result['parser'],
                    parse_result=cached_result['parse_result'],
                    cache_hit=True
                )

        # Find appropriate parser
        parser = self.get_parser(file_path, content)
        if parser is None:
            raise ParseError(f"No suitable parser found for file: {file_path}")

        # Parse the file
        try:
            parse_result = parser.extract_translatable_units(content, file_path)
        except Exception as e:
            raise ParseError(f"Failed to parse file {file_path}: {e}") from e

        # Cache the result
        if self.cache:
            self.cache.set(cache_key, {
                'parser': parser,
                'parse_result': parse_result
            })

        return DispatchResult(
            parser=parser,
            parse_result=parse_result,
            cache_hit=False
        )

    def _get_cache_key(self, file_path: str, content: str) -> str:
        """
        Generate a cache key for a file.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            Cache key string
        """
        import hashlib
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        return f"{file_path}:{content_hash}"

    def get_supported_extensions(self) -> List[str]:
        """
        Get all supported file extensions.

        Returns:
            List of supported file extensions
        """
        return list(self._parsers.keys())

    def get_parser_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all registered parsers.

        Returns:
            Dictionary mapping file extensions to parser information
        """
        info = {}
        for ext, parser in self._parsers.items():
            info[ext] = {
                'class_name': parser.__class__.__name__,
                'supported_extensions': parser.supported_extensions,
                'supported_mime_types': parser.supported_mime_types,
            }
        return info
